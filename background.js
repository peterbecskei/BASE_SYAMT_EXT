// background.js - Chrome Extension (Manifest V3)

// Konfiguráció
const CONFIG = {
  //START_ID: 22308457,
 // START_ID: 34931604,
//  START_ID: 1251923,
//  START_ID: 436662325,
START_ID: undefined,
//  BASE_URL: 'https://www.hasznaltauto.hu/finanszirozas/',
 // BASE_URL: 'https://www.hasznaltauto.hu/',
  BASE_URL: 'https://www.automobile.at/boerse/expose/',
 // BASE_URL2 : 'https://suchen.mobile.de/fahrzeuge/details.html?id=',
 // BASE_URL : "https://www.autoscout24.com/lst?atype=C&cy=D%2CA%2CB%2CE%2CF%2CI%2CL%2CNL&damaged_listing=exclude&desc=1&powertype=kw&search_id=1unft4d8lu3&sort=age&source=homepage_search-mask&ustate=N%2CU",
//  BASE_URL3: 'https://realestatehungary.hu/',
//  BASE_URL4: 'https://immobilienungarn.net/',
//  BASE_URL5: 'https://www.immobilien.hu/',
  CHECK_INTERVAL: 150, // 10 másodperc várakozás kérek között
  STORAGE_KEY: 'URL_data'
};

  // Fő változó az adatok tárolására
  let URLData = {};
  

// Extension install/update esetén
chrome.runtime.onInstalled.addListener(() => {
  CONFIG.START_ID = 1251923,
  LastID = CONFIG.START_ID;
  //loadStoredData();
  startChecking();
});


// Extension indításakor
chrome.runtime.onStartup.addListener(() => {
  loadStoredData();
  updateLastIDFromURLData();
  startChecking();
});

// Adatok betöltése localStorage-ből
function loadStoredData() {
  chrome.storage.local.get([CONFIG.STORAGE_KEY], (result) => {
    if (result[CONFIG.STORAGE_KEY]) {
      URLData = result[CONFIG.STORAGE_KEY];
      console.log('Adatok betöltve:', Object.keys(URLData).length, 'elem');
    } else {
      // Nincs tárolt adat: állítsunk alapértelmezett START_ID értéket
            LastID = CONFIG.START_ID;
      saveLastIDToSession();
      console.log('Nincs tárolt adat. Alapértelmezett START_ID beállítva:', CONFIG.START_ID);
    }
  });
}

// Adatok mentése localStorage-ba
function saveData() {
  chrome.storage.local.set({ [CONFIG.STORAGE_KEY]: URLData }, () => {
    //console.log('Adatok elmentve:', Object.keys(URLData).length, 'elem');
    updateLastIDFromURLData();
  });
}


// LastID to session store
function saveLastIDToSession() {
  if (typeof LastID === 'number') {
    chrome.storage.session.set({ LastID });
  }
}



// Állítsuk a LastID-t az URLData legnagyobb, létező (exists=true) azonosítójára
function updateLastIDFromURLData() {
  try {
    const candidateIds = Object.keys(URLData)
      .filter((key) => URLData[key] && URLData[key].exists === true)
      .map((key) => Number(key))
      .filter((n) => Number.isFinite(n));
    if (candidateIds.length > 0) {
      const maxId = Math.max(...candidateIds);
      LastID = maxId;
      saveLastIDToSession();
      console.log('LastID frissítve az URLData alapján:', LastID);
    }
  } catch (e) {
    console.error('Nem sikerült LastID-t frissíteni URLData-ból:', e);
  }
}

// Tartalom feldolgozása JSON objektummá (JSON vagy XML bemenet esetén)
function parseContentToJson(rawContent) {
  if (!rawContent || typeof rawContent !== 'string') {
    return { raw: rawContent };
  }
  // 1) Próbáljuk JSON-ként
  try {
    return JSON.parse(rawContent);
  } catch (_) {
    // nem JSON
  }
  // 2) XML egyszerű feldolgozása DOMParser nélkül (MV3 background-ban nem elérhető)
  //    Egyszerű fallback: kulcs-érték párok kinyerése XML tagekből
  try {
    const result = {};
    const tagRegex = /<([A-Za-z0-9_:-]+)[^>]*>([\s\S]*?)<\/\1>/g;
    let m;
    while ((m = tagRegex.exec(rawContent)) !== null) {
      const key = m[1];
      const val = m[2].trim();
      if (result[key] === undefined) result[key] = val;
      else if (Array.isArray(result[key])) result[key].push(val);
      else result[key] = [result[key], val];
    }
    if (Object.keys(result).length > 0) return result;
  } catch (_) {}
  // Ha semmi nem sikerült, az eredetit adjuk vissza
  return { raw: rawContent };
}



