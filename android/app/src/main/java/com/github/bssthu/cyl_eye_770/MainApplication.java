package com.github.bssthu.cyl_eye_770;

import android.app.Application;
import android.content.res.AssetManager;

import java.io.InputStream;
import java.util.Properties;

/**
 * Created by bss on 2016/4/4.
 */
public class MainApplication extends Application {
    static String serverAddress = "http://localhost";

    @Override
    public void onCreate() {
        loadProperties();

        // start watcher service
        WatcherService.restartService(this);

        super.onCreate();
    }


    // 从 assets 中载入配置
    private void loadProperties() {
        try {
            Properties properties = new Properties();
            AssetManager am = getApplicationContext().getAssets();
            InputStream inputStream = am.open("local.properties");
            properties.load(inputStream);
            serverAddress = properties.getProperty("serverAddress");
        } catch (Exception ignore) {
            ignore.printStackTrace();
        }
    }
}
