# 梯子代理自动感应（2026-09-01 添加；被 ~/.bashrc 和 BASH_ENV 共同引用，删除需三处一起清）
# 每个新 shell 启动时读 Windows 系统代理设置：开着且端口活着就自动设代理，否则保持直连
# 注意：此文件绝不能 spawn 新的 bash 子进程（BASH_ENV 会递归加载），探测用纯子 shell 实现
if command -v reg >/dev/null 2>&1; then
  _proxy_enable=$(reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" //v ProxyEnable 2>/dev/null | grep -o "0x[01]" | head -1)
  _proxy_server=$(reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" //v ProxyServer 2>/dev/null | grep ProxyServer | awk '{print $NF}')
  case "$_proxy_server" in
    *=*) _proxy_server=$(echo "$_proxy_server" | tr ';' '\n' | grep -i '^http=' | head -1 | cut -d= -f2-) ;;
  esac
  if [ "$_proxy_enable" = "0x1" ] && [ -n "$_proxy_server" ] \
     && (exec 3<>"/dev/tcp/${_proxy_server%%:*}/${_proxy_server##*:}") 2>/dev/null; then
    export http_proxy="http://$_proxy_server" https_proxy="http://$_proxy_server"
    export HTTP_PROXY="$http_proxy" HTTPS_PROXY="$https_proxy"
    export no_proxy="localhost,127.0.0.1" NO_PROXY="$no_proxy"
  else
    unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
  fi
  unset _proxy_enable _proxy_server
fi
