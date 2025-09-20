#ifndef BACKGROUND_H
#define BACKGROUND_H

#include <string>
#include <map>
#include <vector>
#include <fstream>
#include <iostream>
#include <sstream>
#include <chrono>
#include <thread>
#include <curl/curl.h>
#include <json/json.h>

// Configuration class
class Config {
public:
    static const int START_ID = 1251923;
    static const std::string BASE_URL;
    static const double CHECK_INTERVAL_SECONDS;
    static const std::string URL_DATA_CSV;
    static const std::string LAST_ID_FILE;
};

// URL data structure
struct UrlData {
    bool exists;
    std::string url;
    std::string timestamp;
    std::string elemdata;
};

// Main background runner class
class BackgroundRunner {
private:
    std::map<int, UrlData> url_data;
    int last_id;
    
    // Utility functions
    std::string now_iso();
    int load_last_id();
    void save_last_id(int id);
    std::map<int, UrlData> load_url_data();
    void save_url_data();
    int update_last_id_from_data();
    
    // HTTP functions
    int http_status(const std::string& url, const std::string& method = "GET");
    std::string get_api_data(const std::string& api_url);
    
    // Main checking function
    bool check_url(int id);
    
public:
    BackgroundRunner();
    ~BackgroundRunner();
    void start_checking();
};

// Callback function for libcurl
size_t WriteCallback(void* contents, size_t size, size_t nmemb, std::string* s);

#endif // BACKGROUND_H
