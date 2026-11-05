#!/bin/bash
# Folosire: gpu.sh name|util|temp|mem   (NVIDIA, AMD sau Intel)
q="$1"

if command -v nvidia-smi >/dev/null 2>&1; then
    case "$q" in
        name) nvidia-smi --query-gpu=name --format=csv,noheader | head -1 ;;
        util) nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits | head -1 ;;
        temp) nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits | head -1 ;;
        mem)  nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits | head -1 | awk -F', ' '{printf "%s / %s MiB", $1, $2}' ;;
    esac
    exit 0
fi

# AMD (driver amdgpu) - citește din sysfs
card=$(ls -d /sys/class/drm/card?/device 2>/dev/null | while read d; do
    [ "$(cat $d/vendor 2>/dev/null)" = "0x1002" ] && echo "$d" && break; done)
if [ -n "$card" ]; then
    case "$q" in
        name) echo "AMD GPU" ;;
        util) cat "$card/gpu_busy_percent" 2>/dev/null || echo 0 ;;
        temp) t=$(cat $card/hwmon/hwmon*/temp1_input 2>/dev/null | head -1); echo $(( ${t:-0} / 1000 )) ;;
        mem)  u=$(cat $card/mem_info_vram_used 2>/dev/null); m=$(cat $card/mem_info_vram_total 2>/dev/null)
              echo "$(( ${u:-0} / 1048576 )) / $(( ${m:-0} / 1048576 )) MiB" ;;
    esac
    exit 0
fi

# Intel / necunoscut
case "$q" in
    name) echo "Intel/integrat" ;;
    *) echo "n/a" ;;
esac
