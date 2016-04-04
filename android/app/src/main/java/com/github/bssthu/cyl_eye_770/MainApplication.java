package com.github.bssthu.cyl_eye_770;

import android.app.Application;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.res.AssetManager;

import java.io.InputStream;
import java.util.Properties;

/**
 * Created by bss on 2016/4/4.
 */
public class MainApplication extends Application {
    static String serverAddress = "http://localhost";

    static MessageReceiver receiver = null;

    @Override
    public void onCreate() {
        loadProperties();
        registerMessageReceiver(getApplicationContext());

        super.onCreate();
    }


    // 注册广播接收
    public static void registerMessageReceiver(Context context) {
        if (receiver == null) {
            receiver = new MessageReceiver();
        }

        IntentFilter filter = new IntentFilter();
        filter.setPriority(IntentFilter.SYSTEM_HIGH_PRIORITY);
        filter.addAction(Intent.ACTION_TIME_TICK);
        context.registerReceiver(receiver, filter);
    }

    // 取消广播接收
    public static void unregisterMessageReceiver(Context context) {
        try {
            context.unregisterReceiver(receiver);
        } catch (IllegalArgumentException ignore) { }
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
