import 'dart:convert';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

class AuthService {
  final backendUrl = "http://192.168.29.36:8000/auth";
  final FlutterSecureStorage secureStorage = FlutterSecureStorage();

  Future<Map<String, String>> _getCookieHeader() async {
    final accessToken = await secureStorage.read(key: 'access_token');
    final refreshToken = await secureStorage.read(key: 'refresh_token');
    final userCognitoSub = await secureStorage.read(key: 'user_cognito_sub');

    final headers = {'Content-Type': 'application/json'};

    if (accessToken != null) {
      headers['Cookie'] = 'access_token=$accessToken';

      if (refreshToken != null) {
        headers['Cookie'] = '${headers['Cookie']};refresh_token=$refreshToken';
        if (userCognitoSub != null) {
          headers['Cookie'] =
              '${headers['Cookie']};user_cognito_sub=$userCognitoSub';
        }
      }
    }

    return headers;
  }

  Future<void> _storeCookies(http.Response response) async {
    String? cookies = response.headers['set-cookie'];

    if (cookies != null) {
      final accessTokenMatch = RegExp(
        r'access_token=([^;]+)',
      ).firstMatch(cookies);

      if (accessTokenMatch != null) {
        await secureStorage.write(
          key: 'access_token',
          value: accessTokenMatch.group(1),
        );
      }

      final refreshTokenMatch = RegExp(
        r'refresh_token=([^;]+)',
      ).firstMatch(cookies);

      if (refreshTokenMatch != null) {
        await secureStorage.write(
          key: 'refresh_token',
          value: refreshTokenMatch.group(1),
        );
      }
    }
  }

  Future<String> signUpUser({
    required String name,
    required String password,
    required String email,
  }) async {
    print(
      'AuthService - signUpUser: Making POST request to $backendUrl/signup',
    );
    final res = await http
        .post(
          Uri.parse("$backendUrl/signup"),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({
            "name": name,
            "email": email,
            "password": password,
          }),
        )
        .timeout(const Duration(seconds: 30));

    print('AuthService - signUpUser: Response status: ${res.statusCode}');
    if (res.statusCode != 200) {
      print('AuthService - signUpUser: Error response: ${res.body}');
      throw jsonDecode(res.body)['detail'] ?? 'An error occurred!';
    }

    return jsonDecode(res.body)['message'] ??
        'Signup successful, please verify your email';
  }

  Future<String> confirmSignUpUser({
    required String email,
    required String otp,
  }) async {
    print(
      'AuthService - confirmSignUpUser: Making POST request to $backendUrl/confirm-user',
    );
    final res = await http
        .post(
          Uri.parse("$backendUrl/confirm-user"),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({"email": email, "otp": otp}),
        )
        .timeout(const Duration(seconds: 30));

    print(
      'AuthService - confirmSignUpUser: Response status: ${res.statusCode}',
    );
    if (res.statusCode != 200) {
      print('AuthService - confirmSignUpUser: Error response: ${res.body}');
      throw jsonDecode(res.body)['detail'] ?? 'An error occurred!';
    }

    return jsonDecode(res.body)['message'] ?? 'OTP Confirmed, LOGIN!';
  }

  Future<String> loginUser({
    required String password,
    required String email,
  }) async {
    print('AuthService - loginUser: Making POST request to $backendUrl/login');
    final res = await http
        .post(
          Uri.parse("$backendUrl/login"),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({"email": email, "password": password}),
        )
        .timeout(const Duration(seconds: 30));

    print('AuthService - loginUser: Response status: ${res.statusCode}');
    if (res.statusCode != 200) {
      print('AuthService - loginUser: Error response: ${res.body}');
      throw jsonDecode(res.body)['detail'] ?? 'An error occurred!';
    }
    print('AuthService - loginUser: Storing cookies and verifying auth');
    await _storeCookies(res);
    isAuthenticated();

    return jsonDecode(res.body)['message'] ?? 'Login successful';
  }

  Future<String> refreshToken() async {
    print(
      'AuthService - refreshToken: Making POST request to $backendUrl/refresh',
    );
    final cookieHeaders = await _getCookieHeader();

    final res = await http
        .post(Uri.parse("$backendUrl/refresh-token"), headers: cookieHeaders)
        .timeout(const Duration(seconds: 30));

    print('AuthService - refreshToken: Response status: ${res.statusCode}');
    if (res.statusCode != 200) {
      print('AuthService - refreshToken: Error response: ${res.body}');
      throw jsonDecode(res.body)['detail'] ?? 'An error occurred!';
    }
    await _storeCookies(res);

    return jsonDecode(res.body)['message'] ?? 'Token refresh successful';
  }

  Future<bool> isAuthenticated({int count = 0}) async {
    print('AuthService - isAuthenticated: Start (count: $count)');
    if (count > 1) {
      print(
        'AuthService - isAuthenticated: Max retry reached, returning false',
      );
      return false;
    }
    final cookieHeaders = await _getCookieHeader();

    try {
      print(
        'AuthService - isAuthenticated: Making GET request to $backendUrl/me',
      );
      final res = await http
          .get(Uri.parse("$backendUrl/me"), headers: cookieHeaders)
          .timeout(const Duration(seconds: 30));

      print(
        'AuthService - isAuthenticated: Response status: ${res.statusCode}',
      );
      if (res.statusCode != 200) {
        print(
          'AuthService - isAuthenticated: Unauthorized, attempting refresh',
        );
        await refreshToken();
        return await isAuthenticated(count: count + 1);
      } else {
        await secureStorage.write(
          key: 'user_cognito_sub',
          value: jsonDecode(res.body)['user']['sub'],
        );
      }
      return res.statusCode == 200;
    } catch (e) {
      print('AuthService - isAuthenticated: Error -> $e');
      rethrow;
    }
  }

  Future<void> logout() async {
    print('AuthService - logout: Clearing secure storage');
    await secureStorage.deleteAll();
  }
}
