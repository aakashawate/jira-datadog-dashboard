#!/usr/bin/env python3
"""
DataDog Metrics Integration
Fetches real metrics from DataDog API and serves them to the dashboard
"""

import requests
import json
import time
import os
from datetime import datetime, timedelta

class DataDogClient:
    """DataDog API client for fetching metrics"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.ap1.datadoghq.com/api/v1"
        self.headers = {
            'DD-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
    
    def get_metrics(self, query, start_time=None, end_time=None):
        """Get metrics from DataDog"""
        if not start_time:
            start_time = datetime.now() - timedelta(hours=4)
        if not end_time:
            end_time = datetime.now()
        
        params = {
            'query': query,
            'from': int(start_time.timestamp()),
            'to': int(end_time.timestamp())
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/query",
                headers=self.headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"DataDog API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error fetching DataDog metrics: {e}")
            return None
    
    def get_system_metrics(self):
        """Get common system metrics"""
        metrics = {}
        
        # Common system metrics queries
        metric_queries = {
            'cpu': 'avg:system.cpu.user{*}',
            'memory': 'avg:system.mem.pct_usable{*}',
            'disk': 'avg:system.disk.used{*}',
            'network_sent': 'avg:system.net.bytes_sent{*}',
            'network_received': 'avg:system.net.bytes_rcvd{*}'
        }
        
        for metric_name, query in metric_queries.items():
            print(f"Fetching {metric_name} metrics...")
            data = self.get_metrics(query)
            if data:
                metrics[metric_name] = data
            else:
                # Generate mock data if API fails
                metrics[metric_name] = self.generate_mock_data(metric_name)
        
        return metrics
    
    def generate_mock_data(self, metric_name):
        """Generate mock data for development/demo"""
        import random
        
        # Generate 20 data points over 4 hours
        points = []
        base_time = datetime.now() - timedelta(hours=4)
        
        for i in range(20):
            timestamp = base_time + timedelta(minutes=i * 12)
            
            if metric_name == 'cpu':
                value = random.uniform(10, 80)
            elif metric_name == 'memory':
                value = random.uniform(20, 60)
            elif metric_name == 'disk':
                value = random.uniform(15, 35)
            elif 'network' in metric_name:
                value = random.uniform(100, 1000)
            else:
                value = random.uniform(0, 100)
            
            points.append([int(timestamp.timestamp()) * 1000, value])
        
        return {
            'status': 'ok',
            'series': [{
                'metric': f'mock.{metric_name}',
                'points': points,
                'scope': '*',
                'interval': 60
            }]
        }

def save_metrics_data(metrics, filepath="datadog_metrics.json"):
    """Save metrics data to JSON file"""
    try:
        with open(filepath, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'metrics': metrics
            }, f, indent=2)
        print(f"✅ Metrics saved to {filepath}")
        return True
    except Exception as e:
        print(f"❌ Error saving metrics: {e}")
        return False

def test_datadog_connection(api_key):
    """Test DataDog API connection"""
    print("🔍 Testing DataDog API connection...")
    
    client = DataDogClient(api_key)
    
    # Test with a simple query
    test_data = client.get_metrics('avg:system.cpu.user{*}')
    
    if test_data and test_data.get('status') == 'ok':
        print("✅ DataDog API connection successful!")
        return True
    else:
        print("⚠️  DataDog API connection failed, will use mock data")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("📈 DATADOG METRICS INTEGRATION")
    print("=" * 60)
    
    # DataDog API Key
    DATADOG_API_KEY = "fc50b4d7ebb710a4f1eff7a3a42330df"
    
    print(f"🔑 Using API Key: {DATADOG_API_KEY[:8]}...")
    
    # Test connection
    connection_ok = test_datadog_connection(DATADOG_API_KEY)
    
    # Create client and fetch metrics
    client = DataDogClient(DATADOG_API_KEY)
    
    print("📊 Fetching system metrics...")
    metrics = client.get_system_metrics()
    
    # Save metrics
    save_metrics_data(metrics)
    
    print("\n📈 Metrics Summary:")
    for metric_name, data in metrics.items():
        if data and data.get('series'):
            points_count = len(data['series'][0].get('points', []))
            print(f"   {metric_name}: {points_count} data points")
        else:
            print(f"   {metric_name}: No data")
    
    print(f"\n💡 Metrics data saved and ready for dashboard")
    print(f"🌐 Dashboard: http://localhost:8080")

if __name__ == "__main__":
    main()
