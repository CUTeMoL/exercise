
# Arthas

### 一、文档链接

```shell
https://arthas.aliyun.com/doc/quick-start.html
```

### 导出火焰图

```shell
java_pid=84634
output_file='/tmp/profile_84634.md'
java -jar arthas-boot.jar ${java_pid} -c "profiler start -d 30 ; sleep 31 ; profiler stop --format md --file ${output_file}"
sleep 31
if [ -e "${output_file}" ]; then
    echo "[success] Export to ${output_file}"
else
    echo "[failed] Failed to generate profiler report"
fi
```