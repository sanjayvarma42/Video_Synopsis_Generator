document.getElementById("summarizeBtn").addEventListener("click", () => {
  chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
    const url = tabs[0].url;

    if (!url.includes("youtube.com/watch")) {
      document.getElementById("result").innerHTML = "<p style='color:red;'>Not a YouTube video.</p>";
      return;
    }

    document.getElementById("result").innerHTML = "Processing...";

    try {
      const response = await fetch("http://127.0.0.1:5000/summarize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url })
      });

      const data = await response.json();

      if (data.error) {
        document.getElementById("result").innerHTML = `<p style="color:red;">${data.error}</p>`;
        return;
      }

      document.getElementById("result").innerHTML = `
        <strong>Title:</strong> ${data.title}<br/>
        <strong>Channel:</strong> ${data.channel}<br/><br/>
        <img src="https://img.youtube.com/vi/${data.video_id}/0.jpg" width="100%"/><br/>
        <strong>Summary:</strong><br/>
        <div id="summary">${data.summary}</div>
        <br/>
        <strong>Transcript:</strong><br/>
        <div id="transcript">${data.transcript.slice(0, 500)}...</div>
      `;
    } catch (error) {
      document.getElementById("result").innerHTML = `<p style="color:red;">${error.message}</p>`;
    }
  });
});
