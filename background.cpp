#include "background.h"
#include <iomanip>
#include <algorithm>

// Static member definitions
const std::string Config::BASE_URL = "https://www.automobile.at/boerse/expose/";
const double Config::CHECK_INTERVAL_SECONDS = 0.2;
const std::string Config::URL_DATA_CSV = "URL_data.csv";
const std::string Config::LAST_ID_FILE = "LastID.TXT";

// Callback function for libcurl
size_t WriteCallback(void* contents, size_t size, size_t nmemb, std::string* s) {
    size_t newLength = size * nmemb;
    try {
        s->append((char*)contents, newLength);
        return newLength;
    } catch (std::bad_alloc& e) {
        return 0;
    }
}

// Constructor
BackgroundRunner::BackgroundRunner() : last_id(Config::START_ID) {
    curl_global_init(CURL_GLOBAL_DEFAULT);
    url_data = load_url_data();
    last_id = load_last_id();
}

// Destructor
BackgroundRunner::~BackgroundRunner() {
    curl_global_cleanup();
}

// Get current timestamp in ISO format
std::string BackgroundRunner::now_iso() {
    auto now = std::chrono::system_clock::now();
    auto time_t = std::chrono::system_clock::to_time_t(now);
    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
        now.time_since_epoch()) % 1000;
    
    std::stringstream ss;
    ss << std::put_time(std::gmtime(&time_t), "%Y-%m-%dT%H:%M:%S");
    ss << '.' << std::setfill('0') << std::setw(3) << ms.count() << "Z";
    return ss.str();
}

// Load last ID from file
int BackgroundRunner::load_last_id() {
    std::ifstream file(Config::LAST_ID_FILE);
    if (file.is_open()) {
        std::string content;
        if (std::getline(file, content)) {
            try {
                return std::stoi(content);
            } catch (const std::exception&) {
                // Fall through to return START_ID
            }
        }
        file.close();
    }
    return Config::START_ID;
}

// Save last ID to file
void BackgroundRunner::save_last_id(int id) {
    std::ofstream file(Config::LAST_ID_FILE);
    if (file.is_open()) {
        file << id;
        file.close();
    }
}

// Load URL data from CSV file
std::map<int, UrlData> BackgroundRunner::load_url_data() {
    std::map<int, UrlData> data;
    std::ifstream file(Config::URL_DATA_CSV);
    
    if (!file.is_open()) {
        return data;
    }
    
    std::string line;
    bool first_line = true;
    
    while (std::getline(file, line)) {
        if (first_line) {
            first_line = false;
            continue; // Skip header
        }
        
        std::stringstream ss(line);
        std::string token;
        std::vector<std::string> tokens;
        
        while (std::getline(ss, token, ',')) {
            tokens.push_back(token);
        }
        
        if (tokens.size() >= 5) {
            try {
                int id = std::stoi(tokens[0]);
                UrlData url_data;
                url_data.exists = (tokens[1] == "true");
                url_data.url = tokens[2];
                url_data.timestamp = tokens[3];
                url_data.elemdata = tokens[4];
                data[id] = url_data;
            } catch (const std::exception&) {
                continue;
            }
        }
    }
    
    file.close();
    return data;
}

// Save URL data to CSV file
void BackgroundRunner::save_url_data() {
    std::ofstream file(Config::URL_DATA_CSV);
    if (!file.is_open()) {
        return;
    }
    
    // Write header
    file << "id,exists,url,timestamp,elemdata\n";
    
    // Write data
    for (const auto& pair : url_data) {
        file << pair.first << ","
             << (pair.second.exists ? "true" : "false") << ","
             << pair.second.url << ","
             << pair.second.timestamp << ","
             << pair.second.elemdata << "\n";
    }
    
    file.close();
}

// Update last ID based on existing data
int BackgroundRunner::update_last_id_from_data() {
    int max_id = last_id;
    for (const auto& pair : url_data) {
        if (pair.second.exists && pair.first > max_id) {
            max_id = pair.first;
        }
    }
    
    if (max_id != last_id) {
        save_last_id(max_id);
    }
    
    return max_id;
}

