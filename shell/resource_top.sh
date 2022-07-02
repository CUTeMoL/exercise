#!/bin/bash
read -p "请输入c|cpu or m|mem|memory:  " ps_sort_format
case $ps_sort_format in
    m|mem|memory)
        echo "....................................memory top10......................................."
        ps -eo pid,pcpu,pmem,stat,cmd --sort=pmem |tail -n10|sort -nr -k2
        ;;
    c|cpu)
        echo "......................................cpu top10........................................."
        ps -eo pid,pcpu,pmem,stat,cmd --sort=pcpu |tail -n10|sort -nr -k2
        ;;
    *)
        echo "please input c|cpu or m|mem|memory"
        ;;
esac