import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:video_streaming_app_frontend/cubits/auth/auth_cubit.dart';
import 'package:video_streaming_app_frontend/pages/auth/signup_page.dart';
import 'package:video_streaming_app_frontend/pages/home/upload_page.dart';
import 'package:video_streaming_app_frontend/pages/home/video_player_page.dart';
import 'package:video_streaming_app_frontend/services/video_service.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  late Future<List<Map<String, dynamic>>> videosFuture;

  @override
  void initState() {
    super.initState();
    _fetchVideos();
  }

  Future<void> _fetchVideos() async {
    setState(() {
      videosFuture = VideoService().getVideos();
    });
    try {
      await videosFuture;
    } catch (_) {}
  }

  Widget _buildVideoCard(BuildContext context, Map<String, dynamic> video) {
    final thumbnail =
        "https://daof0lmdufmhd.cloudfront.net/${video['video_s3_key'].replaceAll('.mp4', "").replaceAll("videos/", "thumbnails/")}";

    return GestureDetector(
      onTap: () {
        Navigator.push(context, VideoPlayerPage.route(video));
      },
      child: Card(
        margin: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
        elevation: 10,
        shadowColor: Colors.black26,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            ClipRRect(
              borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
              child: AspectRatio(
                aspectRatio: 16 / 9,
                child: Stack(
                  fit: StackFit.expand,
                  children: [
                    Image.network(
                      thumbnail,
                      fit: BoxFit.cover,
                      headers: const {'Content-Type': 'image/jpg'},
                      errorBuilder: (context, error, stackTrace) => Container(
                        color: Colors.grey.shade200,
                        child: const Center(child: Icon(Icons.error_outline, size: 40)),
                      ),
                    ),
                    Container(
                      color: Colors.black.withOpacity(0.2), // Slight darkening for play button contrast
                      child: Center(
                        child: Icon(
                          Icons.play_circle_fill,
                          color: Colors.white.withOpacity(0.9),
                          size: 60,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    video['title'] ?? 'Untitled Video',
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w800,
                      letterSpacing: -0.5,
                      color: Colors.black87,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      const Icon(Icons.play_arrow_rounded, size: 16, color: Colors.indigoAccent),
                      const SizedBox(width: 4),
                      Text(
                        'Watch now',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey.shade600,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade100,
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
          'Streamr',
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.w900,
            letterSpacing: -1,
            color: Colors.white,
          ),
        ),
        elevation: 0,
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 8.0),
            child: IconButton(
              onPressed: () {
                context.read<AuthCubit>().logoutUser();
              },
              icon: const Icon(Icons.logout, color: Colors.white, size: 26),
              tooltip: 'Logout',
            ),
          ),
          Padding(
            padding: const EdgeInsets.only(right: 8.0),
            child: IconButton(
              onPressed: () {
                Navigator.push(context, UploadPage.route());
              },
              icon: const Icon(Icons.add_circle_outline, color: Colors.white, size: 28),
              tooltip: 'Upload Video',
            ),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _fetchVideos,
        color: Colors.indigoAccent,
        child: FutureBuilder(
          future: videosFuture,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Center(child: CircularProgressIndicator.adaptive());
            }
            if (snapshot.hasError) {
              return ListView(
                physics: const AlwaysScrollableScrollPhysics(),
                children: [
                  SizedBox(height: MediaQuery.of(context).size.height * 0.3),
                  Center(child: Text(snapshot.error.toString())),
                ],
              );
            }
            final videos = snapshot.data!;

            if (videos.isEmpty) {
              return ListView(
                physics: const AlwaysScrollableScrollPhysics(),
                children: [
                  SizedBox(height: MediaQuery.of(context).size.height * 0.3),
                  Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.videocam_off_outlined, size: 80, color: Colors.grey.shade400),
                        const SizedBox(height: 16),
                        Text(
                          'There are no videos currently.',
                          style: TextStyle(
                            fontSize: 18,
                            color: Colors.grey.shade600,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              );
            }

            return LayoutBuilder(
              builder: (context, constraints) {
                final isWide = constraints.maxWidth > 700;
                return isWide
                    ? GridView.builder(
                        physics: const AlwaysScrollableScrollPhysics(),
                        padding: const EdgeInsets.all(20),
                        gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
                          maxCrossAxisExtent: 400,
                          crossAxisSpacing: 20,
                          mainAxisSpacing: 20,
                          childAspectRatio: 1.1,
                        ),
                        itemCount: videos.length,
                        itemBuilder: (context, index) {
                          return _buildVideoCard(context, videos[index]);
                        },
                      )
                    : ListView.builder(
                        physics: const AlwaysScrollableScrollPhysics(),
                        padding: const EdgeInsets.only(top: 10, bottom: 20),
                        itemCount: videos.length,
                        itemBuilder: (context, index) {
                          return _buildVideoCard(context, videos[index]);
                        },
                      );
              },
            );
          },
        ),
      ),
    );
  }
}
