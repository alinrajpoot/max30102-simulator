#!/usr/bin/env python3
"""
Scenario demonstration for MAX30102 Simulator

This script demonstrates different physiological scenarios by
cycling through them and showing the resulting data patterns.
"""

import time
import json
from client_example import MAX30102Client

def run_scenario_demo():
    """Run a demonstration of different scenarios"""
    
    client = MAX30102Client()
    
    if not client.connect():
        return
    
    try:
        # Define demonstration scenarios with durations
        scenarios = [
            ("normal_resting", 10, "Normal resting state"),
            ("walking", 15, "Walking activity"),
            ("running", 15, "Running activity"),
            ("sleeping", 10, "Sleeping state"),
            ("sex_intercourse", 10, "Sexual activity"),
            ("extreme_anxiety", 12, "Panic attack simulation"),
            ("heart_attack", 12, "Heart attack simulation"),
            ("shock", 10, "Medical shock simulation"),
            ("fear", 10, "Acute fear response"),
        ]
        
        print("MAX30102 Simulator Scenario Demonstration")
        print("=" * 60)
        
        for scenario, duration, description in scenarios:
            print(f"\n🎯 Scenario: {scenario}")
            print(f"📝 {description}")
            print(f"⏱️  Running for {duration} seconds...")
            print("-" * 60)
            
            # Set the scenario
            if client.set_scenario(scenario):
                time.sleep(2)  # Wait for scenario to apply
                
                # Receive data for this scenario
                start_time = time.time()
                sample_count = 0
                
                while time.time() - start_time < duration:
                    data_line = client.socket.recv(1024).decode('utf-8').strip()
                    if not data_line:
                        continue
                    
                    try:
                        data = json.loads(data_line)
                        if data.get('type') in [None, 'data']:  # Regular data sample
                            sample_count += 1
                            if sample_count % 20 == 1:  # Show sample every 20th
                                hr = data.get('heart_rate', 0)
                                spo2 = data.get('spO2', 0)
                                red_ppg = data.get('red_ppg', 0)
                                ir_ppg = data.get('ir_ppg', 0)
                                print(f"Sample {sample_count:3d}: HR={hr:5.1f}bpm, SpO2={spo2:4.1f}%, "
                                      f"Red={red_ppg:6d}, IR={ir_ppg:6d}")
                    
                    except json.JSONDecodeError:
                        pass
                
                print(f"✅ Completed: {sample_count} samples received")
            
            time.sleep(1)  # Brief pause between scenarios
        
        print("\n🎉 Scenario demonstration completed!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Demonstration stopped by user")
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
    finally:
        client.disconnect()

if __name__ == "__main__":
    run_scenario_demo()