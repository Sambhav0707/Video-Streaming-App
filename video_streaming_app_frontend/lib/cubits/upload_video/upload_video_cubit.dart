import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:path/path.dart';
import 'package:path_provider/path_provider.dart';
import 'package:video_streaming_app_frontend/services/upload_video_service.dart';

part 'upload_video_state.dart';

class UploadVideoCubit extends Cubit<UploadVideoState> {
  UploadVideoCubit() : super(UploadVideoInitial());
  final uploadVideoService = UploadVideoService();

  Future<void> uploadVideo({
    required File videoFile,
    required File thumbnailFile,
    required String title,
    required String description,
    required String visibility,
  }) async {
    print('UploadVideoCubit - uploadVideo: Start (title: $title)');
    emit(UploadVideoLoading());
    try {
      print('UploadVideoCubit - uploadVideo: Requesting presigned URLs');
      final videoData = await uploadVideoService.getPresignedUrlForVideo();
      final thumbnailData = await uploadVideoService
          .getPresignedUrlForThumbnail(videoData['video_id']);
      print('UploadVideoCubit - uploadVideo: URLs received -> Video ID: ${videoData['video_id']}');

      final appDir = await getApplicationDocumentsDirectory();
      if (!appDir.existsSync()) {
        appDir.createSync(recursive: true);
      }

      final newThumbnailPath =
          "${appDir.path}/${thumbnailData['thumbnail_id']}";
      final newVideoPath = "${appDir.path}/${videoData['video_id']}";

      final thumbnailDir = Directory(dirname(newThumbnailPath));
      final videoDir = Directory(dirname(newVideoPath));

      if (!thumbnailDir.existsSync()) {
        thumbnailDir.createSync(recursive: true);
      }

      if (!videoDir.existsSync()) {
        videoDir.createSync(recursive: true);
      }

      File newThumbnailFile = await thumbnailFile.copy(newThumbnailPath);
      File newVideoFile = await videoFile.copy(newVideoPath);

      print('UploadVideoCubit - uploadVideo: Temp files created, uploading thumbnail...');
      final isThumbnailUploaded = await uploadVideoService.uploadFileToS3(
        presignedUrl: thumbnailData['url'],
        file: newThumbnailFile,
        isVideo: false,
      );

      print('UploadVideoCubit - uploadVideo: Thumbnail uploaded: $isThumbnailUploaded, uploading video...');
      final isVideoUploaded = await uploadVideoService.uploadFileToS3(
        presignedUrl: videoData['url'],
        file: newVideoFile,
        isVideo: true,
      );

      if (isThumbnailUploaded && isVideoUploaded) {
        print('UploadVideoCubit - uploadVideo: Files uploaded successfully to S3, uploading metadata...');
        final isMetadataUploaded = await uploadVideoService.uploadMetadata(
          title: title,
          description: description,
          visibility: visibility,
          s3Key: videoData['video_id'],
        );

        if (isMetadataUploaded) {
          print('UploadVideoCubit - uploadVideo: Metadata uploaded, Success!');
          emit(UploadVideoSuccess());
        } else {
          print('UploadVideoCubit - uploadVideo: Metadata upload failed');
          emit(UploadVideoError('Metadata not uploaded to backend!'));
        }
      } else {
        print('UploadVideoCubit - uploadVideo: S3 upload failed (Thumb=$isThumbnailUploaded, Vid=$isVideoUploaded)');
        emit(UploadVideoError('Files not uploaded to S3!'));
      }

      try {
        if (newThumbnailFile.existsSync()) {
          await newThumbnailFile.delete();
        }
        if (newVideoFile.existsSync()) {
          await newVideoFile.delete();
        }
      } catch (e) {
        print('Error cleaning up temp files: $e');
      }
    } catch (e) {
      print('Upload error: $e');
      emit(UploadVideoError(e.toString()));
    }
  }
}
