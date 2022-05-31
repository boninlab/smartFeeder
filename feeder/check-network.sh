#!/bin/bash

CHECK_IP=168.126.63.1
( ! ping -c1 $CHECK_IP >/dev/null 2>&1 ) && service network-manager restart >/dev/null 2>&1
