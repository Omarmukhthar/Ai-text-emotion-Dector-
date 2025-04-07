document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("analyze-btn").addEventListener("click", function () {
        const textInput = document.getElementById("text-input").value.trim();
        const selectedLanguage = document.getElementById("language").value; 
        const resultDiv = document.getElementById("result");
        const loader = document.getElementById("loader");

        if (!textInput) {
            resultDiv.innerHTML = "⚠️ Please enter some text.";
            return;
        }

        // Show loader and clear previous result
        loader.style.display = "block"; 
        resultDiv.innerHTML = "";

        console.log("Sending request:", { text: textInput, language: selectedLanguage });

        fetch("http://127.0.0.1:5000/analyze", {
            method: "POST",  
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ text: textInput, language: selectedLanguage }) 
        })
        .then(response => response.json())
        .then(data => {
            console.log("Response from server:", data);
            loader.style.display = "none";

            if (data.labels && data.scores) {
                let topEmotion = data.labels[0];  
                let confidence = (data.scores[0] * 100).toFixed(2);  

                resultDiv.innerHTML = `✅ Emotion: <b>${topEmotion}</b> (${confidence}%)`;
            } else {
                resultDiv.innerHTML = `⚠️ Error: ${data.error || "Unexpected response format"}`;
            }
        })
        .catch(error => {
            console.error("Fetch error:", error);
            loader.style.display = "none";
            resultDiv.innerHTML = "❌ An error occurred.";
        });
    });
});
