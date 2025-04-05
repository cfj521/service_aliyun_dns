#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import time
import logging
import requests
from aliyunsdkcore.client import AcsClient
from aliyunsdkalidns.request.v20150109 import UpdateDomainRecordRequest
from aliyunsdkalidns.request.v20150109 import DescribeDomainRecordsRequest
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

class AliyunDNSUpdater:
    def __init__(self):
        self.access_key_id = os.getenv('ALIYUN_ACCESS_KEY_ID')
        self.access_key_secret = os.getenv('ALIYUN_ACCESS_KEY_SECRET')
        self.region_id = os.getenv('ALIYUN_REGION_ID', 'cn-hangzhou')
        self.domain_name = os.getenv('DOMAIN_NAME')
        
        if not all([self.access_key_id, self.access_key_secret, self.domain_name]):
            raise ValueError("请确保设置了所有必要的环境变量")
            
        self.client = AcsClient(
            self.access_key_id,
            self.access_key_secret,
            self.region_id
        )
    
    def get_current_ip(self):
        """获取当前公网IP，使用多个国内API作为备选"""
        ip_apis = [
            {
                'url': 'https://ip.3322.net',
                'method': 'get',
                'parser': lambda r: r.text.strip()
            },
            {
                'url': 'https://myip.ipip.net',
                'method': 'get',
                'parser': lambda r: r.text.strip().split()[0]
            },
            {
                'url': 'https://ip.chinaz.com/getip.aspx',
                'method': 'get',
                'parser': lambda r: json.loads(r.text)['ip']
            }
        ]
        
        for api in ip_apis:
            try:
                if api['method'] == 'get':
                    response = requests.get(api['url'], timeout=5)
                else:
                    response = requests.post(api['url'], timeout=5)
                
                if response.status_code == 200:
                    ip = api['parser'](response)
                    if ip:
                        logger.info(f"成功获取IP地址: {ip}")
                        return ip
            except Exception as e:
                logger.warning(f"从 {api['url']} 获取IP失败: {e}")
                continue
        
        logger.error("所有IP获取API均失败")
        return None
    
    def get_domain_record(self, rr):
        """获取域名记录"""
        request = DescribeDomainRecordsRequest.DescribeDomainRecordsRequest()
        request.set_DomainName(self.domain_name)
        request.set_RRKeyWord(rr)
        request.set_Type('A')
        
        try:
            response = self.client.do_action_with_exception(request)
            records = json.loads(response)
            if records['DomainRecords']['Record']:
                return records['DomainRecords']['Record'][0]
            return None
        except Exception as e:
            logger.error(f"获取域名记录失败: {e}")
            return None
    
    def update_dns_record(self, record_id, rr, ip):
        """更新DNS记录"""
        request = UpdateDomainRecordRequest.UpdateDomainRecordRequest()
        request.set_RecordId(record_id)
        request.set_RR(rr)
        request.set_Type('A')
        request.set_Value(ip)
        
        try:
            response = self.client.do_action_with_exception(request)
            logger.info(f"DNS记录更新成功: {rr}.{self.domain_name} -> {ip}")
            return True
        except Exception as e:
            logger.error(f"DNS记录更新失败: {e}")
            return False
    
    def run(self, subdomains):
        """运行更新程序"""
        current_ip = self.get_current_ip()
        if not current_ip:
            return
        
        for subdomain in subdomains:
            record = self.get_domain_record(subdomain)
            if not record:
                logger.warning(f"未找到子域名记录: {subdomain}")
                continue
            
            if record['Value'] != current_ip:
                self.update_dns_record(record['RecordId'], subdomain, current_ip)
            else:
                logger.info(f"IP地址未变化，无需更新: {subdomain}")

def main():
    # 从环境变量获取子域名列表
    subdomains = os.getenv('SUBDOMAINS', '').split(',')
    if not subdomains or not subdomains[0]:
        logger.error("请设置SUBDOMAINS环境变量，多个子域名用逗号分隔")
        return
    
    updater = AliyunDNSUpdater()
    updater.run(subdomains)

if __name__ == '__main__':
    main() 