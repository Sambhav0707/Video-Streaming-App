import 'package:flutter/widgets.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:video_streaming_app_frontend/services/auth_service.dart';

part 'auth_state.dart';

class AuthCubit extends Cubit<AuthState> {
  AuthCubit() : super(AuthInitial());
  final AuthService authService = AuthService();

  void signUpUser({
    required String name,
    required String email,
    required String password,
  }) async {
    print('AuthCubit - signUpUser: Start for email=$email');
    emit(AuthLoading());
    try {
      final res = await authService.signUpUser(
        name: name,
        password: password,
        email: email,
      );
      print('AuthCubit - signUpUser: Success -> $res');
      emit(AuthSignupSuccess(res));
    } catch (e) {
      print('AuthCubit - signUpUser: Error -> $e');
      emit(AuthError(e.toString()));
    }
  }

  void confirmSignUpUser({required String email, required String otp}) async {
    print('AuthCubit - confirmSignUpUser: Start for email=$email, otp=$otp');
    emit(AuthLoading());
    try {
      final res = await authService.confirmSignUpUser(email: email, otp: otp);
      print('AuthCubit - confirmSignUpUser: Success -> $res');
      emit(AuthConfirmSignupSuccess(res));
    } catch (e) {
      print('AuthCubit - confirmSignUpUser: Error -> $e');
      emit(AuthError(e.toString()));
    }
  }

  void loginUser({required String email, required String password}) async {
    print('AuthCubit - loginUser: Start for email=$email');
    emit(AuthLoading());
    try {
      final res = await authService.loginUser(password: password, email: email);
      print('AuthCubit - loginUser: Success -> $res');
      emit(AuthLoginSuccess(res));
    } catch (e) {
      print('AuthCubit - loginUser: Error -> $e');
      emit(AuthError(e.toString()));
    }
  }

  void isAuthenticated() async {
    print('AuthCubit - isAuthenticated: Start');
    emit(AuthLoading());
    try {
      final res = await authService.isAuthenticated();
      print('AuthCubit - isAuthenticated: Result -> $res');
      if (res) {
        emit(AuthLoginSuccess('Logged in!'));
      } else {
        emit(AuthInitial());
      }
    } catch (e) {
      print('AuthCubit - isAuthenticated: Error -> $e');
      emit(AuthError(e.toString()));
    }
  }

  void logoutUser() async {
    print('AuthCubit - logoutUser: Start');
    try {
      await authService.logout();
      emit(AuthInitial());
    } catch (e) {
      print('AuthCubit - logoutUser: Error -> $e');
      emit(AuthError(e.toString()));
    }
  }
}
