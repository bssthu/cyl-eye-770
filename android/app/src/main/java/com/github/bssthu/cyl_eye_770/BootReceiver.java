package com.github.bssthu.cyl_eye_770;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

/**
 * Created by bss on 2016/4/4.
 * 自启动
 */
public class BootReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        WatcherService.restartService(context);
    }
}