// URL ellenőrzése fetch-el
async function checkUrl(id) {
  const url = `${CONFIG.BASE_URL}${id}`;
 // const url = `${CONFIG.BASE_URL}`;

  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    });
// időkorlát
    if (response.status === 429) {
      console.log(`ID ${id}: 429  várakozás: 60 másodperc`);
      await new Promise(resolve => setTimeout(resolve, 61000));
      await checkUrl(id);
      return false;
    }
// capcsha
    if (response.status === 302) {
      console.log(`ID ${id}: 302 capchac`);
  // Nyissuk meg az URL-t egy új Chrome fülön
  try {
    chrome.tabs.create( url );
  } catch (e) {
    console.error('Nem sikerült megnyitni a lapot:', e);
  }
  
      await new Promise(resolve => setTimeout(resolve, 60000));
      await checkUrl(id);
      return false;
    }

    if (response.status === 200) {
      console.log(`ID ${id}: LÉTEZIK (200)`);

      // Ha szeretnéd a teljes tartalmat is, használd ezt:
      // const fullResponse = await fetch(url);
     // const content = await Response.text();
  
      urlapi=  `https://api.automobile.at/api/v1/public/listing/${id}`
      const responseapi = await fetch(urlapi, {
        method: 'GET',
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
      })
      const content = await responseapi.text();
      const parsed = parseContentToJson(content);
      //const parsed = "NULL"
      URLData[id] = {
        exists: true,
        url: url,
        timestamp: new Date().toISOString(),
        ELEMData: parsed.title
      };
    // Frissítsük és mentsük az aktuális LastID értéket a session tárolóba
    LastID = id;
    saveLastIDToSession();
    saveData();
    return true;
    } else {
      console.log(`ID ${id}: Nem létezik (${response.status}) ${url}  `);
      URLData[id] = {
        exists: false,
        url: url,
        timestamp: new Date().toISOString(),
        ELEMData: "NULL"
      };
      // Sikertelen találatnál is megpróbálhatjuk frissíteni a LastID-t
      updateLastIDFromURLData();
      return false;
    }
  } catch (error) {
    console.error(`ID ${id}: Hiba -`, error.message);
    URLData[id] = {
      exists: false,
      url: url,
      ELEMData: error.message,
      timestamp: new Date().toISOString()
    };
    updateLastIDFromURLData();
    return false;
  }
}

// Fő ellenőrző függvény
async function startChecking() {
  console.log('Autó adatok ellenőrzése elkezdődött...');

  for (let id = LastID; id <= LastID + 100; id++) {
    // Ha már ellenőriztük korábban, kihagyjuk
    if (URLData[id] && URLData[id].exists !== undefined) {
      console.log(`ID ${id}: Már ellenőrizve korábban`);
      continue;
    }

    await checkUrl(id);

    // Várakozás a következő kérés előtt
    await new Promise(resolve => setTimeout(resolve, CONFIG.CHECK_INTERVAL));
  }

  console.log('Ellenőrzés befejeződött');
}

// Külső hívások kezelése (pl. popup-ból)
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  switch (request.action) {
    case 'startCheck':
      startChecking();
      sendResponse({ status: 'started' });
      break;

    case 'getData':
      sendResponse({ data: URLData, count: Object.keys(URLData).length });
      break;

    case 'clearData':
      URLData = {};
      chrome.storage.local.remove([CONFIG.STORAGE_KEY], () => {
        sendResponse({ status: 'cleared' });
      });
      break;

    default:
      sendResponse({ error: 'Ismeretlen művelet' });
  }

  return true; // Aszinkron válaszhoz szükséges
});

// Periodikus ellenőrzés (opcionális)
/*
setInterval(() => {
  console.log('Periodikus ellenőrzés...');
  startChecking();
}, 3600000); // Óránként
*/