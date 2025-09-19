
document.addEventListener('DOMContentLoaded', function() {
  const saveCurrentBtn = document.getElementById('saveCurrent');
  const viewSavedBtn = document.getElementById('viewSaved');
  const statusDiv = document.getElementById('status');
  const savedList = document.getElementById('savedList');
  
  // Load recent saved items
  loadRecentItems();
  
  // Save current page HTML
  saveCurrentBtn.addEventListener('click', function() {
    //chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    //  chrome.scripting.executeScript({
     //   target: {tabId: tabs[0].id},
     //   files: ['script.js']
   //   }, () => {
        // Call the function
        injectScript();

        showStatus('HTML content saved successfully!', 'success');
        // Reload recent items after a short delay
        setTimeout(loadRecentItems, 500);
      });


async function injectScript() {
  try {
    const tabs = await chrome.tabs.query({active: true, currentWindow: true});
    if (tabs.length === 0) {
      throw new Error('No active tab found');
    }

    await chrome.scripting.executeScript({
      target: {tabId: tabs[0].id},
      files: ['script.js']
    });

    console.log('Script injected successfully');
  } catch (error) {
    console.error('Error:', error);
  }
}



  // View saved HTML
  viewSavedBtn.addEventListener('click', function() {
    chrome.tabs.create({url: chrome.runtime.getURL('saved.html')});
  });
  
  // Load recent saved items from storage
  function loadRecentItems() {
    chrome.storage.local.get(null, function(items) {
      savedList.innerHTML = '';
      
      // Filter and sort items
      const htmlItems = [];
      for (let key in items) {
        if (key.startsWith('tab_html_')) {
          htmlItems.push({
            key: key,
            data: items[key]
          });
        }
      }
      
      // Sort by timestamp (newest first)
      htmlItems.sort((a, b) => 
        new Date(b.data.timestamp) - new Date(a.data.timestamp)
      );
      
      // Display recent items (max 5)
      const displayItems = htmlItems.slice(0, 5);
      if (displayItems.length === 0) {
        savedList.innerHTML = '<p>No saved HTML yet</p>';
        return;
      }
      
      displayItems.forEach(item => {
        const div = document.createElement('div');
        div.className = 'saved-item';
        div.innerHTML = `
          <strong>${item.data.title}</strong><br>
          <small>${new Date(item.data.timestamp).toLocaleString()}</small>
        `;
        savedList.appendChild(div);
      });
    });
  }
  
  // Show status message
  function showStatus(message, type) {
    statusDiv.textContent = message;
    statusDiv.className = `status ${type}`;
    statusDiv.style.display = 'block';
    
    // Hide after 3 seconds
    setTimeout(() => {
      statusDiv.style.display = 'none';
    }, 3000);
  }
  
  // Listen for messages from content script
  chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.type === 'html_saved') {
      // Store the metadata in chrome.storage
      chrome.storage.local.set({
        [request.key]: {
          url: request.url,
          title: request.title,
          timestamp: request.timestamp
        }
      });
      
      // Update the UI
      loadRecentItems();
    }
  });
});