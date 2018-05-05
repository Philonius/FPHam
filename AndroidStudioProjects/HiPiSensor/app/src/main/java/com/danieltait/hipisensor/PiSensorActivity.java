package com.danieltait.hipisensor;

import android.bluetooth.BluetoothDevice;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;

public class PiSensorActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_pi_sensor);

        // Recieve the btdevice passed to activity
        BluetoothDevice PiDevice = getIntent().getExtras().getPa
    }
}