// Check HTTP status of URL
int BackgroundRunner::http_status(const std::string& url, const std::string& method) {
    CURL* curl;
    CURLcode res;
    long response_code = 0;
    
    curl = curl_easy_init();
    if (curl) {
        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L);
        curl_easy_setopt(curl, CURLOPT_TIMEOUT, 20L);
        curl_easy_setopt(curl, CURLOPT_USERAGENT, 
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36");
        
        if (method == "HEAD") {
            curl_easy_setopt(curl, CURLOPT_NOBODY, 1L);
        }
        
        res = curl_easy_perform(curl);
        
        if (res == CURLE_OK) {
            curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &response_code);
        }
        
        curl_easy_cleanup(curl);
    }
    
    return static_cast<int>(response_code);
}

// Get API data
std::string BackgroundRunner::get_api_data(const std::string& api_url) {
    CURL* curl;
    CURLcode res;
    std::string response_data;
    long response_code = 0;
    
    curl = curl_easy_init();
    if (curl) {
        curl_easy_setopt(curl, CURLOPT_URL, api_url.c_str());
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response_data);
        curl_easy_setopt(curl, CURLOPT_TIMEOUT, 20L);
        curl_easy_setopt(curl, CURLOPT_USERAGENT, 
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36");
        
        res = curl_easy_perform(curl);
        
        if (res == CURLE_OK) {
            curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &response_code);
            if (response_code == 200) {
                curl_easy_cleanup(curl);
                return response_data;
            } else {
                curl_easy_cleanup(curl);
                return "API_ERROR_" + std::to_string(response_code);
            }
        } else {
            curl_easy_cleanup(curl);
            return "API_ERROR_CONNECTION";
        }
    }
    
    return "API_ERROR_UNKNOWN";
}

// Check URL for specific ID
bool BackgroundRunner::check_url(int id) {
    std::string url = Config::BASE_URL + std::to_string(id);
    int status = http_status(url, "GET");
    
    // Handle rate limiting and captcha cases
    if (status == 429) {
        std::cout << "ID " << id << ": 429 várakozás 60s" << std::endl;
        std::this_thread::sleep_for(std::chrono::seconds(61));
        status = http_status(url, "GET");
    } else if (status == 302) {
        std::cout << "ID " << id << ": 302 captcha/redirect, várakozás 60s" << std::endl;
        std::this_thread::sleep_for(std::chrono::seconds(60));
        status = http_status(url, "GET");
    }
    
    UrlData data;
    data.url = url;
    data.timestamp = now_iso();
    
    if (status == 200) {
        std::string api_url = "https://api.automobile.at/api/v1/public/listing/" + std::to_string(id);
        std::string elemdata = get_api_data(api_url);
        
        data.exists = true;
        data.elemdata = elemdata.substr(10, 42); // Extract substring like Python version
        
        url_data[id] = data;
        std::cout << id << " " << data.elemdata << std::endl;
        return true;
    } else {
        data.exists = false;
        data.elemdata = "NA";
        
        url_data[id] = data;
        return false;
    }
}

// Main checking function
void BackgroundRunner::start_checking() {
    std::cout << "Kezdés. LastID = " << last_id << std::endl;
    
    // Simple range window like Python version
    int upper = last_id + 30;
    for (int id = last_id; id <= upper; ++id) {
        // Skip if already known
        if (url_data.find(id) != url_data.end()) {
            std::cout << "ID " << id << ": Már ellenőrizve korábban" << std::endl;
            continue;
        }
        
        bool ok = check_url(id);
        
        // Persist after each check
        save_url_data();
        
        // Update LastID based on known good items
        last_id = update_last_id_from_data();
        save_last_id(ok ? last_id : last_id);
        
        std::this_thread::sleep_for(std::chrono::milliseconds(
            static_cast<int>(Config::CHECK_INTERVAL_SECONDS * 1000)));
    }
    
    std::cout << "Ellenőrzés befejeződött" << std::endl;
}

// Main function
int main() {
    BackgroundRunner runner;
    runner.start_checking();
    return 0;
}
