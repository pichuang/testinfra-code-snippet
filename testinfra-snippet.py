#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import testinfra

class TestNetworkRules(unittest.TestCase):
    """
    Test that the network rules are working as expected.
    How to run:
        pytest -p no:cacheprovider -v testinfra-snippet.py
    Requirements:
        - pip3 install testinfra
        - pip3 install pytest
    """

    def setUp(self):
        self.host = testinfra.get_host("local://")

    def test_to_azure_managed_dns(self):
        """
        Azure Managed DNS IP is unreachable from Internet, it only works on Azure.
        """
        azure_managed_dns = self.host.addr("168.63.129.16")
        self.assertFalse(azure_managed_dns.is_reachable) # Equal to "ping -W 1 -c 1 168.63.129.16"
        self.assertFalse(azure_managed_dns.port(53).is_reachable) # Equal to "nc -w 1 -z 168.63.129.16 53"
        self.assertFalse(azure_managed_dns.port(80).is_reachable) # Equal to "nc -w 1 -z 168.63.129.16 80"
        self.assertFalse(azure_managed_dns.port(443).is_reachable) # Equal to "nc -w 1 -z 168.63.129.16 443"
        # self.assertTrue(azure_managed_dns.is_resolvable) # Equal to "getent ahosts 168.63.129.16"

    def test_to_google_dns(self):
        """
        Google Public DNS is reachable from Internet.
        """
        google_dns = self.host.addr("8.8.8.8")
        self.assertTrue(google_dns.is_reachable) # Equal to "ping -W 1 -c 1 8.8.8.8"
        self.assertTrue(google_dns.port(53).is_reachable) # Equal to "nc -w 1 -z 8.8.8.8 53"
        self.assertFalse(google_dns.port(80).is_reachable) # Equal to "nc -w 1 -z 8.8.8.8 80"
        self.assertTrue(google_dns.port(443).is_reachable) # Equal to "nc -w 1 -z 8.8.8.8 443"
        # self.assertTrue(google_dns.is_resolvable) # Equal to "getent ahosts 8.8.8.8"

    def test_to_cloudflare_dns(self):
        """
        Cloudflare DNS is reachable from Internet.
        """
        google_dns = self.host.addr("1.1.1.1")
        self.assertTrue(google_dns.is_reachable) # Equal to "ping -W 1 -c 1 1.1.1.1"
        self.assertTrue(google_dns.port(53).is_reachable) # Equal to "nc -w 1 -z 1.1.1.1 53"
        self.assertTrue(google_dns.port(80).is_reachable) # Equal to "nc -w 1 -z 1.1.1.1 80"
        self.assertTrue(google_dns.port(443).is_reachable) # Equal to "nc -w 1 -z 1.1.1.1 443"
        # self.assertTrue(google_dns.is_resolvable) # Equal to "getent ahosts 1.1.1.1"

    def test_non_reachable_ip(self):

        non_reachable_ip = self.host.addr("192.168.0.255")
        self.assertFalse(non_reachable_ip.is_reachable) # Equal to "ping -W 1 -c 1 192.168.0.255"
        self.assertFalse(non_reachable_ip.port(53).is_reachable) # Equal to "nc -w 1 -z 192.168.0.255 53"
        self.assertFalse(non_reachable_ip.port(80).is_reachable) # Equal to "nc -w 1 -z 192.168.0.255 80"
        self.assertFalse(non_reachable_ip.port(443).is_reachable) # Equal to "nc -w 1 -z 192.168.0.255 443"
        # self.assertTrue(non_reachable_ip.is_resolvable) # Equal to "getent ahosts 192.168.0.255"

class TestApplicationRules(unittest.TestCase):

    def setUp(self):
        self.host = testinfra.get_host("local://")

    def test_to_openai_com(self):
        """
        Typical HTTP/HTTPS website is reachable from Internet.
        """
        openai_com = self.host.addr("openai.com")
        self.assertTrue(openai_com.is_reachable) # Equal to "ping -W 1 -c 1 openai.com"
        self.assertTrue(openai_com.port(80).is_reachable) # Equal to "nc -w 1 -z openai.com 80"
        self.assertTrue(openai_com.port(443).is_reachable) # Equal to "nc -w 1 -z openai.com 443"
        self.assertTrue(openai_com.is_resolvable) # Equal to "getent ahosts openai.com"

        openai_http = self.host.run("curl -o /dev/null -s -w %{http_code} https://openai.com")
        self.assertEqual(openai_http.stdout, "200") # Use HTTP Status Code to check if the website is up

    def test_to_azure_ubuntu_repo(self):
        """
        Special HTTP/HTTPS website is reachable from Internet.
        azure.archive.ubuntu.com only support HTTP, not HTTPS.
        """
        azure_ubuntu_repo = self.host.addr("azure.archive.ubuntu.com")
        self.assertFalse(azure_ubuntu_repo.is_reachable) # Equal to "ping -W 1 -c 1 azure.archive.ubuntu.com"
        self.assertTrue(azure_ubuntu_repo.port(80).is_reachable)  # Equal to "nc -w 1 -z azure.archive.ubuntu.com 80"
        self.assertFalse(azure_ubuntu_repo.port(443).is_reachable) # Equal to "nc -w 1 -z azure.archive.ubuntu.com 443"
        self.assertTrue(azure_ubuntu_repo.is_resolvable) # Equal to "getent ahosts azure.archive.ubuntu.com"

        azure_ubuntu_http = self.host.run("curl --connect-timeout 3 -o /dev/null -s -w %{http_code} https://azure.archive.ubuntu.com")
        self.assertNotEqual(azure_ubuntu_http.stdout, "200") # Use HTTP Status Code to check if the website is up

        azure_ubuntu_http = self.host.run("curl --connect-timeout 3 -o /dev/null -s -w %{http_code} http://azure.archive.ubuntu.com")
        self.assertEqual(azure_ubuntu_http.stdout, "200") # Use HTTP Status Code to check if the website is up

    def test_to_non_reachable_http(self):
        """
        Special HTTP/HTTPS website is reachable from Internet.
        azure.archive.ubuntu.com only support HTTP, not HTTPS.
        """
        non_reachable_http = self.host.addr("none.pichuang.com.tw")
        self.assertFalse(non_reachable_http.is_reachable) # Equal to "ping -W 1 -c 1 none.pichuang.com.tw"
        self.assertFalse(non_reachable_http.port(80).is_reachable)  # Equal to "nc -w 1 -z none.pichuang.com.tw 80"
        self.assertFalse(non_reachable_http.port(443).is_reachable) # Equal to "nc -w 1 -z none.pichuang.com.tw 443"
        self.assertFalse(non_reachable_http.is_resolvable) # Equal to "getent ahosts none.pichuang.com.tw"

        azure_ubuntu_http = self.host.run("curl --connect-timeout 3 -o /dev/null -s -w %{http_code} https://none.pichuang.com.tw")
        self.assertNotEqual(azure_ubuntu_http.stdout, "200") # Use HTTP Status Code to check if the website is up

if __name__ == "__main__":
    unittest.main()
