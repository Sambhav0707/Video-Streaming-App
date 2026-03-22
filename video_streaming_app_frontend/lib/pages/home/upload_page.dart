import 'dart:io';

import 'package:dotted_border/dotted_border.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:video_streaming_app_frontend/cubits/upload_video/upload_video_cubit.dart';
import 'package:video_streaming_app_frontend/utils/utils.dart';

class UploadPage extends StatefulWidget {
  static route() => MaterialPageRoute(builder: (context) => UploadPage());
  const UploadPage({super.key});

  @override
  State<UploadPage> createState() => _UploadPageState();
}

class _UploadPageState extends State<UploadPage> {
  final descriptionController = TextEditingController();
  final titleController = TextEditingController();
  String visibility = 'PRIVATE';
  File? imageFile;
  File? videoFile;

  @override
  void dispose() {
    descriptionController.dispose();
    titleController.dispose();
    super.dispose();
  }

  void selectImage() async {
    final _imageFile = await pickImage();

    setState(() {
      imageFile = _imageFile;
    });
  }

  void selectVideo() async {
    final _videoFile = await pickVideo();

    setState(() {
      videoFile = _videoFile;
    });
  }

  void uploadVideo() async {
    if (titleController.text.trim().isNotEmpty &&
        descriptionController.text.trim().isNotEmpty &&
        videoFile != null &&
        imageFile != null) {
      await context.read<UploadVideoCubit>().uploadVideo(
        videoFile: videoFile!,
        thumbnailFile: imageFile!,
        title: titleController.text.trim(),
        description: descriptionController.text.trim(),
        visibility: visibility,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade50,
      appBar: AppBar(
        flexibleSpace: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [Colors.indigo.shade900, Colors.deepPurple.shade500],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
        ),
        title: const Text(
          'Upload Video',
          style: TextStyle(
            fontSize: 22,
            fontWeight: FontWeight.w800,
            letterSpacing: -0.5,
            color: Colors.white,
          ),
        ),
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: BlocConsumer<UploadVideoCubit, UploadVideoState>(
        listener: (context, state) {
          if (state is UploadVideoSuccess) {
            showSnackBar('Video uploaded successfully!', context);
            Navigator.pop(context);
          } else if (state is UploadVideoError) {
            showSnackBar(state.error, context);
          }
        },
        builder: (context, state) {
          if (state is UploadVideoLoading) {
            return Center(child: CircularProgressIndicator.adaptive());
          }
          return Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 600),
              child: Card(
                margin: const EdgeInsets.all(20),
                elevation: 8,
                shadowColor: Colors.black12,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(20),
                ),
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(30.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Upload Video',
                        style: TextStyle(
                          fontSize: 28,
                          fontWeight: FontWeight.bold,
                          letterSpacing: -1,
                        ),
                      ),
                      const SizedBox(height: 25),
                      GestureDetector(
                        onTap: selectImage,
                        child: imageFile != null
                            ? ClipRRect(
                                borderRadius: BorderRadius.circular(10),
                                child: SizedBox(
                                  height: 180,
                                  width: double.infinity,
                                  child: Image.file(imageFile!, fit: BoxFit.cover),
                                ),
                              )
                            : DottedBorder(
                                dashPattern: const [8, 4],
                                color: Colors.indigo.shade200,
                                borderType: BorderType.RRect,
                                strokeCap: StrokeCap.round,
                                strokeWidth: 2,
                                radius: const Radius.circular(15),
                                child: Container(
                                  height: 150,
                                  width: double.infinity,
                                  decoration: BoxDecoration(
                                    color: Colors.indigo.shade50.withOpacity(0.5),
                                    borderRadius: BorderRadius.circular(15),
                                  ),
                                  child: Column(
                                    mainAxisAlignment: MainAxisAlignment.center,
                                    children: [
                                      Icon(Icons.image_outlined,
                                          size: 40, color: Colors.indigo),
                                      const SizedBox(height: 10),
                                      Text(
                                        'Select Thumbnail',
                                        style: TextStyle(
                                            fontSize: 16,
                                            fontWeight: FontWeight.w600,
                                            color: Colors.indigo.shade700),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                      ),
                      const SizedBox(height: 20),
                      GestureDetector(
                        onTap: selectVideo,
                        child: videoFile != null
                            ? Container(
                                padding: const EdgeInsets.all(20),
                                decoration: BoxDecoration(
                                  color: Colors.green.shade50,
                                  borderRadius: BorderRadius.circular(10),
                                  border: Border.all(color: Colors.green.shade200),
                                ),
                                child: Row(
                                  children: [
                                    Icon(Icons.check_circle, color: Colors.green),
                                    const SizedBox(width: 15),
                                    Expanded(
                                      child: Text(
                                        videoFile!.path.split('/').last,
                                        style: TextStyle(
                                            fontWeight: FontWeight.bold,
                                            color: Colors.green.shade900),
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                    ),
                                  ],
                                ),
                              )
                            : DottedBorder(
                                dashPattern: const [8, 4],
                                color: Colors.blue.shade200,
                                borderType: BorderType.RRect,
                                strokeCap: StrokeCap.round,
                                strokeWidth: 2,
                                radius: const Radius.circular(15),
                                child: Container(
                                  height: 150,
                                  width: double.infinity,
                                  decoration: BoxDecoration(
                                    color: Colors.blue.shade50.withOpacity(0.5),
                                    borderRadius: BorderRadius.circular(15),
                                  ),
                                  child: Column(
                                    mainAxisAlignment: MainAxisAlignment.center,
                                    children: [
                                      Icon(Icons.video_file_outlined,
                                          size: 40, color: Colors.blue),
                                      const SizedBox(height: 10),
                                      Text(
                                        'Select Video File',
                                        style: TextStyle(
                                            fontSize: 16,
                                            fontWeight: FontWeight.w600,
                                            color: Colors.blue.shade700),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                      ),
                      const SizedBox(height: 25),
                      TextField(
                        controller: titleController,
                        decoration: const InputDecoration(
                          hintText: 'Video Title',
                          prefixIcon: Icon(Icons.title),
                        ),
                      ),
                      const SizedBox(height: 15),
                      TextField(
                        controller: descriptionController,
                        decoration: const InputDecoration(
                          hintText: 'Description',
                          prefixIcon: Icon(Icons.description_outlined),
                        ),
                        maxLines: 4,
                        minLines: 2,
                      ),
                      const SizedBox(height: 20),
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.symmetric(horizontal: 10),
                        decoration: BoxDecoration(
                          border: Border.all(color: Colors.grey.shade300, width: 2),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: DropdownButtonHideUnderline(
                          child: DropdownButton<String>(
                            value: visibility,
                            isExpanded: true,
                            icon: const Icon(Icons.expand_more),
                            items: ['PUBLIC', 'PRIVATE', 'UNLISTED']
                                .map(
                                  (elem) => DropdownMenuItem(
                                    value: elem,
                                    child: Text(
                                      elem,
                                      style: const TextStyle(fontWeight: FontWeight.w500),
                                    ),
                                  ),
                                )
                                .toList(),
                            onChanged: (val) {
                              setState(() {
                                visibility = val!;
                              });
                            },
                          ),
                        ),
                      ),
                      const SizedBox(height: 30),
                      SizedBox(
                        width: double.infinity,
                        height: 50,
                        child: ElevatedButton(
                          onPressed: uploadVideo,
                          style: ElevatedButton.styleFrom(
                            shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(10)),
                          ),
                          child: const Text(
                            'PUBLISH VIDEO',
                            style: TextStyle(
                                fontSize: 16,
                                color: Colors.white,
                                fontWeight: FontWeight.bold),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}
