# KagiMod for Koken (KM4K)

## How to Use

### Register

```
$ ./Register.sh 
Add User
name> kokenuser
Touch your Suica
Registered (idm:****)
$
```

### Unregister

```
$ ./Unregister.sh 
Delete User
name> kokenuser
Deleted (name:kokenuser)
$
```

### Launch

KM4K.serviceはsystemdに登録されています。

```
systemctl status KM4K
```

で確認

### 環境変数

- `VERIFY_API_URL` : CardManagerのカード認証用エンドポイント
- `API_KEY` : CardManagerのAPI-Key
