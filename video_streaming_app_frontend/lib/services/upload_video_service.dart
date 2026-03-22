import 'dart:convert';
import 'dart:io';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_dotenv/flutter_dotenv.dart';

class UploadVideoService {
  final FlutterSecureStorage secureStorage = FlutterSecureStorage();
  String backendUrl = "${dotenv.env['API_BASE_URL']}/upload/video";

  Future<Map<String, String>> _getCookieHeader() async {
    final accessToken = await secureStorage.read(key: 'access_token');

    final headers = {'Content-Type': 'application/json'};

    if (accessToken != null) {
      headers['Cookie'] = 'access_token=$accessToken';
    }

    return headers;
  }

  Future<Map<String, dynamic>> getPresignedUrlForThumbnail(
    String thumbnailId,
  ) async {
    print('UploadVideoService - getPresignedUrlForThumbnail: Requesting URL for $thumbnailId');
    final res = await http.get(
      Uri.parse("$backendUrl/url/thumbnail?thumbnail_id=$thumbnailId"),
      headers: await _getCookieHeader(),
    ).timeout(const Duration(seconds: 10));

    print('UploadVideoService - getPresignedUrlForThumbnail: Response status: ${res.statusCode}');
    if (res.statusCode == 200) {
      return jsonDecode(res.body) as Map<String, dynamic>;
    }

    print('UploadVideoService - getPresignedUrlForThumbnail: Error response: ${res.body}');
    throw jsonDecode(res.body)['detail'] ?? 'Unexpected error occurred';
  }

  Future<Map<String, dynamic>> getPresignedUrlForVideo() async {
    print('UploadVideoService - getPresignedUrlForVideo: Requesting URL');
    final res = await http.get(
      Uri.parse("$backendUrl/url"),
      headers: await _getCookieHeader(),
    ).timeout(const Duration(seconds: 10));

    print('UploadVideoService - getPresignedUrlForVideo: Response status: ${res.statusCode}');
    if (res.statusCode == 200) {
      return jsonDecode(res.body) as Map<String, dynamic>;
    }

    print('UploadVideoService - getPresignedUrlForVideo: Error response: ${res.body}');
    throw jsonDecode(res.body)['detail'] ?? 'Unexpected error occurred';
  }

  Future<bool> uploadFileToS3({
    required String presignedUrl,
    required File file,
    required bool isVideo,
  }) async {
    print('UploadVideoService - uploadFileToS3: Uploading ${isVideo ? 'video' : 'thumbnail'} to S3');
    final res = await http.put(
      Uri.parse(presignedUrl),
      headers: {
        'Content-Type': isVideo ? 'video/mp4' : 'image/jpg',
        if (!isVideo) 'x-amz-acl': 'public-read',
      },
      body: file.readAsBytesSync(),
    ); // S3 uploads might take longer, removing 10s timeout here.

    print('UploadVideoService - uploadFileToS3: Response status: ${res.statusCode}, body: ${res.body}');
    return res.statusCode == 200;
  }

  Future<bool> uploadMetadata({
    required String title,
    required String description,
    required String visibility,
    required String s3Key,
  }) async {
    print('UploadVideoService - uploadMetadata: Uploading metadata for video=$s3Key');
    final res = await http.post(
      Uri.parse("$backendUrl/metadata"),
      headers: await _getCookieHeader(),
      body: jsonEncode({
        'title': title,
        'description': description,
        'visibility': visibility,
        'video_id': s3Key,
        'video_s3_key': s3Key,
      }),
    ).timeout(const Duration(seconds: 10));

    print('UploadVideoService - uploadMetadata: Response status: ${res.statusCode}');
    return res.statusCode == 200;
  }
}
