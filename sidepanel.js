
document.addEventListener('DOMContentLoaded', function() {
// Konfiguráció
const CONFIG = {
 //  BASE_URL: 'https://www.hasznaltauto.hu/finanszirozas/',
 // BASE_URL: 'https://www.hasznaltauto.hu/',
  BASE_URL: 'https://www.automobile.at/boerse/expose/',
//  BASE_URL : 'https://suchen.mobile.de/fahrzeuge/details.html?id=',
//  BASE_URL : "https://www.autoscout24.com/lst?atype=C&cy=D%2CA%2CB%2CE%2CF%2CI%2CL%2CNL&damaged_listing=exclude&desc=1&powertype=kw&search_id=1unft4d8lu3&sort=age&source=homepage_search-mask&ustate=N%2CU",
 
//  BASE_URL3: 'https://realestatehungary.hu/',
//  BASE_URL4: 'https://immobilienungarn.net/',
//  BASE_URL5: 'https://www.immobilien.hu/',
  CHECK_INTERVAL: 650, // 10 másodperc várakozás kérek között
STORAGE_KEY: 'URL_data'
};


  const saveCurrentBtn = document.getElementById('saveCurrent');
  const viewSavedBtn = document.getElementById('viewSaved');
  const statusDiv = document.getElementById('status');
  const savedList = document.getElementById('savedList');
  let lastStartCheckResponse = null;
  
  // Load recent saved items
  let URLData = {};
  loadStoredData();
  function loadStoredData() {
    chrome.storage.local.get([CONFIG.STORAGE_KEY], (result) => {
      if (result[CONFIG.STORAGE_KEY]) {
        URLData = result[CONFIG.STORAGE_KEY];
        console.log('Adatok betöltve:', Object.keys(URLData).length, 'elem');
      } else {
        // Nincs tárolt adat: állítsunk alapértelmezett START_ID értéket
            console.log('Nincs tárolt adat:');
      }
    });
  }
  
  let LastID = null;
  loadLastID();
  function loadLastID() {
    chrome.storage.session.get("LastID", (result) => {
      if (result["LastID"]) {
        LastID = result["LastID"];
        console.log('Adatok betöltve lastID:', LastID, ' ');
      } else {
        // Nincs tárolt adat: állítsunk alapértelmezett START_ID értéket
            console.log('Nincs tárolt adat:');
      }
    });
  }

  // Figyeljük a session storage LastID változását és frissítsük a listát
  let OldID = null;
  chrome.storage.onChanged.addListener((changes, areaName) => {
    if (areaName !== 'session') return;
    if (changes.LastID) {
      OldID = changes.LastID.oldValue;
      LastID = changes.LastID.newValue
      loadRecentItems();
    }
  });

  // Save current page HTML
  saveCurrentBtn.addEventListener('click', function() {
    //chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    //  chrome.scripting.executeScript({
     //   target: {tabId: tabs[0].id},
     //   files: ['script.js']
   //   }, () => {
        // Call the function
        //injectScript();

        // Kérjük a háttér szolgáltatót az ellenőrzés indítására
        chrome.runtime.sendMessage({ action: 'startCheck' }, (response) => {
          lastStartCheckResponse = response;
          // opcionális: log vagy státusz
          try {
            console.log('startCheck válasz:', response);
          } catch (e) {}
        });

        showStatus('Symat background (startCheck sent)', lastStartCheckResponse);
        // Reload recent items after a short delay
        setTimeout(loadRecentItems, 500);
      });


  // View saved HTML
  viewSavedBtn.addEventListener('click', function() {
    loadRecentItems();
   // chrome.tabs.create({url: chrome.runtime.getURL('saved.html')});
  });
  
  // Load recent saved items from storage
  function loadRecentItems() {
    loadStoredData()
    savedList.innerHTML = '';
   //   console.log("sss")
   //    Filter and sort items  
      const htmlItems = [];
      for (let key in URLData) {
           htmlItems.push({
           key: key,
            data: URLData[key]
          });
        }
      
      
   //    Sort by timestamp (newest first)
      htmlItems.sort((a, b) => 
       new Date(b.data.timestamp) - new Date(a.data.timestamp)
     );
      
      // Display recent items (max 5)
      const displayItems = htmlItems.slice(0, 100);
      if (displayItems.length === 0) {
        savedList.innerHTML = '<p>No saved HTML yet</p>';
        return;
      }
      
      displayItems.forEach(item => {
        const div = document.createElement('div');
        div.className = 'saved-item';
        div.innerHTML = `
            <strong>${item.data.ELEMData} ${item.data.exists}</strong><br>
        <small>${new Date(item.data.timestamp).toLocaleString()}  ${item.data.url}</small>
        `;
        savedList.appendChild(div);
      });
     
  //  }  );
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