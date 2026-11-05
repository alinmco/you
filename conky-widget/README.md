# Widget Conky + Lua pentru Linux Mint

Arată CPU, RAM, GPU, disk și rețea (stil Task Manager), cu inele desenate în Lua/Cairo.

## Instalare

```bash
sudo apt install conky-all lm-sensors
mkdir -p ~/.config/conky
cp conky.conf rings.lua gpu.sh ~/.config/conky/
chmod +x ~/.config/conky/gpu.sh
conky -c ~/.config/conky/conky.conf
```

## Configurare (obligatoriu)

1. **Interfața de rețea**: `ip -br link`, apoi schimbă `template1` în `conky.conf`
   (ex. `wlp2s0` pentru Wi-Fi, `enp3s0` pentru cablu).
2. **Temperatura CPU**: `${hwmon 1 temp 1}` depinde de sistem. Rulează `sensors-detect`,
   apoi `ls /sys/class/hwmon/*/name` și găsește `coretemp` (Intel) sau `k10temp` (AMD);
   pune indexul lui în `hwmon N temp 1`.
3. **Discuri**: schimbă `/home` dacă nu e partiție separată (sau șterge liniile).
4. **GPU**: NVIDIA merge cu `nvidia-smi`, AMD prin sysfs, Intel afișează doar „n/a”.

## Pornire automată

*Meniu → Startup Applications → Add*:
`bash -c "sleep 5 && conky -c ~/.config/conky/conky.conf"`

## Probleme frecvente
- Nu apare nimic / eroare Lua: rulează `conky -c ~/.config/conky/conky.conf` în terminal și citește erorile.
- Fundal negru: asigură-te că ai compozitor activ (Cinnamon îl are implicit) și `own_window_argb_visual = true`.
- Inelele nu se aliniază cu textul: ajustează `x`, `y` din `rings.lua` și `voffset` din `conky.conf`.
