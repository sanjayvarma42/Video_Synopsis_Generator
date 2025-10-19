import 'package:http/http.dart' as http;

class Service {
  static Future<String> summarizeVideo(String url) async {
    try {
      final response = await http.post(
        Uri.parse("http://<YOUR_FLASK_IP>:5000/summarize"),
        headers: {"Content-Type": "application/json"},
        body: '{"url": "$url"}',
      );
      if (response.statusCode == 200) {
        return response.body;
      } else {
        return "Failed to summarize.";
      }
    } catch (e) {
      return "Error: $e";
    }
  }
}
