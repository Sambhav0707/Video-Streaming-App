import 'dart:convert';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

class VideoService {
  final FlutterSecureStorage secureStorage = FlutterSecureStorage();
  String backendUrl = "http://192.168.29.36:8000/videos";

  Future<Map<String, String>> _getCookieHeader() async {
    final accessToken = await secureStorage.read(key: 'access_token');

    final headers = {'Content-Type': 'application/json'};

    if (accessToken != null) {
      headers['Cookie'] = 'access_token=$accessToken';
    }

    return headers;
  }

  Future<List<Map<String, dynamic>>> getVideos() async {
    print('VideoService - getVideos: Fetching videos from $backendUrl/all');
    try {
      final res = await http
          .get(Uri.parse("$backendUrl/all"), headers: await _getCookieHeader());
      print(res.body);
      print('VideoService - getVideos: Response status: ${res.statusCode}');
      if (res.statusCode != 200) {
        print('VideoService - getVideos: Error response: ${res.body}');
        throw jsonDecode(res.body)['detail'] ?? 'Error fetching videos!';
      }

      print('VideoService - getVideos: Successfully fetched videos');
      return List<Map<String, dynamic>>.from(jsonDecode(res.body));
    } catch (e) {
      print('VideoService - getVideos: Error -> $e');
      throw e.toString();
    }
  }
}
