package com.github.bssthu.cyl_eye_770;

import android.app.Notification;
import android.app.NotificationManager;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.os.Binder;
import android.os.IBinder;
import android.os.PowerManager;
import android.preference.PreferenceManager;
import android.support.v4.app.NotificationCompat;

public class WatcherService extends Service {
    private static final String keepAliveKey = "keep_alive";

    private Context context;
    private MessageReceiver receiver = null;
    private PowerManager.WakeLock wakeLock = null;

    // service 是否保持运行
    public static boolean keepAlive(Context context) {
        SharedPreferences preferences = PreferenceManager.getDefaultSharedPreferences(context);
        return preferences.getBoolean(keepAliveKey, true);
    }

    public static void setKeepAlive(Context context, boolean keepAlive) {
        SharedPreferences.Editor editor = PreferenceManager.getDefaultSharedPreferences(context).edit();
        editor.putBoolean(keepAliveKey, keepAlive);
        editor.apply();
    }

    public static void restartService(Context context) {
        if (keepAlive(context)) {
            Intent intent = new Intent(context, WatcherService.class);
            context.startService(intent);
        }
    }

    public WatcherService() {
        context = this;
    }

    public class ServiceBinder extends Binder {
        public WatcherService getService() {
            return WatcherService.this;
        }
    }

    @Override
    public IBinder onBind(Intent intent) {
        return new ServiceBinder();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        // receiver
        registerMessageReceiver(context);

        // keep foreground
        NotificationManager notificationManager = (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
        NotificationCompat.Builder builder=  new NotificationCompat.Builder(context);
        builder.setContentTitle("770 watcher")
                .setContentText("alarm system running...")
                .setOngoing(true)
                .setPriority(Notification.PRIORITY_HIGH)
                .setWhen(System.currentTimeMillis())
                .setSmallIcon(R.drawable.ic_launcher);
        final Notification notification = builder.build();
        notificationManager.notify(1, notification);
        startForeground(1, notification);

        // wakelock
        PowerManager powerManager = (PowerManager) getSystemService(POWER_SERVICE);
        wakeLock = powerManager.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "WatcherService");
        wakeLock.acquire();

        // start sticky
        flags = START_STICKY;
        return super.onStartCommand(intent, flags, startId);
    }

    // 注册广播接收
    public void registerMessageReceiver(final Context context) {
        if (receiver == null) {
            receiver = new MessageReceiver();
        }
        unregisterMessageReceiver(context);

        IntentFilter filter = new IntentFilter();
        filter.setPriority(IntentFilter.SYSTEM_HIGH_PRIORITY);      // 设定最高优先级，慎用
        filter.addAction(Intent.ACTION_TIME_TICK);
        context.registerReceiver(receiver, filter);
    }

    // 取消广播接收
    public void unregisterMessageReceiver(final Context context) {
        try {
            context.unregisterReceiver(receiver);
        } catch (IllegalArgumentException ignore) { }
    }

    @Override
    public void onDestroy() {
        stopForeground(true);
        wakeLock.release();

        // send broadcast to restart
        if (keepAlive(context)) {
            Intent intent = new Intent("com.github.bssthu.cyl_eye_770.restart_service");
            sendBroadcast(intent);
        }

        super.onDestroy();
    }
}
