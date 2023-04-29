# KagiMod for Koken ver.2 (KM4K2)

KagiMod for Kokenを元にして認証機能を切り離してたものです。

### Launch

KM4K.serviceはsystemdに登録されています。

```
systemctl status KM4K2
```

で確認

### 環境変数

- `VERIFY_API_URL` : CardManagerのカード認証用エンドポイント
- `API_KEY` : CardManagerのAPI-Key
- `REDIS_HOST` : Redisサーバーのホスト名
- `REDIS_PORT` : Redisサーバーのポート番号
- `REDIS_DB` : RedisサーバーのDB番号
