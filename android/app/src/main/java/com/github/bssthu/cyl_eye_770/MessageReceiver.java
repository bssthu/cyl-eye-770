package com.github.bssthu.cyl_eye_770;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

/**
 * Created by bss on 2016/4/4.
 * 定时检查
 */
public class MessageReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        if (Intent.ACTION_TIME_TICK.equals(intent.getAction())) {
            WatcherUtil.checkAlarm(context);
        }
    }
}
