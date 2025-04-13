const startBtn = document.getElementById("start");
const icon = document.getElementById("start-icon");
const text = document.getElementById("start-text");

const resultContainer = document.getElementById("result-container");
const scoreDisplay = document.getElementById("circle-score");
const label = document.getElementById("result-label");
const server_url = "https://127.0.0.1:5000"

// Function to grab both text content and links from the page body
function grabPageContent() {
  console.log("Injecting script to grab page content and links...");

  // Grabbing all the text in the body
  const bodyText = document.body.innerText || "";  // Get the text from the body

  // Grabbing all the links
  const links = [];
  document.querySelectorAll('a').forEach(link => {
    const href = link.getAttribute('href');
    const text = link.textContent.trim();

    if (href && href.startsWith('http')) {
      links.push({ type: 'Link', text: text, href: href });
    }
  });

  return { bodyText, links };  // Return both text and links
}

// Function to send the extracted text to the backend for analysis
function sendTextToBackend(textContent) {
  const payload = {
    messages: [textContent]
  };

  return fetch(server_url + '/api/predict', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })
  .then(response => response.json())
  .then(data => {
    console.log("Backend response:", data);

    // Get confidence and label from the response
    const confidence = data.predictions[0]?.confidence || 100; // Default to 100 if confidence is not available
    const labelText = data.predictions[0]?.label || "Safe";

    // Store confidence and label in chrome storage
    chrome.storage.local.set({ confidence, labelText }, () => {
      console.log("Confidence and label saved to storage.");
    });

    

    // Store the initial analysis in Chrome storage
    const analysisWithVendor = {
      analysis: data,
      vendor: "Predictor Model",
      score: confidence,
      label: labelText
    };

    chrome.storage.local.set({ analysis: analysisWithVendor }, () => {
      console.log("Initial analysis and vendor saved to storage.");
    });

    // Update the UI with the initial report
    updateUIWithPrediction(data);
  })
  .catch(err => {
    console.error("Error sending text to backend:", err);
  });
}

// Function to update the UI with the prediction data from the backend
function updateUIWithPrediction(data) {
  const predictions = data.predictions || [];

  if (predictions.length === 0) {
    console.error("No predictions returned");
    return;
  }

  const prediction = predictions[0];  // Assuming only one prediction is returned
  const confidence = prediction.confidence;
  const labelText = prediction.label;

  // Display score (confidence)
  scoreDisplay.textContent = `${confidence.toFixed(2)}%`;

  // Display label (spam, safe, etc.)
  label.textContent = labelText;

  // Update UI color based on label
  if (labelText.toLowerCase() === "spam") {
    scoreDisplay.classList.remove("good");
    scoreDisplay.classList.add("bad");
    label.classList.add("text-danger");  // Add red color class to label
  } else {
    scoreDisplay.classList.remove("bad");
    scoreDisplay.classList.add("good");
    label.classList.remove("text-danger");  // Remove red color if not spam
  }

  // Show the result container
  resultContainer.style.display = "block";
  
}

// Function to fetch the analysis for each link from the backend
function fetchLinkAnalysis(link) {
  return fetch(server_url + '/api/scan', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ url: link.href }),
  })
  .then(response => response.json())
  .then(data => {
    return {
      link: link.href,
      report: data
    };
  })
  .catch(err => {
    console.error("Error analyzing link:", link.href, err);
    return {
      link: link.href,
      report: { error: "Failed to analyze" }
    };
  });
}

// Main handler when the start button is clicked
startBtn.addEventListener("click", () => {
  console.log("Start button clicked");

  // UI: loading state
  icon.className = "bi bi-arrow-repeat icon-spin";
  text.textContent = "Checking...";

  // Query the active tab
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const tab = tabs[0];

    // Inject script into the tab to grab content (text and links)
    chrome.scripting.executeScript(
      {
        target: { tabId: tab.id },
        func: grabPageContent,
      },
      (results) => {
        if (chrome.runtime.lastError) {
          console.error(chrome.runtime.lastError.message);
          return;
        }

        const { bodyText, links } = results[0]?.result || {};

        if (!bodyText) {
          console.error("No text found in the page.");
          return;
        }

        // Send the extracted text to the backend for analysis
        sendTextToBackend(bodyText);

        // If there are links, analyze them as well
        if (links.length > 0) {
          const linkRequests = links.map(link => fetchLinkAnalysis(link));

          Promise.all(linkRequests)
            .then(analyzedLinks => {
              // Check if any of the links are malicious
              const maliciousLinks = analyzedLinks.filter(item => item.report && item.report.malicious_count > 0);

              // Retrieve confidence and labelText from storage
              chrome.storage.local.get(["confidence", "labelText"], (result) => {
                let finalScore = result.confidence || 100; // Default to stored confidence if exists
                let analysisLabel = result.labelText || "Safe"; // Default to stored label if exists

                if(analyzedLinks.count > 0){
                  // Show the result container and info button if there are links
        
                  resultContainer.style.display = "block";
                  document.getElementById("info-container").style.display = "block";
                }

                // If any links are malicious, update the score and label
                if (maliciousLinks.length > 0) {
                  finalScore = 100;  // Set score to 100% if any malicious link is found
                  analysisLabel = "Malicious";
                  resultContainer.style.display = "block";
                  document.getElementById("info-container").style.display = "block";
                }

                // Add the model as one of the vendors for the analysis
                const finalAnalysis = {
                  score: finalScore,
                  links: analyzedLinks,
                  vendor: "Predictor Model",
                  label: analysisLabel
                };

                // Store the final analysis in Chrome storage
                chrome.storage.local.set({ analysis: finalAnalysis }, () => {
                  console.log("Final analysis with vendor saved to storage:", finalAnalysis);
                });

                // Update the UI based on the final analysis
                scoreDisplay.textContent = `${finalScore}%`;
                label.textContent = analysisLabel;

                // Update UI colors based on score
                scoreDisplay.classList.remove("good", "bad");
                scoreDisplay.classList.add(analysisLabel === "Malicious" || analysisLabel === "spam" ? "bad" : "good");

                
                // Hide the spinner
                icon.classList.remove("icon-spin");
                text.textContent = "Done";
              });
            })
            .catch(err => {
              console.error("Error processing all links:", err);
              text.textContent = "Error during analysis.";
              icon.className = "bi bi-x-circle";
            });
        } else {
          // If no links, just update the UI with the initial model analysis
          console.log("No links to analyze.");
          text.textContent = "Done";
          icon.classList.remove("icon-spin");
          
          document.getElementById("info-container").style.display = "none"; // Hide info button if no links
        }

        console.log("Detected links:", links);
      }
    );
  });
});
