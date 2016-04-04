package com.github.bssthu.cyl_eye_770;

import android.app.Activity;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Bundle;
import android.support.v4.content.LocalBroadcastManager;
import android.view.View;
import android.widget.TextView;

public class MainActivity extends Activity {
    public static final String ACTION_UPDATE_UI = "com.github.bssthu.cyl_eye_770.UPDATE_UI";

    public static boolean isForeground = false;

    private Context context;

    private TextView serverTimeTextView;
    private TextView heartbeatStateTextView;
    private TextView lastHeartbeatTimeTextView;
    private TextView lastAlarmTextView;


    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        context = MainActivity.this;
        initView();
    }


    @Override
    protected void onResume() {
        isForeground = true;
        super.onResume();

        // ui broadcast
        IntentFilter filter = new IntentFilter();
        filter.addAction(ACTION_UPDATE_UI);
        LocalBroadcastManager.getInstance(context).registerReceiver(uiReceiver, filter);
    }


    @Override
    protected void onPause() {
        LocalBroadcastManager.getInstance(context).unregisterReceiver(uiReceiver);

        isForeground = false;
        super.onPause();
    }


    @Override
    protected void onDestroy() {
        super.onDestroy();
    }


    private void initView() {
        serverTimeTextView = (TextView) findViewById(R.id.server_time);
        heartbeatStateTextView = (TextView) findViewById(R.id.heartbeat_state);
        lastHeartbeatTimeTextView = (TextView) findViewById(R.id.last_heartbeat_time);
        lastAlarmTextView = (TextView) findViewById(R.id.last_alarm);
    }


    private void updateUi(final String lastAlarm, final String serverTime,
                          final String heartbeatState, final String lastHeartbeatTime) {
        MainActivity.this.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                if (lastAlarm != null) {
                    lastAlarmTextView.setText(lastAlarm);
                }
                if (serverTime != null) {
                    serverTimeTextView.setText(serverTime);
                }
                if (heartbeatState != null) {
                    heartbeatStateTextView.setText(heartbeatState);
                }
                if (lastHeartbeatTime != null) {
                    lastHeartbeatTimeTextView.setText(lastHeartbeatTime);
                }
            }
        });
    }


    // 注册广播接收
    public void registerMessageReceiver(View view) {
        MainApplication.registerMessageReceiver(context);
    }

    // 取消广播接收
    public void unregisterMessageReceiver(View view) {
        MainApplication.unregisterMessageReceiver(context);
    }


    // 刷新显示
    public void refresh(View view) {
        WatcherUtil.checkAlarm(context);
    }


    private UiReceiver uiReceiver = new UiReceiver();

    // 修改 UI 显示的广播接收器
    public class UiReceiver extends BroadcastReceiver {
        @Override
        public void onReceive(Context context, Intent intent) {
            if (ACTION_UPDATE_UI.equals(intent.getAction())) {
                String lastAlarm = intent.getStringExtra("lastAlarm");
                String serverTime = intent.getStringExtra("serverTime");
                String heartbeatState = intent.getStringExtra("heartbeatState");
                String lastHeartbeatTime = intent.getStringExtra("lastHeartbeatTime");

                updateUi(lastAlarm, serverTime, heartbeatState, lastHeartbeatTime);
            }
        }
    }
}