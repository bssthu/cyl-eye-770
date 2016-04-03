package com.github.bssthu.cyl_eye_770;


import android.app.Activity;
import android.app.Notification;
import android.app.NotificationManager;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.res.AssetManager;
import android.os.Bundle;
import android.support.v4.app.NotificationCompat;
import android.view.View;
import android.widget.TextView;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Properties;


public class MainActivity extends Activity {
    public static boolean isForeground = false;
    private static String lastAlarm = null;
    private static String serverAddress = "http://localhost";

    private static MessageReceiver receiver = null;

    private TextView serverTimeTextView;
    private TextView heartbeatStateTextView;
    private TextView lastHeartbeatTimeTextView;
    private TextView lastAlarmTextView;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        initView();

        registerMessageReceiver(null);

        loadProperties();

        checkAlarm();
    }


    private void initView() {
        serverTimeTextView = (TextView) findViewById(R.id.server_time);
        heartbeatStateTextView = (TextView) findViewById(R.id.heartbeat_state);
        lastHeartbeatTimeTextView = (TextView) findViewById(R.id.last_heartbeat_time);
        lastAlarmTextView = (TextView) findViewById(R.id.last_alarm);
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


    // 检查是否有警报
    private void checkAlarm() {
        new Thread() {
            @Override
            public void run() {
                String html = getHtml();
                String[] tags = html.split("</div><div>");
                int num = tags.length;

                String serverTime = "server time:";
                String heartbeatState = "heartbeat state unknown";
                String lastHeartbeatTime = "last heartbeat time:";
                for (int i = 0; i < num; i++) {
                    if ("alarm history:".equals(tags[i])) {
                        String alarm = tags[i + 1];
                        if (alarm.startsWith("...")) {
                            alarm = "...";
                        }
                        if (!alarm.equals(lastAlarm)) {
                            // new alarm
                            lastAlarm = alarm;
                            sendNotification(MainActivity.this, lastAlarm);
                        }
                    } else if (tags[i].contains("server time:")) {
                        serverTime = "server time:" + tags[i].split("server time:")[1];
                    } else if (tags[i].startsWith("heartbeat state:")) {
                        heartbeatState = tags[i];
                    } else if (tags[i].startsWith("last heartbeat time:")) {
                        lastHeartbeatTime = tags[i];
                    }
                }

                // update UI
                if (isForeground) {
                    updateUi(lastAlarm, serverTime, heartbeatState, lastHeartbeatTime);
                }
            }
        }.start();
    }


    private void updateUi(final String lastAlarm, final String serverTime,
                          final String heartbeatState, final String lastHeartbeatTime) {
        MainActivity.this.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                lastAlarmTextView.setText(lastAlarm);
                serverTimeTextView.setText(serverTime);
                heartbeatStateTextView.setText(heartbeatState);
                lastHeartbeatTimeTextView.setText(lastHeartbeatTime);
            }
        });
    }


    // 发送通知到通知栏
    private static void sendNotification(Context context, final String message) {
        NotificationManager notificationManager = (NotificationManager) context.getSystemService(NOTIFICATION_SERVICE);

        NotificationCompat.Builder builder=  new NotificationCompat.Builder(context);

        builder.setContentTitle("770 alarm")
                .setContentText(message)
                .setPriority(Notification.PRIORITY_HIGH)
                .setWhen(System.currentTimeMillis())
                .setVibrate(new long[] {0, 500, 500, 1500})
                .setSmallIcon(R.drawable.ic_launcher);
        notificationManager.notify(1, builder.build());
    }


    // 读取 html 文本
    private String getHtml() {
        String resultData = "";
        try {
            URL url = new URL(serverAddress);
            HttpURLConnection urlConn = (HttpURLConnection) url.openConnection();

            InputStreamReader in = new InputStreamReader(urlConn.getInputStream());
            BufferedReader buffer = new BufferedReader(in);

            String inputLine;
            while (((inputLine = buffer.readLine()) != null)) {
                resultData += inputLine;
            }

            in.close();
            urlConn.disconnect();
        } catch (Exception ignore) {
            ignore.printStackTrace();
        }
        return resultData;
    }


    @Override
    protected void onResume() {
        isForeground = true;
        super.onResume();
    }


    @Override
    protected void onPause() {
        isForeground = false;
        super.onPause();
    }


    @Override
    protected void onDestroy() {
        unregisterReceiver(receiver);
        super.onDestroy();
    }


    // 注册广播接收
    public void registerMessageReceiver(View view) {
        if (receiver == null) {
            receiver = new MessageReceiver();
        }
        IntentFilter filter = new IntentFilter();
        filter.setPriority(IntentFilter.SYSTEM_HIGH_PRIORITY);
        filter.addAction(Intent.ACTION_TIME_TICK);
        registerReceiver(receiver, filter);
    }

    // 取消广播接收
    public void unregisterMessageReceiver(View view) {
        unregisterReceiver(receiver);
    }


    // 刷新显示
    public void refresh(View view) {
        checkAlarm();
    }


    // 定时检查
    public class MessageReceiver extends BroadcastReceiver {
        @Override
        public void onReceive(Context context, Intent intent) {
            if (Intent.ACTION_TIME_TICK.equals(intent.getAction())) {
                checkAlarm();
            }
        }
    }
}