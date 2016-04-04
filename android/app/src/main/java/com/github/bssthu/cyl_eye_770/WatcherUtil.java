package com.github.bssthu.cyl_eye_770;

import android.app.Notification;
import android.app.NotificationManager;
import android.content.Context;
import android.content.Intent;
import android.support.v4.app.NotificationCompat;
import android.support.v4.content.LocalBroadcastManager;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

/**
 * Created by bss on 2016/4/4.
 */
public class WatcherUtil {
    static String lastAlarm = null;

    // 检查是否有警报
    static void checkAlarm(final Context context) {
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
                            sendNotification(context, lastAlarm);
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
                if (MainActivity.isForeground) {
                    updateUi(context, lastAlarm, serverTime, heartbeatState, lastHeartbeatTime);
                }
            }
        }.start();
    }


    // 发送通知到通知栏
    private static void sendNotification(Context context, final String message) {
        NotificationManager notificationManager = (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);

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
    private static String getHtml() {
        String resultData = "";
        try {
            URL url = new URL(MainApplication.serverAddress);
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


    // 发广播更新 UI
    private static void updateUi(Context context, final String lastAlarm, final String serverTime,
                          final String heartbeatState, final String lastHeartbeatTime) {
        Intent intent = new Intent(MainActivity.ACTION_UPDATE_UI);
        intent.putExtra("lastAlarm", lastAlarm);
        intent.putExtra("serverTime", serverTime);
        intent.putExtra("heartbeatState", heartbeatState);
        intent.putExtra("lastHeartbeatTime", lastHeartbeatTime);
        LocalBroadcastManager.getInstance(context).sendBroadcast(intent);
    }
}
