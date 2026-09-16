# StudyLoom / ThreadSpace

Vue 3 + FastAPI 的多人自习室。首次启动自动创建 SQLite 数据库与表，访客身份、专注记录、留言持久化保存。每个浏览器自动分配独立访客身份，同一浏览器多个标签页共用身份；用不同浏览器或无痕窗口验证多人在线。

## 本地开发

```powershell
python -m pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

另开终端：

```powershell
npm ci --prefix frontend
npm run dev --prefix frontend
```

访问 http://localhost:5173。Vite 同时代理 `/api` 和 `/static` 到后端。

## 生产运行

要求 Python 3.11+、Node.js 22.18+（或 24.12+）。在项目根目录运行：

```powershell
python -m pip install -r backend/requirements.txt
npm ci --prefix frontend
npm run build --prefix frontend
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

构建完成后再启动后端，访问服务器的 8000 端口即可使用完整网站。后端同时提供前端构建产物、接口、音乐和字幕。正式域名通过反向代理提供 HTTPS，并将全部请求转发至 8000 端口；使用系统服务或容器保持进程运行。

也可运行 `docker compose up -d --build`，通过 `http://服务器地址:8000` 访问。数据库使用独立持久卷，音乐目录只读挂载；更新代码后重新构建镜像。

### 配置与数据

- `STUDYLOOM_DB`：SQLite 文件路径，默认 `backend/data/studyloom.db`。无需手工建库，必须给进程写入父目录的权限。
- `CORS_ORIGINS`：逗号分隔的前端来源，仅跨域部署需要配置。同域部署无需修改。
- 数据库启用 WAL，备份时使用 SQLite backup API 或停止服务后一起保存数据库及其 WAL 文件。不要使用 `docker compose down -v`，该选项会删除数据卷。
- 当前是单个公共自习室，访客身份存储在浏览器 localStorage；清除浏览器数据会生成新身份。房间面向所有能访问站点的访客开放，尚未实现邀请或登录访问控制。

### 音乐与字幕

将音乐放在 `backend/static` 或其子目录。同名 `.lrc` 自动匹配，例如 `You - vietra.mp3` 与 `You - vietra.lrc`。支持扫描 mp3、flac、ogg、wav、m4a、aac；能否解码取决于浏览器。文件名包含 ` - ` 时，最后一段作为艺术家。

音乐板块提供上一首、加入/暂停收听、下一首和个人音量，不提供选曲或拖动进度。后端随机抽取曲目（曲库不止一首时避免连续同曲），上一首返回历史曲目，下一首重新随机抽取。切歌会同步整个房间，结束后按真实文件时长自动续播。共享曲目、播放历史和起始时间保存在 SQLite，重启后继续依据时间基准播放。浏览器要求首次收听由用户点击“加入收听”触发；暂停只停止自己的声音，重新加入会立即对齐房间进度。

客户端每秒获取共享播放状态，用请求往返时间估算网络延迟；小偏差通过轻微调整播放速率校正，大偏差自动跳到房间进度。切歌传播一般需要 1 秒加网络延迟。每人的音量独立并保存在自己的浏览器，字幕跟随实际音频时间，支持 LRC 多时间标签、毫秒时间与 offset。现有曲库多数为纯音乐，字幕只有“纯音乐，请欣赏”这一行属于正常情况。后端识别音频真实格式和时长，兼容部分扩展名为 flac、实际为 MP3 的现有文件；无法识别时长的文件不进入随机电台。

Minecraft 使用木质唱片机、旋转像素唱片和经验绿进度条；Terraria 使用星夜音乐盒、浮动音符和淡紫进度条。切换主题保持收听状态和音量。

在线列表每 5 秒刷新，25 秒没有心跳则移除。正常离开会主动发送离线请求，后台冻结或异常断网通过超时处理；多标签页离开其中一个后，其他标签页下一次心跳会恢复在线。专注会保留至用户明确结束，刷新后自动恢复，结束时按完整分钟累计，重复结束不会重复计时。

## 验证

```powershell
python -m pip install -r backend/requirements-dev.txt
python -m unittest backend.test_main backend.test_music -v
npm run build --prefix frontend
```

后端测试覆盖首次自动建库、重启持久化、两位真实访客在线与离线、身份校验、专注归属与计时、空留言校验，以及整个曲库音频 Range 分段响应和同名字幕可访问。

共享电台测试覆盖两个访客的统一进度、并发切歌只生效一次、历史回退、自动随机续播、重启恢复、空曲库与单曲库，以及全部音乐的真实时长识别。
