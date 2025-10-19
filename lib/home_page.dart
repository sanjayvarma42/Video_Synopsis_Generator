import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class HomePage extends StatefulWidget {
  final String username;
  const HomePage({required this.username});

  @override
  _HomePageState createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final TextEditingController _urlController = TextEditingController();
  String title = '';
  String channel = '';
  String summary = '';
  String transcript = '';
  String videoId = '';
  bool isLoading = false;
  String errorMessage = '';

  Future<void> summarizeVideo() async {
    final url = _urlController.text.trim();
    if (url.isEmpty) return;

    setState(() {
      isLoading = true;
      errorMessage = '';
      title = '';
      channel = '';
      summary = '';
      transcript = '';

      videoId = getVideoIdFromUrl(url);
    });

    try {
      final response = await http.post(
        Uri.parse('http://192.168.208.20:5000/summarize'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'url': url}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          title = data['title'] ?? '';
          channel = data['channel'] ?? '';
          summary = data['summary'] ?? 'No summary available.';
          transcript = data['transcript'] ?? 'Transcript not available.';
        });
      } else {
        final data = jsonDecode(response.body);
        setState(() {
          errorMessage = data['error'] ?? 'Something went wrong.';
        });
      }
    } catch (e) {
      setState(() {
        errorMessage = 'Error: $e';
      });
    } finally {
      setState(() => isLoading = false);
    }
  }

  String getVideoIdFromUrl(String url) {
    try {
      final uri = Uri.parse(url);
      if (uri.host.contains('youtu.be')) {
        return uri.pathSegments.first;
      } else if (uri.host.contains('youtube.com')) {
        return uri.queryParameters['v'] ?? '';
      }
    } catch (_) {}
    return '';
  }

  Widget infoBlock(String label, String content) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: TextStyle(fontWeight: FontWeight.bold)),
          SizedBox(height: 4),
          Text(content),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("YouTube Summarizer")),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text("Welcome, ${widget.username}!", style: TextStyle(fontSize: 18, fontWeight: FontWeight.w500)),
            SizedBox(height: 16),
            TextField(
              controller: _urlController,
              decoration: InputDecoration(
                labelText: 'Enter YouTube Video URL',
                border: OutlineInputBorder(),
                suffixIcon: IconButton(
                  icon: Icon(Icons.clear),
                  onPressed: () => _urlController.clear(),
                ),
              ),
            ),
            SizedBox(height: 12),
            ElevatedButton(
              onPressed: isLoading ? null : summarizeVideo,
              child: isLoading
                  ? CircularProgressIndicator(color: Colors.white)
                  : Text("Summarize"),
              style: ElevatedButton.styleFrom(
                minimumSize: Size(double.infinity, 50),
              ),
            ),
            SizedBox(height: 20),
            Expanded(
              child: SingleChildScrollView(
                child: errorMessage.isNotEmpty
                    ? Text(errorMessage, style: TextStyle(color: Colors.red))
                    : Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (videoId.isNotEmpty)
                      ClipRRect(
                        borderRadius: BorderRadius.circular(10),
                        child: Image.network(
                          'https://img.youtube.com/vi/$videoId/0.jpg',
                        ),
                      ),
                    if (title.isNotEmpty) infoBlock("Title", title),
                    if (channel.isNotEmpty) infoBlock("Channel", channel),
                    if (summary.isNotEmpty) infoBlock("Summary", summary),
                    if (transcript.isNotEmpty) infoBlock("Transcript", transcript),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
