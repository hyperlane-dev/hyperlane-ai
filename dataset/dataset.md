# Path: hyperlane-utils/README.md
## hyperlane-utils
[Official Documentation](https://docs.ltpp.vip/hyperlane-utils/)
[Api Docs](https://docs.rs/hyperlane-utils/latest/hyperlane_utils/)
> A library providing utils for hyperlane.
## Installation
To use this crate, you can run cmd:
```shell
cargo add hyperlane-utils
```
## Contact
# Path: hyperlane-utils/src/lib.rs
```rust
pub use bin_encode_decode::*;
pub use chunkify::*;
pub use clonelicious::*;
pub use color_output::*;
pub use compare_version::*;
pub use file_operation::*;
pub use future_fn::*;
pub use hot_restart::*;
pub use http_request::*;
pub use hyperlane_broadcast::*;
pub use hyperlane_log::*;
pub use hyperlane_macros::*;
pub use hyperlane_plugin_websocket::*;
pub use lombok_macros::*;
pub use recoverable_spawn::*;
pub use recoverable_thread_pool::*;
pub use server_manager::*;
pub use std_macro_extensions::*;
pub use ahash;
pub use bytemuck_derive;
pub use chrono;
pub use dotenvy;
pub use futures;
pub use hex;
pub use log;
pub use num_cpus;
pub use once_cell;
pub use redis;
pub use regex;
pub use sea_orm;
pub use serde;
pub use serde_urlencoded;
pub use serde_with;
pub use serde_xml_rs;
pub use serde_yaml;
pub use simd_json;
pub use snafu;
pub use sqlx;
pub use twox_hash;
pub use url;
pub use urlencoding;
pub use utoipa;
pub use utoipa_rapidoc;
pub use utoipa_swagger_ui;
pub use uuid;
```
# Path: hyperlane-broadcast/README.md
## hyperlane-broadcast
[Official Documentation](https://docs.ltpp.vip/hyperlane-broadcast/)
[Api Docs](https://docs.rs/hyperlane-broadcast/latest/hyperlane_broadcast/)
> hyperlane-broadcast is a lightweight and ergonomic wrapper over Tokio’s broadcast channel designed for easy-to-use publish-subscribe messaging in async Rust applications. It simplifies the native Tokio broadcast API by providing a straightforward interface for broadcasting messages to multiple subscribers with minimal boilerplate.
## Installation
To use this crate, you can run cmd:
```shell
cargo add hyperlane-broadcast
```
## Contact
# Path: hyperlane-broadcast/src/lib.rs
```rust
pub(crate) mod broadcast;
pub(crate) mod broadcast_map;
pub(crate) mod cfg;
pub use broadcast::{r#const::*, r#struct::*, r#trait::*, r#type::*};
pub use broadcast_map::{r#struct::*, r#trait::*, r#type::*};
pub(crate) use std::{fmt::Debug, hash::BuildHasherDefault};
pub(crate) use dashmap::*;
pub(crate) use tokio::sync::broadcast::{
    error::SendError,
    {Receiver, Sender},
};
pub(crate) use twox_hash::XxHash3_64;
```
# Path: hyperlane-broadcast/src/cfg.rs
```rust
#[tokio::test]
pub async fn test_broadcast() {
    use crate::*;
    let broadcast: Broadcast<usize> = Broadcast::new(10);
    let mut rec1: BroadcastReceiver<usize> = broadcast.subscribe();
    let mut rec2: BroadcastReceiver<usize> = broadcast.subscribe();
    broadcast.send(20).unwrap();
    assert_eq!(rec1.recv().await, Ok(20));
    assert_eq!(rec2.recv().await, Ok(20));
}
#[tokio::test]
pub async fn test_broadcast_map() {
    use crate::*;
    let broadcast_map: BroadcastMap<usize> = BroadcastMap::new();
    broadcast_map.insert("a", 10);
    let mut rec1: BroadcastMapReceiver<usize> = broadcast_map.subscribe("a").unwrap();
    let mut rec2: BroadcastMapReceiver<usize> = broadcast_map.subscribe("a").unwrap();
    let mut rec3: BroadcastMapReceiver<usize> =
        broadcast_map.subscribe_or_insert("b", DEFAULT_BROADCAST_SENDER_CAPACITY);
    broadcast_map.send("a", 20).unwrap();
    broadcast_map.send("b", 10).unwrap();
    assert_eq!(rec1.recv().await, Ok(20));
    assert_eq!(rec2.recv().await, Ok(20));
    assert_eq!(rec3.recv().await, Ok(10));
}
```
# Path: hyperlane-broadcast/src/broadcast/trait.rs
```rust
use crate::*;
pub trait BroadcastTrait: Clone + Debug {}
```
# Path: hyperlane-broadcast/src/broadcast/const.rs
```rust
pub const DEFAULT_BROADCAST_SENDER_CAPACITY: usize = 1024;
```
# Path: hyperlane-broadcast/src/broadcast/mod.rs
```rust
pub mod r#const;
pub mod r#impl;
pub mod r#struct;
pub mod r#trait;
pub mod r#type;
```
# Path: hyperlane-broadcast/src/broadcast/struct.rs
```rust
use crate::*;
#[derive(Debug, Clone)]
pub struct Broadcast<T: BroadcastTrait>(pub(super) BroadcastSender<T>);
```
# Path: hyperlane-broadcast/src/broadcast/impl.rs
```rust
use crate::*;
impl<T: Clone + Debug> BroadcastTrait for T {}
impl<T: BroadcastTrait> Default for Broadcast<T> {
    #[inline(always)]
    fn default() -> Self {
        let sender: BroadcastSender<T> = BroadcastSender::new(DEFAULT_BROADCAST_SENDER_CAPACITY);
        Self(sender)
    }
}
impl<T: BroadcastTrait> Broadcast<T> {
    #[inline(always)]
    pub fn new(capacity: Capacity) -> Self {
        let sender: BroadcastSender<T> = BroadcastSender::new(capacity);
        Self(sender)
    }
    #[inline(always)]
    pub fn receiver_count(&self) -> ReceiverCount {
        self.0.receiver_count()
    }
    #[inline(always)]
    pub fn subscribe(&self) -> BroadcastReceiver<T> {
        self.0.subscribe()
    }
    #[inline(always)]
    pub fn send(&self, data: T) -> BroadcastSendResult<T> {
        self.0.send(data)
    }
}
```
# Path: hyperlane-broadcast/src/broadcast/type.rs
```rust
use crate::*;
pub type ReceiverCount = usize;
pub type BroadcastSendError<T> = SendError<T>;
pub type BroadcastSendResult<T> = Result<ReceiverCount, BroadcastSendError<T>>;
pub type BroadcastReceiver<T> = Receiver<T>;
pub type BroadcastSender<T> = Sender<T>;
pub type Capacity = usize;
```
# Path: hyperlane-broadcast/src/broadcast_map/trait.rs
```rust
use crate::*;
pub trait BroadcastMapTrait: Clone + Debug {}
```
# Path: hyperlane-broadcast/src/broadcast_map/mod.rs
```rust
pub mod r#impl;
pub mod r#struct;
pub mod r#trait;
pub mod r#type;
```
# Path: hyperlane-broadcast/src/broadcast_map/struct.rs
```rust
use crate::*;
#[derive(Debug, Clone)]
pub struct BroadcastMap<T: BroadcastTrait>(pub(super) DashMapStringBroadcast<T>);
```
# Path: hyperlane-broadcast/src/broadcast_map/impl.rs
```rust
use crate::*;
impl<T: Clone + Debug> BroadcastMapTrait for T {}
impl<T: BroadcastMapTrait> Default for BroadcastMap<T> {
    #[inline(always)]
    fn default() -> Self {
        Self(DashMap::with_hasher(BuildHasherDefault::default()))
    }
}
impl<T: BroadcastMapTrait> BroadcastMap<T> {
    #[inline(always)]
    pub fn new() -> Self {
        Self::default()
    }
    #[inline(always)]
    fn get(&self) -> &DashMapStringBroadcast<T> {
        &self.0
    }
    #[inline(always)]
    pub fn insert<K>(&self, key: K, capacity: Capacity) -> OptionBroadcast<T>
    where
        K: AsRef<str>,
    {
        let broadcast: Broadcast<T> = Broadcast::new(capacity);
        self.get().insert(key.as_ref().to_owned(), broadcast)
    }
    #[inline(always)]
    pub fn receiver_count<K>(&self, key: K) -> OptionReceiverCount
    where
        K: AsRef<str>,
    {
        self.get()
            .get(key.as_ref())
            .map(|receiver| receiver.receiver_count())
    }
    #[inline(always)]
    pub fn subscribe<K>(&self, key: K) -> OptionBroadcastMapReceiver<T>
    where
        K: AsRef<str>,
    {
        self.get()
            .get(key.as_ref())
            .map(|receiver| receiver.subscribe())
    }
    #[inline(always)]
    pub fn subscribe_or_insert<K>(&self, key: K, capacity: Capacity) -> BroadcastMapReceiver<T>
    where
        K: AsRef<str>,
    {
        let key_ref: &str = key.as_ref();
        match self.get().get(key_ref) {
            Some(sender) => sender.subscribe(),
            None => {
                self.insert(key_ref, capacity);
                self.subscribe_or_insert(key_ref, capacity)
            }
        }
    }
    #[inline(always)]
    pub fn send<K: AsRef<str>>(&self, key: K, data: T) -> BroadcastMapSendResult<T> {
        match self.get().get(key.as_ref()) {
            Some(sender) => sender.send(data).map(Some),
            None => Ok(None),
        }
    }
}
```
# Path: hyperlane-broadcast/src/broadcast_map/type.rs
```rust
use crate::*;
pub type BroadcastMapSendError<T> = SendError<T>;
pub type BroadcastMapSendResult<T> = Result<Option<ReceiverCount>, BroadcastMapSendError<T>>;
pub type BroadcastMapReceiver<T> = Receiver<T>;
pub type OptionBroadcast<T> = Option<Broadcast<T>>;
pub type OptionBroadcastMapReceiver<T> = Option<BroadcastMapReceiver<T>>;
pub type BroadcastMapSender<T> = Sender<T>;
pub type OptionBroadcastMapSender<T> = Option<BroadcastMapSender<T>>;
pub type OptionReceiverCount = Option<ReceiverCount>;
pub type DashMapStringBroadcast<T> = DashMap<String, Broadcast<T>, BuildHasherDefault<XxHash3_64>>;
```
# Path: hyperlane-plugin-websocket/README.md
## hyperlane-plugin-websocket
[Official Documentation](https://docs.ltpp.vip/hyperlane-plugin-websocket/)
[Api Docs](https://docs.rs/hyperlane-plugin-websocket/latest/http_type/)
> A WebSocket plugin for the Hyperlane framework, providing robust WebSocket communication capabilities and integrating with hyperlane-broadcast for efficient message dissemination.
## Installation
To use this crate, you can run cmd:
```shell
cargo add hyperlane-plugin-websocket
```
## Contact
# Path: hyperlane-plugin-websocket/src/lib.rs
```rust
#[cfg(test)]
pub(crate) mod tests;
pub(crate) mod websocket;
pub use websocket::{r#enum::*, r#struct::*};
pub(crate) use websocket::{r#const::*, r#trait::*};
pub(crate) use std::{
    convert::Infallible,
    net::{IpAddr, Ipv4Addr, Ipv6Addr, SocketAddr},
    num::{
        NonZeroI8, NonZeroI16, NonZeroI32, NonZeroI64, NonZeroI128, NonZeroIsize, NonZeroU8,
        NonZeroU16, NonZeroU32, NonZeroU64, NonZeroU128, NonZeroUsize,
    },
    sync::Arc,
};
pub(crate) use hyperlane::{tokio::sync::broadcast::Receiver, *};
pub(crate) use hyperlane_broadcast::*;
#[cfg(test)]
pub(crate) use std::sync::OnceLock;
```
# Path: hyperlane-plugin-websocket/src/tests/mod.rs
```rust
mod cfg;
```
# Path: hyperlane-plugin-websocket/src/tests/cfg.rs
```rust
use crate::*;
static BROADCAST_MAP: OnceLock<WebSocket> = OnceLock::new();
fn get_broadcast_map() -> &'static WebSocket {
    BROADCAST_MAP.get_or_init(WebSocket::new)
}
struct TaskPanicHook {
    response_body: String,
    content_type: String,
}
impl ServerHook for TaskPanicHook {
    async fn new(ctx: &Context) -> Self {
        let error: PanicData = ctx.try_get_task_panic_data().await.unwrap_or_default();
        let response_body: String = error.to_string();
        let content_type: String = ContentType::format_content_type_with_charset(TEXT_PLAIN, UTF8);
        Self {
            response_body,
            content_type,
        }
    }
    async fn handle(self, ctx: &Context) {
        ctx.set_response_version(HttpVersion::Http1_1)
            .await
            .set_response_status_code(500)
            .await
            .clear_response_headers()
            .await
            .set_response_header(SERVER, HYPERLANE)
            .await
            .set_response_header(CONTENT_TYPE, &self.content_type)
            .await
            .set_response_body(&self.response_body)
            .await
            .send()
            .await;
    }
}
struct RequestErrorHook {
    response_status_code: ResponseStatusCode,
    response_body: String,
}
impl ServerHook for RequestErrorHook {
    async fn new(ctx: &Context) -> Self {
        let request_error: RequestError =
            ctx.try_get_request_error_data().await.unwrap_or_default();
        Self {
            response_status_code: request_error.get_http_status_code(),
            response_body: request_error.to_string(),
        }
    }
    async fn handle(self, ctx: &Context) {
        ctx.set_response_version(HttpVersion::Http1_1)
            .await
            .set_response_status_code(self.response_status_code)
            .await
            .set_response_body(self.response_body)
            .await
            .send()
            .await;
    }
}
struct RequestMiddleware {
    socket_addr: String,
}
impl ServerHook for RequestMiddleware {
    async fn new(ctx: &Context) -> Self {
        let socket_addr: String = ctx.get_socket_addr_string().await;
        Self { socket_addr }
    }
    async fn handle(self, ctx: &Context) {
        ctx.set_response_version(HttpVersion::Http1_1)
            .await
            .set_response_status_code(200)
            .await
            .set_response_header(SERVER, HYPERLANE)
            .await
            .set_response_header(CONNECTION, KEEP_ALIVE)
            .await
            .set_response_header(CONTENT_TYPE, TEXT_PLAIN)
            .await
            .set_response_header(ACCESS_CONTROL_ALLOW_ORIGIN, WILDCARD_ANY)
            .await
            .set_response_header("SocketAddr", &self.socket_addr)
            .await;
    }
}
struct UpgradeHook;
impl ServerHook for UpgradeHook {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &Context) {
        if !ctx.get_request().await.is_ws() {
            return;
        }
        if let Some(key) = &ctx.try_get_request_header_back(SEC_WEBSOCKET_KEY).await {
            let accept_key: String = WebSocketFrame::generate_accept_key(key);
            ctx.set_response_version(HttpVersion::Http1_1)
                .await
                .set_response_status_code(101)
                .await
                .set_response_header(UPGRADE, WEBSOCKET)
                .await
                .set_response_header(CONNECTION, UPGRADE)
                .await
                .set_response_header(SEC_WEBSOCKET_ACCEPT, &accept_key)
                .await
                .set_response_body(&vec![])
                .await
                .send()
                .await;
        }
    }
}
struct ConnectedHook {
    receiver_count: ReceiverCount,
    data: String,
    group_broadcast_type: BroadcastType<String>,
    private_broadcast_type: BroadcastType<String>,
}
impl ServerHook for ConnectedHook {
    async fn new(ctx: &Context) -> Self {
        let group_name: String = ctx
            .try_get_route_param("group_name")
            .await
            .unwrap_or_default();
        let group_broadcast_type: BroadcastType<String> = BroadcastType::PointToGroup(group_name);
        let receiver_count: ReceiverCount =
            get_broadcast_map().receiver_count(group_broadcast_type.clone());
        let my_name: String = ctx.try_get_route_param("my_name").await.unwrap_or_default();
        let your_name: String = ctx
            .try_get_route_param("your_name")
            .await
            .unwrap_or_default();
        let private_broadcast_type: BroadcastType<String> =
            BroadcastType::PointToPoint(my_name, your_name);
        let data: String = format!("receiver_count => {receiver_count:?}");
        Self {
            receiver_count,
            data,
            group_broadcast_type,
            private_broadcast_type,
        }
    }
    async fn handle(self, _ctx: &Context) {
        get_broadcast_map()
            .send(self.group_broadcast_type, self.data.clone())
            .unwrap_or_else(|err| {
                println!("[connected_hook]send group error => {:?}", err.to_string());
                None
            });
        get_broadcast_map()
            .send(self.private_broadcast_type, self.data)
            .unwrap_or_else(|err| {
                println!(
                    "[connected_hook]send private error => {:?}",
                    err.to_string()
                );
                None
            });
        println!(
            "[connected_hook]receiver_count => {:?}",
            self.receiver_count
        );
        Server::flush_stdout();
    }
}
struct SendedHook {
    msg: String,
}
impl ServerHook for SendedHook {
    async fn new(ctx: &Context) -> Self {
        let msg: String = ctx.get_response_body_string().await;
        Self { msg }
    }
    async fn handle(self, _ctx: &Context) {
        println!("[sended_hook]msg => {}", self.msg);
        Server::flush_stdout();
    }
}
struct GroupChatRequestHook {
    body: RequestBody,
    receiver_count: ReceiverCount,
}
impl ServerHook for GroupChatRequestHook {
    async fn new(ctx: &Context) -> Self {
        let group_name: String = ctx.try_get_route_param("group_name").await.unwrap();
        let key: BroadcastType<String> = BroadcastType::PointToGroup(group_name);
        let mut receiver_count: ReceiverCount = get_broadcast_map().receiver_count(key.clone());
        let mut body: RequestBody = ctx.get_request_body().await;
        if body.is_empty() {
            receiver_count = get_broadcast_map().receiver_count_after_closed(key);
            body = format!("receiver_count => {receiver_count:?}").into();
        }
        Self {
            body,
            receiver_count,
        }
    }
    async fn handle(self, ctx: &Context) {
        ctx.set_response_body(&self.body).await;
        println!("[group_chat]receiver_count => {:?}", self.receiver_count);
        Server::flush_stdout();
    }
}
struct GroupClosedHook {
    body: String,
    receiver_count: ReceiverCount,
}
impl ServerHook for GroupClosedHook {
    async fn new(ctx: &Context) -> Self {
        let group_name: String = ctx.try_get_route_param("group_name").await.unwrap();
        let key: BroadcastType<String> = BroadcastType::PointToGroup(group_name);
        let receiver_count: ReceiverCount =
            get_broadcast_map().receiver_count_after_closed(key.clone());
        let body: String = format!("receiver_count => {receiver_count:?}");
        Self {
            body,
            receiver_count,
        }
    }
    async fn handle(self, ctx: &Context) {
        ctx.set_response_body(&self.body).await;
        println!("[group_closed]receiver_count => {:?}", self.receiver_count);
        Server::flush_stdout();
    }
}
struct GroupChat;
impl ServerHook for GroupChat {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &Context) {
        let group_name: String = ctx.try_get_route_param("group_name").await.unwrap();
        let key: BroadcastType<String> = BroadcastType::PointToGroup(group_name);
        let config: WebSocketConfig<String> = WebSocketConfig::new()
            .set_context(ctx.clone())
            .set_broadcast_type(key)
            .set_request_config(RequestConfig::default())
            .set_capacity(1024)
            .set_connected_hook::<ConnectedHook>()
            .set_request_hook::<GroupChatRequestHook>()
            .set_sended_hook::<SendedHook>()
            .set_closed_hook::<GroupClosedHook>();
        get_broadcast_map().run(config).await;
    }
}
struct PrivateChatRequestHook {
    body: RequestBody,
    receiver_count: ReceiverCount,
}
impl ServerHook for PrivateChatRequestHook {
    async fn new(ctx: &Context) -> Self {
        let my_name: String = ctx.try_get_route_param("my_name").await.unwrap();
        let your_name: String = ctx.try_get_route_param("your_name").await.unwrap();
        let key: BroadcastType<String> = BroadcastType::PointToPoint(my_name, your_name);
        let mut receiver_count: ReceiverCount = get_broadcast_map().receiver_count(key.clone());
        let mut body: RequestBody = ctx.get_request_body().await;
        if body.is_empty() {
            receiver_count = get_broadcast_map().receiver_count_after_closed(key);
            body = format!("receiver_count => {receiver_count:?}").into();
        }
        Self {
            body,
            receiver_count,
        }
    }
    async fn handle(self, ctx: &Context) {
        ctx.set_response_body(&self.body).await;
        println!("[private_chat]receiver_count => {:?}", self.receiver_count);
        Server::flush_stdout();
    }
}
struct PrivateClosedHook {
    body: String,
    receiver_count: ReceiverCount,
}
impl ServerHook for PrivateClosedHook {
    async fn new(ctx: &Context) -> Self {
        let my_name: String = ctx.try_get_route_param("my_name").await.unwrap();
        let your_name: String = ctx.try_get_route_param("your_name").await.unwrap();
        let key: BroadcastType<String> = BroadcastType::PointToPoint(my_name, your_name);
        let receiver_count: ReceiverCount = get_broadcast_map().receiver_count_after_closed(key);
        let body: String = format!("receiver_count => {receiver_count:?}");
        Self {
            body,
            receiver_count,
        }
    }
    async fn handle(self, ctx: &Context) {
        ctx.set_response_body(&self.body).await;
        println!(
            "[private_closed]receiver_count => {:?}",
            self.receiver_count
        );
        Server::flush_stdout();
    }
}
struct PrivateChat {
    config: WebSocketConfig<String>,
}
impl ServerHook for PrivateChat {
    async fn new(ctx: &Context) -> Self {
        let my_name: String = ctx.try_get_route_param("my_name").await.unwrap();
        let your_name: String = ctx.try_get_route_param("your_name").await.unwrap();
        let key: BroadcastType<String> = BroadcastType::PointToPoint(my_name, your_name);
        let config: WebSocketConfig<String> = WebSocketConfig::new()
            .set_context(ctx.clone())
            .set_broadcast_type(key)
            .set_request_config(RequestConfig::default())
            .set_capacity(1024)
            .set_connected_hook::<ConnectedHook>()
            .set_request_hook::<PrivateChatRequestHook>()
            .set_sended_hook::<SendedHook>()
            .set_closed_hook::<PrivateClosedHook>();
        Self { config }
    }
    async fn handle(self, _ctx: &Context) {
        get_broadcast_map().run(self.config).await;
    }
}
#[tokio::test]
async fn main() {
    let server: Server = Server::new().await;
    server.task_panic::<TaskPanicHook>().await;
    server.request_error::<RequestErrorHook>().await;
    server.request_middleware::<RequestMiddleware>().await;
    server.request_middleware::<UpgradeHook>().await;
    server.route::<GroupChat>("/{group_name}").await;
    server.route::<PrivateChat>("/{my_name}/{your_name}").await;
    let server_control_hook_1: ServerControlHook = server.run().await.unwrap_or_default();
    let server_control_hook_2: ServerControlHook = server_control_hook_1.clone();
    tokio::spawn(async move {
        tokio::time::sleep(std::time::Duration::from_secs(60)).await;
        server_control_hook_2.shutdown().await;
    });
    server_control_hook_1.wait().await;
}
```
# Path: hyperlane-plugin-websocket/src/websocket/trait.rs
```rust
pub trait BroadcastTypeTrait: ToString + PartialOrd + Clone {}
```
# Path: hyperlane-plugin-websocket/src/websocket/const.rs
```rust
pub(crate) const POINT_TO_POINT_KEY: &str = "ptp-";
pub(crate) const POINT_TO_GROUP_KEY: &str = "ptg-";
```
# Path: hyperlane-plugin-websocket/src/websocket/mod.rs
```rust
pub(crate) mod r#const;
pub(crate) mod r#enum;
pub(crate) mod r#impl;
pub(crate) mod r#struct;
pub(crate) mod r#trait;
```
# Path: hyperlane-plugin-websocket/src/websocket/enum.rs
```rust
use crate::*;
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum BroadcastType<T: BroadcastTypeTrait> {
    PointToPoint(T, T),
    PointToGroup(T),
    Unknown,
}
```
# Path: hyperlane-plugin-websocket/src/websocket/struct.rs
```rust
use crate::*;
#[derive(Debug, Clone, Default)]
pub struct WebSocket {
    pub(super) broadcast_map: BroadcastMap<Vec<u8>>,
}
#[derive(Clone)]
pub struct WebSocketConfig<B: BroadcastTypeTrait> {
    pub(super) context: Context,
    pub(super) request_config: RequestConfig,
    pub(super) capacity: Capacity,
    pub(super) broadcast_type: BroadcastType<B>,
    pub(super) connected_hook: ServerHookHandler,
    pub(super) request_hook: ServerHookHandler,
    pub(super) sended_hook: ServerHookHandler,
    pub(super) closed_hook: ServerHookHandler,
}
```
# Path: hyperlane-plugin-websocket/src/websocket/impl.rs
```rust
use crate::*;
impl BroadcastTypeTrait for String {}
impl BroadcastTypeTrait for &str {}
impl BroadcastTypeTrait for char {}
impl BroadcastTypeTrait for bool {}
impl BroadcastTypeTrait for i8 {}
impl BroadcastTypeTrait for i16 {}
impl BroadcastTypeTrait for i32 {}
impl BroadcastTypeTrait for i64 {}
impl BroadcastTypeTrait for i128 {}
impl BroadcastTypeTrait for isize {}
impl BroadcastTypeTrait for u8 {}
impl BroadcastTypeTrait for u16 {}
impl BroadcastTypeTrait for u32 {}
impl BroadcastTypeTrait for u64 {}
impl BroadcastTypeTrait for u128 {}
impl BroadcastTypeTrait for usize {}
impl BroadcastTypeTrait for f32 {}
impl BroadcastTypeTrait for f64 {}
impl BroadcastTypeTrait for IpAddr {}
impl BroadcastTypeTrait for Ipv4Addr {}
impl BroadcastTypeTrait for Ipv6Addr {}
impl BroadcastTypeTrait for SocketAddr {}
impl BroadcastTypeTrait for NonZeroU8 {}
impl BroadcastTypeTrait for NonZeroU16 {}
impl BroadcastTypeTrait for NonZeroU32 {}
impl BroadcastTypeTrait for NonZeroU64 {}
impl BroadcastTypeTrait for NonZeroU128 {}
impl BroadcastTypeTrait for NonZeroUsize {}
impl BroadcastTypeTrait for NonZeroI8 {}
impl BroadcastTypeTrait for NonZeroI16 {}
impl BroadcastTypeTrait for NonZeroI32 {}
impl BroadcastTypeTrait for NonZeroI64 {}
impl BroadcastTypeTrait for NonZeroI128 {}
impl BroadcastTypeTrait for NonZeroIsize {}
impl BroadcastTypeTrait for Infallible {}
impl BroadcastTypeTrait for &String {}
impl BroadcastTypeTrait for &&str {}
impl BroadcastTypeTrait for &char {}
impl BroadcastTypeTrait for &bool {}
impl BroadcastTypeTrait for &i8 {}
impl BroadcastTypeTrait for &i16 {}
impl BroadcastTypeTrait for &i32 {}
impl BroadcastTypeTrait for &i64 {}
impl BroadcastTypeTrait for &i128 {}
impl BroadcastTypeTrait for &isize {}
impl BroadcastTypeTrait for &u8 {}
impl BroadcastTypeTrait for &u16 {}
impl BroadcastTypeTrait for &u32 {}
impl BroadcastTypeTrait for &u128 {}
impl BroadcastTypeTrait for &usize {}
impl BroadcastTypeTrait for &f32 {}
impl BroadcastTypeTrait for &f64 {}
impl BroadcastTypeTrait for &IpAddr {}
impl BroadcastTypeTrait for &Ipv4Addr {}
impl BroadcastTypeTrait for &Ipv6Addr {}
impl BroadcastTypeTrait for &SocketAddr {}
impl BroadcastTypeTrait for &NonZeroU8 {}
impl BroadcastTypeTrait for &NonZeroU16 {}
impl BroadcastTypeTrait for &NonZeroU32 {}
impl BroadcastTypeTrait for &NonZeroU64 {}
impl BroadcastTypeTrait for &NonZeroU128 {}
impl BroadcastTypeTrait for &NonZeroUsize {}
impl BroadcastTypeTrait for &NonZeroI8 {}
impl BroadcastTypeTrait for &NonZeroI16 {}
impl BroadcastTypeTrait for &NonZeroI32 {}
impl BroadcastTypeTrait for &NonZeroI64 {}
impl BroadcastTypeTrait for &NonZeroI128 {}
impl BroadcastTypeTrait for &NonZeroIsize {}
impl BroadcastTypeTrait for &Infallible {}
impl<B: BroadcastTypeTrait> Default for BroadcastType<B> {
    #[inline(always)]
    fn default() -> Self {
        BroadcastType::Unknown
    }
}
impl<B: BroadcastTypeTrait> BroadcastType<B> {
    #[inline(always)]
    pub fn get_key(broadcast_type: BroadcastType<B>) -> String {
        match broadcast_type {
            BroadcastType::PointToPoint(key1, key2) => {
                let (first_key, second_key) = if key1 <= key2 {
                    (key1, key2)
                } else {
                    (key2, key1)
                };
                format!(
                    "{}-{}-{}",
                    POINT_TO_POINT_KEY,
                    first_key.to_string(),
                    second_key.to_string()
                )
            }
            BroadcastType::PointToGroup(key) => {
                format!("{}-{}", POINT_TO_GROUP_KEY, key.to_string())
            }
            BroadcastType::Unknown => String::new(),
        }
    }
}
impl<B: BroadcastTypeTrait> Default for WebSocketConfig<B> {
    #[inline(always)]
    fn default() -> Self {
        let default_hook: ServerHookHandler = Arc::new(|_ctx| Box::pin(async {}));
        Self {
            context: Context::default(),
            request_config: RequestConfig::default(),
            capacity: DEFAULT_BROADCAST_SENDER_CAPACITY,
            broadcast_type: BroadcastType::default(),
            connected_hook: default_hook.clone(),
            request_hook: default_hook.clone(),
            sended_hook: default_hook.clone(),
            closed_hook: default_hook,
        }
    }
}
impl<B: BroadcastTypeTrait> WebSocketConfig<B> {
    #[inline(always)]
    pub fn new() -> Self {
        Self::default()
    }
}
impl<B: BroadcastTypeTrait> WebSocketConfig<B> {
    #[inline(always)]
    pub fn set_request_config(mut self, request_config: RequestConfig) -> Self {
        self.request_config = request_config;
        self
    }
    #[inline(always)]
    pub fn set_capacity(mut self, capacity: Capacity) -> Self {
        self.capacity = capacity;
        self
    }
    #[inline(always)]
    pub fn set_context(mut self, context: Context) -> Self {
        self.context = context;
        self
    }
    #[inline(always)]
    pub fn set_broadcast_type(mut self, broadcast_type: BroadcastType<B>) -> Self {
        self.broadcast_type = broadcast_type;
        self
    }
    #[inline(always)]
    pub fn get_context(&self) -> &Context {
        &self.context
    }
    #[inline(always)]
    pub fn get_request_config(&self) -> RequestConfig {
        self.request_config
    }
    #[inline(always)]
    pub fn get_capacity(&self) -> Capacity {
        self.capacity
    }
    #[inline(always)]
    pub fn get_broadcast_type(&self) -> &BroadcastType<B> {
        &self.broadcast_type
    }
    #[inline(always)]
    pub fn set_connected_hook<S>(mut self) -> Self
    where
        S: ServerHook,
    {
        self.connected_hook = server_hook_factory::<S>();
        self
    }
    #[inline(always)]
    pub fn set_request_hook<S>(mut self) -> Self
    where
        S: ServerHook,
    {
        self.request_hook = server_hook_factory::<S>();
        self
    }
    #[inline(always)]
    pub fn set_sended_hook<S>(mut self) -> Self
    where
        S: ServerHook,
    {
        self.sended_hook = server_hook_factory::<S>();
        self
    }
    #[inline(always)]
    pub fn set_closed_hook<S>(mut self) -> Self
    where
        S: ServerHook,
    {
        self.closed_hook = server_hook_factory::<S>();
        self
    }
    #[inline(always)]
    pub fn get_connected_hook(&self) -> &ServerHookHandler {
        &self.connected_hook
    }
    #[inline(always)]
    pub fn get_request_hook(&self) -> &ServerHookHandler {
        &self.request_hook
    }
    #[inline(always)]
    pub fn get_sended_hook(&self) -> &ServerHookHandler {
        &self.sended_hook
    }
    #[inline(always)]
    pub fn get_closed_hook(&self) -> &ServerHookHandler {
        &self.closed_hook
    }
}
impl WebSocket {
    #[inline(always)]
    pub fn new() -> Self {
        Self::default()
    }
    #[inline(always)]
    fn subscribe_unwrap_or_insert<B: BroadcastTypeTrait>(
        &self,
        broadcast_type: BroadcastType<B>,
        capacity: Capacity,
    ) -> BroadcastMapReceiver<Vec<u8>> {
        let key: String = BroadcastType::get_key(broadcast_type);
        self.broadcast_map.subscribe_or_insert(&key, capacity)
    }
    #[inline(always)]
    fn point_to_point<B: BroadcastTypeTrait>(
        &self,
        key1: &B,
        key2: &B,
        capacity: Capacity,
    ) -> BroadcastMapReceiver<Vec<u8>> {
        self.subscribe_unwrap_or_insert(
            BroadcastType::PointToPoint(key1.clone(), key2.clone()),
            capacity,
        )
    }
    #[inline(always)]
    fn point_to_group<B: BroadcastTypeTrait>(
        &self,
        key: &B,
        capacity: Capacity,
    ) -> BroadcastMapReceiver<Vec<u8>> {
        self.subscribe_unwrap_or_insert(BroadcastType::PointToGroup(key.clone()), capacity)
    }
    #[inline(always)]
    pub fn receiver_count<B: BroadcastTypeTrait>(
        &self,
        broadcast_type: BroadcastType<B>,
    ) -> ReceiverCount {
        let key: String = BroadcastType::get_key(broadcast_type);
        self.broadcast_map.receiver_count(&key).unwrap_or(0)
    }
    #[inline(always)]
    pub fn receiver_count_before_connected<B: BroadcastTypeTrait>(
        &self,
        broadcast_type: BroadcastType<B>,
    ) -> ReceiverCount {
        let count: ReceiverCount = self.receiver_count(broadcast_type);
        count.clamp(0, ReceiverCount::MAX - 1) + 1
    }
    #[inline(always)]
    pub fn receiver_count_after_closed<B: BroadcastTypeTrait>(
        &self,
        broadcast_type: BroadcastType<B>,
    ) -> ReceiverCount {
        let count: ReceiverCount = self.receiver_count(broadcast_type);
        count.clamp(1, ReceiverCount::MAX) - 1
    }
    #[inline(always)]
    pub fn send<T, B>(
        &self,
        broadcast_type: BroadcastType<B>,
        data: T,
    ) -> BroadcastMapSendResult<Vec<u8>>
    where
        T: Into<Vec<u8>>,
        B: BroadcastTypeTrait,
    {
        let key: String = BroadcastType::get_key(broadcast_type);
        self.broadcast_map.send(&key, data.into())
    }
    pub async fn run<B: BroadcastTypeTrait>(&self, config: WebSocketConfig<B>) {
        let ctx: Context = config.get_context().clone();
        if ctx.to_string() == Context::default().to_string() {
            panic!("Context must be set");
        }
        let request_config: RequestConfig = config.get_request_config();
        let capacity: Capacity = config.get_capacity();
        let broadcast_type: BroadcastType<B> = config.get_broadcast_type().clone();
        let mut receiver: Receiver<Vec<u8>> = match &broadcast_type {
            BroadcastType::PointToPoint(key1, key2) => self.point_to_point(key1, key2, capacity),
            BroadcastType::PointToGroup(key) => self.point_to_group(key, capacity),
            BroadcastType::Unknown => panic!("BroadcastType must be PointToPoint or PointToGroup"),
        };
        let key: String = BroadcastType::get_key(broadcast_type);
        config.get_connected_hook()(&ctx).await;
        let result_handle = || async {
            ctx.aborted().await;
            ctx.closed().await;
        };
        loop {
            tokio::select! {
                request_res = ctx.ws_from_stream(request_config) => {
                    if request_res.is_ok() {
                        config.get_request_hook()(&ctx).await;
                    } else {
                        config.get_closed_hook()(&ctx).await;
                    }
                    if ctx.get_aborted().await {
                        continue;
                    }
                    if ctx.get_closed().await {
                        break;
                    }
                    let body: ResponseBody = ctx.get_response_body().await;
                    let is_err: bool = self.broadcast_map.send(&key, body).is_err();
                    config.get_sended_hook()(&ctx).await;
                    if is_err || ctx.get_closed().await{
                        break;
                    }
                },
                msg_res = receiver.recv() => {
                    if let Ok(msg) = &msg_res {
                        let frame_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(msg);
                        if ctx.try_send_body_list_with_data(&frame_list).await.is_ok() {
                            continue;
                        }
                    }
                    break;
                }
            }
        }
        result_handle().await;
    }
}
```
# Path: hyperlane-quick-start/README.md
## hyperlane-quick-start
[English](README.md) | [简体中文](README.ZH-CN.md)
> A lightweight, high-performance, and cross-platform Rust HTTP server library built on Tokio. It simplifies modern web service development by providing built-in support for middleware, WebSocket, Server-Sent Events (SSE), and raw TCP communication. With a unified and ergonomic API across Windows, Linux, and MacOS, it enables developers to build robust, scalable, and event-driven network applications with minimal overhead and maximum flexibility.
## Official Documentation
- [Official Documentation](https://docs.ltpp.vip/hyperlane/)
## Api Docs
- [Api Docs](https://docs.rs/hyperlane/latest/hyperlane/)
## Run
### start
```sh
cargo run
```
### hot-restart
```sh
cargo run hot-restart
```
### started in background
```sh
cargo run -- -d
```
### stop
```sh
cargo run stop
```
### restart
```sh
cargo run restart
```
### restarted in background
```sh
cargo run restart -d
```
## Performance
- [Performance](https://docs.ltpp.vip/hyperlane/speed)
## Appreciate
> If you feel that `hyperlane` is helpful to you, feel free to donate
### WeChat Pay
### Alipay
### Virtual Currency Pay
| Virtual Currency | Virtual Currency Address                   |
| ---------------- | ------------------------------------------ |
| BTC              | 3QndxCJTf3mEniTgyRRQ1jcNTJajm9qSCy         |
| ETH              | 0x8EB3794f67897ED397584d3a1248a79e0B8e97A6 |
| BSC              | 0x8EB3794f67897ED397584d3a1248a79e0B8e97A6 |
## Contact
# Path: hyperlane-quick-start/README.ZH-CN.md
## hyperlane-quick-start
[English](README.md) | [简体中文](README.ZH-CN.md)
> 这是一个轻量级、高性能且跨平台的 Rust HTTP 服务器库，基于 Tokio 构建。它通过提供中间件、WebSocket、服务器推送事件(SSE)和原始 TCP 通信的内置支持，简化了现代 Web 服务的开发。凭借在 Windows、Linux 和 macOS 上统一且符合人体工程学的 API，它使开发者能够以最小的开销和最大的灵活性构建强大、可扩展且事件驱动的网络应用程序。
## 官方文档
- [官方文档](https://docs.ltpp.vip/hyperlane/)
## API 文档
- [API 文档](https://docs.rs/hyperlane/latest/hyperlane/)
## 运行
### 运行
```sh
cargo run
```
### 热重启
```sh
cargo run hot-restart
```
### 在后台运行
```sh
cargo run -- -d
```
### 停止
```sh
cargo run stop
```
### 重启
```sh
cargo run restart
```
### 重启在后台运行
```sh
cargo run restart -d
```
## 性能测试
- [性能测试](https://docs.ltpp.vip/hyperlane/speed)
## 赞赏
> 如果你觉得 `hyperlane` 对你有所帮助，欢迎捐赠
### 微信支付
### 支付宝支付
### 虚拟货币支付
| 虚拟货币 | 虚拟货币地址                               |
| -------- | ------------------------------------------ |
| BTC      | 3QndxCJTf3mEniTgyRRQ1jcNTJajm9qSCy         |
| ETH      | 0x8EB3794f67897ED397584d3a1248a79e0B8e97A6 |
| BSC      | 0x8EB3794f67897ED397584d3a1248a79e0B8e97A6 |
# Path: hyperlane-quick-start/resources/static/not_found/index.html
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>404 Not Found</title>
    <style>
      .center-text {
        text-align: center;
      }
      a {
        color: #1e90ff;
        text-decoration: none;
        transition: color 0.3s, border-bottom-color 0.3s;
      }
      a:hover,
      a:focus {
        color: pink;
        border-bottom-color: pink;
        outline: none;
        cursor: pointer;
      }
    </style>
  </head>
  <body>
    <h1 class="center-text">404 Not Found</h1>
    <hr />
    <p class="center-text">
      Server:
      <a href="https://github.com/hyperlane-dev/hyperlane" target="_blank"
        >Hyperlane</a
    </p>
  </body>
</html>
```
# Path: hyperlane-quick-start/resources/templates/index/index.html
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Hyperlane</title>
    <style>
      .center-text {
        text-align: center;
      }
      a {
        color: #1e90ff;
        text-decoration: none;
        transition: color 0.3s, border-bottom-color 0.3s;
      }
      a:hover,
      a:focus {
        color: pink;
        border-bottom-color: pink;
        outline: none;
        cursor: pointer;
      }
    </style>
  </head>
  <body>
    <h1 class="center-text">Hello hyperlane: {{ time }}</h1>
    <hr />
    <p class="center-text">
      Server:
      <a href="https://github.com/hyperlane-dev/hyperlane" target="_blank"
        >Hyperlane</a
    </p>
  </body>
</html>
```
# Path: hyperlane-quick-start/init/lib.rs
```rust
pub mod application;
pub mod framework;
use hyperlane::*;
use hyperlane_utils::{
    log::{error, info},
    *,
};
```
# Path: hyperlane-quick-start/init/framework/mod.rs
```rust
pub mod shutdown;
pub mod wait;
use super::*;
```
# Path: hyperlane-quick-start/init/framework/wait/mod.rs
```rust
mod r#fn;
pub use r#fn::*;
use super::{shutdown::*, *};
#[allow(unused_imports)]
use hyperlane_app::*;
use hyperlane_config::framework::*;
use hyperlane_plugin::process::*;
use hyperlane_utils::log::LevelFilter;
use tokio::runtime::{Builder, Runtime};
```
# Path: hyperlane-quick-start/init/framework/wait/fn.rs
```rust
use crate::application::init_log;
use super::*;
#[hyperlane(config: ServerConfig)]
async fn init_config(server: &Server) {
    config.host(SERVER_HOST).await;
    config.port(SERVER_PORT).await;
    config.ttl(SERVER_TTI).await;
    config.nodelay(SERVER_NODELAY).await;
    config.request_config(RequestConfig::default()).await;
    server.config(config).await;
}
async fn print_route_matcher(server: &Server) {
    let route_matcher: RouteMatcher = server.get_route_matcher().await;
    for key in route_matcher.get_static_route().keys() {
        info!("Static route: {key}");
    }
    for value in route_matcher.get_dynamic_route().values() {
        for (route_pattern, _) in value {
            info!("Dynamic route: {route_pattern}");
        }
    }
    for value in route_matcher.get_regex_route().values() {
        for (route_pattern, _) in value {
            info!("Regex route: {route_pattern}");
        }
    }
}
fn runtime() -> Runtime {
    Builder::new_multi_thread()
        .worker_threads(num_cpus::get_physical() << 1)
        .thread_stack_size(1_048_576)
        .max_blocking_threads(2_048)
        .max_io_events_per_tick(1_024)
        .enable_all()
        .build()
        .unwrap()
}
#[hyperlane(server: Server)]
async fn create_server() {
    init_log(LevelFilter::Info);
    init_config(&server).await;
    info!("Server initialization successful");
    let server_result: Result<ServerControlHook, ServerError> = server.run().await;
    match server_result {
        Ok(server_hook) => {
            let host_port: String = format!("{SERVER_HOST}:{SERVER_PORT}");
            print_route_matcher(&server).await;
            info!("Server listen in: {host_port}");
            let shutdown: SharedAsyncTaskFactory<()> = server_hook.get_shutdown_hook().clone();
            set_shutdown(shutdown);
            server_hook.wait().await;
        }
        Err(server_error) => error!("Server run error: {server_error}"),
    }
}
pub fn run() {
    runtime().block_on(create(create_server));
}
```
# Path: hyperlane-quick-start/init/framework/shutdown/mod.rs
```rust
mod r#fn;
mod r#static;
pub use r#fn::*;
use super::*;
use r#static::*;
use std::sync::{Arc, OnceLock};
```
# Path: hyperlane-quick-start/init/framework/shutdown/fn.rs
```rust
use super::*;
pub fn set_shutdown(shutdown: SharedAsyncTaskFactory<()>) {
    let _ = SHUTDOWN.set(shutdown);
}
pub fn shutdown() -> SharedAsyncTaskFactory<()> {
    SHUTDOWN
        .get_or_init(|| Arc::new(|| Box::pin(async {})))
        .clone()
}
```
# Path: hyperlane-quick-start/init/framework/shutdown/static.rs
```rust
use super::*;
pub(super) static SHUTDOWN: OnceLock> = OnceLock::new();
```
# Path: hyperlane-quick-start/init/application/mod.rs
```rust
mod log;
pub use log::*;
```
# Path: hyperlane-quick-start/init/application/log/mod.rs
```rust
mod r#fn;
pub use r#fn::*;
use hyperlane_plugin::log::*;
use hyperlane_utils::log::LevelFilter;
```
# Path: hyperlane-quick-start/init/application/log/fn.rs
```rust
use super::*;
pub fn init_log(level: LevelFilter) {
    Logger::init(level);
}
```
# Path: hyperlane-quick-start/app/lib.rs
```rust
pub mod aspect;
pub mod controller;
pub mod domain;
pub mod exception;
pub mod filter;
pub mod mapper;
pub mod middleware;
pub mod model;
pub mod service;
pub mod utils;
pub mod view;
use hyperlane::*;
use hyperlane_utils::{
    log::{error, info},
    *,
};
```
# Path: hyperlane-quick-start/app/model/mod.rs
```rust
pub mod application;
pub mod data_transfer;
pub mod param;
use super::*;
use serde::{Deserialize, Serialize};
use serde_with::skip_serializing_none;
use utoipa::ToSchema;
```
# Path: hyperlane-quick-start/app/model/data_transfer/mod.rs
```rust
pub mod common;
use super::*;
```
# Path: hyperlane-quick-start/app/model/data_transfer/common/mod.rs
```rust
mod r#enum;
mod r#impl;
mod r#struct;
pub use r#enum::*;
pub use r#struct::*;
use super::*;
```
# Path: hyperlane-quick-start/app/model/data_transfer/common/enum.rs
```rust
use super::*;
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, ToSchema)]
#[repr(i32)]
pub enum ResponseCode {
    Success = 200,
    BadRequest = 400,
    Unauthorized = 401,
    Forbidden = 403,
    NotFound = 404,
    InternalError = 500,
    DatabaseError = 501,
    BusinessError = 502,
}
```
# Path: hyperlane-quick-start/app/model/data_transfer/common/struct.rs
```rust
use super::*;
#[skip_serializing_none]
#[derive(Debug, Clone, Default, Serialize, Deserialize, ToSchema, Data)]
pub struct ApiResponse<T>
where
    T: Serialize + Default,
{
    code: i32,
    message: String,
    data: Option<T>,
    timestamp: Option<String>,
}
```
# Path: hyperlane-quick-start/app/model/data_transfer/common/impl.rs
```rust
use super::*;
impl ResponseCode {
    pub fn default_message(&self) -> &'static str {
        match self {
            Self::Success => "Operation successful",
            Self::BadRequest => "Invalid request parameters",
            Self::Unauthorized => "Unauthorized access",
            Self::Forbidden => "Access forbidden",
            Self::NotFound => "Resource not found",
            Self::InternalError => "Internal server error",
            Self::DatabaseError => "Database operation failed",
            Self::BusinessError => "Business logic error",
        }
    }
}
impl<T> ApiResponse<T>
where
    T: Serialize + Default,
{
    pub fn success(data: T) -> Self {
        let mut instance: ApiResponse<T> = Self::default();
        instance
            .set_code(ResponseCode::Success as i32)
            .set_message("Success".to_string())
            .set_data(Some(data))
            .set_timestamp(Some(date()));
        instance
    }
    pub fn success_with_message(data: T, message: impl Into<String>) -> Self {
        let mut instance: ApiResponse<T> = Self::default();
        instance
            .set_code(ResponseCode::Success as i32)
            .set_message(message.into())
            .set_data(Some(data))
            .set_timestamp(Some(date()));
        instance
    }
    pub fn error(message: impl Into<String>) -> Self {
        let mut instance: ApiResponse<T> = Self::default();
        instance
            .set_code(ResponseCode::InternalError as i32)
            .set_message(message.into())
            .set_data(None)
            .set_timestamp(Some(date()));
        instance
    }
    pub fn error_with_code(code: ResponseCode, message: impl Into<String>) -> Self {
        let mut instance: ApiResponse<T> = Self::default();
        instance
            .set_code(code as i32)
            .set_message(message.into())
            .set_data(None)
            .set_timestamp(Some(date()));
        instance
    }
    pub fn to_json_bytes(&self) -> Vec<u8> {
        serde_json::to_vec(self).unwrap_or_default()
    }
}
impl ApiResponse<()> {
    pub fn success_without_data(message: impl Into<String>) -> Self {
        let mut instance: ApiResponse<()> = Self::default();
        instance
            .set_code(ResponseCode::Success as i32)
            .set_message(message.into())
            .set_data(None)
            .set_timestamp(Some(date()));
        instance
    }
}
```
# Path: hyperlane-quick-start/app/model/param/mod.rs
```rust
pub mod websocket;
use super::*;
```
# Path: hyperlane-quick-start/app/model/param/websocket/mod.rs
```rust
mod r#struct;
pub use r#struct::*;
use super::*;
use serde::{Deserialize, Serialize};
```
# Path: hyperlane-quick-start/app/model/param/websocket/struct.rs
```rust
use super::*;
#[derive(Debug, Clone, Default, Data, Deserialize, Serialize)]
pub struct WebSocketMessage {
    pub name: String,
    pub message: String,
}
```
# Path: hyperlane-quick-start/app/middleware/mod.rs
```rust
pub mod request;
pub mod response;
use super::*;
```
# Path: hyperlane-quick-start/app/middleware/response/mod.rs
```rust
pub mod log;
pub mod send;
pub use log::*;
pub use send::*;
use super::*;
```
# Path: hyperlane-quick-start/app/middleware/response/send/mod.rs
```rust
mod r#impl;
mod r#struct;
pub use r#struct::*;
use super::*;
```
# Path: hyperlane-quick-start/app/middleware/response/send/struct.rs
```rust
use super::*;
#[response_middleware(1)]
pub struct SendMiddleware;
```
# Path: hyperlane-quick-start/app/middleware/response/send/impl.rs
```rust
use super::*;
impl ServerHook for SendMiddleware {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(
        http,
        reject(ctx.get_request_upgrade_type().await.is_ws()),
        send
    )]
    async fn handle(self, ctx: &Context) {}
}
```
# Path: hyperlane-quick-start/app/middleware/response/log/mod.rs
```rust
mod r#impl;
mod r#struct;
pub use r#struct::*;
use super::*;
```
# Path: hyperlane-quick-start/app/middleware/response/log/struct.rs
```rust
use super::*;
#[response_middleware(2)]
pub struct LogMiddleware;
```
# Path: hyperlane-quick-start/app/middleware/response/log/impl.rs
```rust
use super::*;
impl ServerHook for LogMiddleware {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &Context) {
        let request: String = ctx.get_request().await.get_string();
        let response: String = ctx.get_response().await.get_string();
        info!("{request}");
        info!("{response}");
    }
}
```
# Path: hyperlane-quick-start/app/middleware/request/mod.rs
```rust
pub mod cross;
pub mod response;
pub mod upgrade;
pub use cross::*;
pub use response::*;
pub use upgrade::*;
use super::*;
```
# Path: hyperlane-quick-start/app/middleware/request/response/mod.rs
```rust
mod r#impl;
mod r#struct;
pub use r#struct::*;
use super::*;
use hyperlane_config::application::templates::*;
```
# Path: hyperlane-quick-start/app/middleware/request/response/struct.rs
```rust
use super::*;
#[request_middleware(2)]
pub struct ResponseHeaderMiddleware;
#[request_middleware(3)]
pub struct ResponseStatusCodeMiddleware;
#[request_middleware(4)]
pub struct ResponseBodyMiddleware;
```
# Path: hyperlane-quick-start/app/middleware/request/response/impl.rs
```rust
use super::*;
impl ServerHook for ResponseHeaderMiddleware {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[response_header(DATE => gmt())]
    #[response_header(SERVER => HYPERLANE)]
    #[response_header(CONNECTION => KEEP_ALIVE)]
    #[epilogue_macros(
        response_header(CONTENT_TYPE => content_type),
        response_header("SocketAddr" => socket_addr_string)
    )]
    async fn handle(self, ctx: &Context) {
        let socket_addr_string: String = ctx.get_socket_addr_string().await;
        let content_type: String = ContentType::format_content_type_with_charset(TEXT_HTML, UTF8);
    }
}
impl ServerHook for ResponseStatusCodeMiddleware {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[response_status_code(200)]
    async fn handle(self, ctx: &Context) {}
}
impl ServerHook for ResponseBodyMiddleware {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[response_body(INDEX_HTML.replace("{{ time }}", &time()))]
    async fn handle(self, ctx: &Context) {}
}
```
# Path: hyperlane-quick-start/app/middleware/request/cross/mod.rs
```rust
mod r#impl;
mod r#struct;
pub use r#struct::*;
use super::*;
```
# Path: hyperlane-quick-start/app/middleware/request/cross/struct.rs
```rust
use super::*;
#[request_middleware(1)]
pub struct CrossMiddleware;
```
# Path: hyperlane-quick-start/app/middleware/request/cross/impl.rs
```rust
use super::*;
impl ServerHook for CrossMiddleware {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[response_version(HttpVersion::Http1_1)]
    #[response_header(ACCESS_CONTROL_ALLOW_ORIGIN => WILDCARD_ANY)]
    #[response_header(ACCESS_CONTROL_ALLOW_METHODS => ALL_METHODS)]
    #[response_header(ACCESS_CONTROL_ALLOW_HEADERS => WILDCARD_ANY)]
    async fn handle(self, ctx: &Context) {}
}
```
# Path: hyperlane-quick-start/app/middleware/request/upgrade/mod.rs
```rust
mod r#impl;
mod r#struct;
pub use r#struct::*;
use super::*;
```
# Path: hyperlane-quick-start/app/middleware/request/upgrade/struct.rs
```rust
use super::*;
#[request_middleware(5)]
pub struct UpgradeMiddleware;
```
# Path: hyperlane-quick-start/app/middleware/request/upgrade/impl.rs
```rust
use super::*;
impl ServerHook for UpgradeMiddleware {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(
        ws,
        response_version(HttpVersion::Http1_1),
        response_status_code(101),
        response_body(&vec![]),
        response_header(UPGRADE => WEBSOCKET),
        response_header(CONNECTION => UPGRADE),
        response_header(SEC_WEBSOCKET_ACCEPT => WebSocketFrame::generate_accept_key(ctx.try_get_request_header_back(SEC_WEBSOCKET_KEY).await.unwrap())),
        send
    )]
    async fn handle(self, ctx: &Context) {}
}
```
# Path: hyperlane-quick-start/app/exception/mod.rs
```rust
pub mod application;
pub mod framework;
pub use framework::*;
use super::*;
```
# Path: hyperlane-quick-start/app/exception/framework/mod.rs
```rust
mod r#impl;
mod r#struct;
pub use r#struct::*;
use super::*;
use model::data_transfer::common::*;
```
# Path: hyperlane-quick-start/app/exception/framework/struct.rs
```rust
use super::*;
#[task_panic]
pub struct TaskPanicHook {
    pub(super) content_type: String,
    pub(super) response_body: String,
}
#[request_error]
pub struct RequestErrorHook {
    pub(super) response_status_code: ResponseStatusCode,
    pub(super) content_type: String,
    pub(super) response_body: String,
}
```
# Path: hyperlane-quick-start/app/exception/framework/impl.rs
```rust
use super::*;
impl ServerHook for TaskPanicHook {
    #[task_panic_data(task_panic_data)]
    async fn new(ctx: &Context) -> Self {
        let content_type: String =
            ContentType::format_content_type_with_charset(APPLICATION_JSON, UTF8);
        Self {
            content_type,
            response_body: task_panic_data.to_string(),
        }
    }
    #[prologue_macros(
        response_version(HttpVersion::Http1_1),
        response_status_code(500),
        clear_response_headers,
        response_header(SERVER => HYPERLANE),
        response_version(HttpVersion::Http1_1),
        response_header(CONTENT_TYPE, &self.content_type),
    )]
    #[epilogue_macros(response_body(&response_body), send)]
    async fn handle(self, ctx: &Context) {
        error!("{}", self.response_body);
        let api_response: ApiResponse<()> =
            ApiResponse::error_with_code(ResponseCode::InternalError, self.response_body);
        let response_body: Vec<u8> = api_response.to_json_bytes();
    }
}
impl ServerHook for RequestErrorHook {
    #[request_error_data(request_error_data)]
    async fn new(_ctx: &Context) -> Self {
        let content_type: String =
            ContentType::format_content_type_with_charset(APPLICATION_JSON, UTF8);
        Self {
            response_status_code: request_error_data.get_http_status_code(),
            content_type,
            response_body: request_error_data.to_string(),
        }
    }
    #[prologue_macros(
        response_version(HttpVersion::Http1_1),
        response_status_code(self.response_status_code),
        clear_response_headers,
        response_header(SERVER => HYPERLANE),
        response_version(HttpVersion::Http1_1),
        response_header(CONTENT_TYPE, &self.content_type),
    )]
    #[epilogue_macros(response_body(&response_body), send)]
    async fn handle(self, ctx: &Context) {
        if self.response_status_code == HttpStatus::BadRequest.code() {
            ctx.aborted().await;
            return;
        }
        if self.response_status_code != HttpStatus::RequestTimeout.code() {
            error!("{}", self.response_body);
        }
        let api_response: ApiResponse<()> =
            ApiResponse::error_with_code(ResponseCode::InternalError, self.response_body);
        let response_body: Vec<u8> = api_response.to_json_bytes();
    }
}
```
# Path: hyperlane-quick-start/app/view/favicon/mod.rs
```rust
mod r#fn;
pub use r#fn::*;
use super::*;
use hyperlane_config::business::logo_img::*;
```
# Path: hyperlane-quick-start/app/view/favicon/fn.rs
```rust
use super::*;
#[route("/favicon.ico")]
#[prologue_macros(
  get,
  response_status_code(301),
  response_header(LOCATION => LOGO_IMG_URL)
)]
pub async fn ico(ctx: Context) {}
```
# Path: hyperlane-quick-start/config/lib.rs
```rust
pub mod application;
pub mod framework;
use hyperlane::*;
```
# Path: hyperlane-quick-start/config/framework/const.rs
```rust
use super::*;
#[cfg(debug_assertions)]
pub const SERVER_PORT: u16 = DEFAULT_WEB_PORT;
#[cfg(not(debug_assertions))]
pub const SERVER_PORT: u16 = 65002;
pub const SERVER_HOST: &str = DEFAULT_HOST;
pub const SERVER_BUFFER: usize = DEFAULT_BUFFER_SIZE;
pub const SERVER_LOG_SIZE: usize = 100_024_000;
pub const SERVER_LOG_DIR: &str = "./tmp/logs";
pub const SERVER_INNER_PRINT: bool = true;
pub const SERVER_INNER_LOG: bool = true;
pub const SERVER_NODELAY: bool = false;
pub const SERVER_TTI: u32 = 128;
pub const SERVER_PID_FILE_PATH: &str = "./tmp/process/hyperlane.pid";
```
# Path: hyperlane-quick-start/config/framework/mod.rs
```rust
mod r#const;
pub use r#const::*;
use super::*;
```
# Path: hyperlane-quick-start/config/application/mod.rs
```rust
pub mod hello;
pub mod logo_img;
pub mod not_found;
pub mod templates;
```
# Path: hyperlane-quick-start/config/application/hello/const.rs
```rust
pub const NAME_KEY: &str = "name";
```
# Path: hyperlane-quick-start/config/application/hello/mod.rs
```rust
mod r#const;
pub use r#const::*;
```
# Path: hyperlane-quick-start/config/application/logo_img/const.rs
```rust
pub const LOGO_IMG_URL: &str = "https://docs.ltpp.vip/img/hyperlane.png";
```
# Path: hyperlane-quick-start/config/application/logo_img/mod.rs
```rust
mod r#const;
pub use r#const::*;
```
# Path: hyperlane-quick-start/config/application/not_found/const.rs
```rust
pub const NOT_FOUND_HTML: &str = include_str!("../../../resources/static/not_found/index.html");
```
# Path: hyperlane-quick-start/config/application/not_found/mod.rs
```rust
mod r#const;
pub use r#const::*;
```
# Path: hyperlane-quick-start/config/application/templates/const.rs
```rust
pub const INDEX_HTML: &str = include_str!("../../../resources/templates/index/index.html");
```
# Path: hyperlane-quick-start/config/application/templates/mod.rs
```rust
mod r#const;
pub use r#const::*;
```
# Path: hyperlane-quick-start/plugin/lib.rs
```rust
pub mod log;
pub mod process;
use hyperlane::*;
use hyperlane_utils::{
    log::{error, info},
    *,
};
```
# Path: hyperlane-quick-start/plugin/process/const.rs
```rust
pub const CMD_STOP: &str = "stop";
pub const CMD_RESTART: &str = "restart";
pub const CMD_HOT_RESTART: &str = "hot-restart";
pub const DAEMON_FLAG: &str = "-d";
```
# Path: hyperlane-quick-start/plugin/process/mod.rs
```rust
mod r#const;
mod r#fn;
pub use r#const::*;
pub use r#fn::*;
use super::*;
use hyperlane_config::framework::*;
use std::{env::args, future::Future};
```
# Path: hyperlane-quick-start/plugin/process/fn.rs
```rust
use super::*;
pub async fn create<F, Fut>(server_hook: F)
where
    F: Fn() -> Fut + Send + Sync + 'static,
    Fut: Future<Output = ()> + Send + 'static,
{
    let args: Vec<String> = args().collect();
    let mut manager: ServerManager = ServerManager::new();
    manager
        .set_pid_file(SERVER_PID_FILE_PATH)
        .set_server_hook(server_hook);
    let is_daemon: bool = args.len() >= 3 && args[2].to_lowercase() == DAEMON_FLAG;
    let start_server = || async {
        if is_daemon {
            match manager.start_daemon().await {
                Ok(_) => info!("Server started in background successfully"),
                Err(error) => {
                    error!("Error starting server in background: {error}")
                }
            };
        } else {
            info!("Server started successfully");
            manager.start().await;
        }
    };
    let stop_server = || async {
        match manager.stop().await {
            Ok(_) => info!("Server stopped successfully"),
            Err(error) => error!("Error stopping server: {error}"),
        };
    };
    let hot_restart_server = || async {
        match manager
            .watch_detached(&["--clear", "--skip-local-deps", "-q", "-x", "run"])
            .await
        {
            Ok(_) => info!("Server started successfully"),
            Err(error) => error!("Error starting server in background: {error}"),
        }
    };
    let restart_server = || async {
        stop_server().await;
        start_server().await;
    };
    if args.len() < 2 {
        start_server().await;
        return;
    }
    let command: String = args[1].to_lowercase();
    match command.as_str() {
        CMD_STOP => stop_server().await,
        CMD_RESTART => restart_server().await,
        CMD_HOT_RESTART => hot_restart_server().await,
        _ => {
            error!("Invalid command: {command}");
        }
    }
}
```
# Path: hyperlane-quick-start/plugin/log/mod.rs
```rust
mod r#impl;
mod r#static;
mod r#struct;
pub use r#struct::*;
use super::*;
use hyperlane_config::framework::*;
use r#static::*;
use hyperlane_utils::{
    log::{Level, LevelFilter, Log, Metadata, Record, set_logger, set_max_level},
    once_cell::sync::Lazy,
};
```
# Path: hyperlane-quick-start/plugin/log/struct.rs
```rust
#[derive(Debug, Clone, Copy)]
pub struct Logger;
```
# Path: hyperlane-quick-start/plugin/log/impl.rs
```rust
use super::*;
impl Logger {
    pub fn log_trace<T>(data: T)
    where
        T: AsRef<str>,
    {
        FILE_LOGGER.trace(data, log_handler);
    }
    pub fn log_debug<T>(data: T)
    where
        T: AsRef<str>,
    {
        FILE_LOGGER.debug(data, log_handler);
    }
    pub fn log_info<T>(data: T)
    where
        T: AsRef<str>,
    {
        FILE_LOGGER.info(data, log_handler);
    }
    pub fn log_warn<T>(data: T)
    where
        T: AsRef<str>,
    {
        FILE_LOGGER.warn(data, log_handler);
    }
    pub fn log_error<T>(data: T)
    where
        T: AsRef<str>,
    {
        FILE_LOGGER.error(data, log_handler);
    }
}
impl Log for Logger {
    fn enabled(&self, metadata: &Metadata) -> bool {
        #[cfg(debug_assertions)]
        {
            metadata.level() <= Level::Trace
        }
        #[cfg(not(debug_assertions))]
        {
            metadata.level() <= Level::Error
        }
    }
    fn log(&self, record: &Record) {
        let time_text: String = format!("{SPACE}{}{SPACE}", time());
        let level_text: String = format!("{SPACE}{}{SPACE}", record.level());
        let args_text: String = format!("{SPACE}{}{SPACE}", record.args());
        let write_file_data: String = format!("{} {}", record.level(), record.args());
        let mut time_output_builder: OutputBuilder<'_> = OutputBuilder::new();
        let mut level_output_builder: OutputBuilder<'_> = OutputBuilder::new();
        let mut args_output_builder: OutputBuilder<'_> = OutputBuilder::new();
        let time_output: Output<'_> = time_output_builder
            .text(&time_text)
            .bold(true)
            .color(ColorType::Use(Color::White))
            .bg_color(ColorType::Use(Color::Green))
            .build();
        let level_output: Output<'_> = level_output_builder
            .text(&level_text)
            .bold(true)
            .color(ColorType::Use(Color::White))
            .bg_color(match record.level() {
                Level::Trace | Level::Debug => ColorType::Use(Color::Yellow),
                Level::Info | Level::Warn => ColorType::Use(Color::Blue),
                Level::Error => ColorType::Use(Color::Red),
            })
            .build();
        let args_output: Output<'_> = args_output_builder
            .text(&args_text)
            .bold(true)
            .endl(true)
            .color(match record.level() {
                Level::Trace | Level::Debug => ColorType::Use(Color::Yellow),
                Level::Info | Level::Warn => ColorType::Use(Color::Blue),
                Level::Error => ColorType::Use(Color::Red),
            })
            .build();
        OutputListBuilder::new()
            .add(time_output)
            .add(level_output)
            .add(args_output)
            .run();
        if self.enabled(record.metadata()) {
            match record.metadata().level() {
                Level::Trace => Self::log_trace(&write_file_data),
                Level::Debug => Self::log_debug(&write_file_data),
                Level::Info => Self::log_info(&write_file_data),
                Level::Warn => Self::log_warn(&write_file_data),
                Level::Error => Self::log_error(&write_file_data),
            }
        }
    }
    fn flush(&self) {
        Server::flush_stdout_and_stderr();
    }
}
impl Logger {
    pub fn init(level: LevelFilter) {
        set_logger(&LOGGER).unwrap();
        set_max_level(level);
    }
}
```
# Path: hyperlane-quick-start/plugin/log/static.rs
```rust
use super::*;
pub(super) static LOGGER: Logger = Logger;
pub(super) static FILE_LOGGER: Lazy<FileLogger> = Lazy::new(|| {
    let mut file_logger: FileLogger = FileLogger::default();
    file_logger.path(SERVER_LOG_DIR);
    file_logger.limit_file_size(SERVER_LOG_SIZE);
    file_logger
});
```
# Path: hyperlane-quick-start/src/main.rs
```rust
fn main() {
    hyperlane_init::framework::wait::run();
}
```
# Path: hyperlane-log/README.md
## hyperlane-log
[Official Documentation](https://docs.ltpp.vip/hyperlane-log/)
[Api Docs](https://docs.rs/hyperlane-log/latest/hyperlane_log/)
> A Rust logging library that supports both asynchronous and synchronous logging. It provides multiple log levels, such as error, info, and debug. Users can define custom log handling methods and configure log file paths. The library supports log rotation, automatically creating a new log file when the current file reaches the specified size limit. It allows flexible logging configurations, making it suitable for both high-performance asynchronous applications and traditional synchronous logging scenarios. The asynchronous mode utilizes Tokio's async channels for efficient log buffering, while the synchronous mode writes logs directly to the file system.
## Installation
To use this crate, you can run cmd:
```shell
cargo add hyperlane-log
```
## Log Storage Location Description
> Three directories will be created under the user-specified directory: one for error logs, one for info logs, and one for debug logs. Each of these directories will contain a subdirectory named by the date, and the log files within these subdirectories will be named in the format `timestamp.index.log`.
## Contact
# Path: hyperlane-log/src/lib.rs
```rust
pub(crate) mod cfg;
pub(crate) mod log;
pub use log::*;
pub(crate) use file_operation::*;
pub(crate) use hyperlane_time::*;
pub(crate) use std::fs::read_dir;
```
# Path: hyperlane-log/src/cfg.rs
```rust
#[cfg(test)]
#[tokio::test]
async fn test() {
    use crate::*;
    let log: FileLogger = FileLogger::new("./logs", 1_024_000);
    let trace_str: String = String::from("custom trace message");
    log.trace(trace_str, |trace| {
        let write_data: String = format!("User trace func => {trace:#?}\n");
        write_data
    });
    let debug_str: String = String::from("custom debug message");
    log.debug(debug_str, |debug| {
        let write_data: String = format!("User debug func => {debug:#?}\n");
        write_data
    });
    let info_str: String = String::from("custom info message");
    log.info(info_str, |info| {
        let write_data: String = format!("User info func => {info:?}\n");
        write_data
    });
    let warn_str: String = String::from("custom warn message");
    log.warn(warn_str, |warn| {
        let write_data: String = format!("User warn func => {warn:#?}\n");
        write_data
    });
    let error_str: String = String::from("custom error message");
    log.error(error_str, |error| {
        let write_data: String = format!("User error func => {error:?}\n");
        write_data
    });
    let async_trace_str: String = String::from("custom async trace message");
    log.async_trace(async_trace_str, |trace| {
        let write_data: String = format!("User trace func => {trace:#?}\n");
        write_data
    })
    .await;
    let async_debug_str: String = String::from("custom async debug message");
    log.async_debug(async_debug_str, |debug| {
        let write_data: String = format!("User debug func => {debug:#?}\n");
        write_data
    })
    .await;
    let async_info_str: String = String::from("custom async info message");
    log.async_info(async_info_str, |info| {
        let write_data: String = format!("User info func => {info:?}\n");
        write_data
    })
    .await;
    let async_warn_str: String = String::from("custom async warn message");
    log.async_warn(async_warn_str, |warn| {
        let write_data: String = format!("User warn func => {warn:#?}\n");
        write_data
    })
    .await;
    let async_error_str: String = String::from("custom async error message");
    log.async_error(async_error_str, |error| {
        let write_data: String = format!("User error func => {error:?}\n");
        write_data
    })
    .await;
}
#[cfg(test)]
#[tokio::test]
async fn test_more_log_first() {
    use crate::*;
    let log: FileLogger = FileLogger::new("./logs", DISABLE_LOG_FILE_SIZE);
    log.trace("trace data => ", |trace| {
        let write_data: String = format!("User trace func => {trace:#?}\n");
        write_data
    });
    log.debug("debug data => ", |debug| {
        let write_data: String = format!("User debug func => {debug:#?}\n");
        write_data
    });
    log.info("info data => ", |info| {
        let write_data: String = format!("User info func => {info:?}\n");
        write_data
    });
    log.warn("warn data => ", |warn| {
        let write_data: String = format!("User warn func => {warn:#?}\n");
        write_data
    });
    log.error("error data => ", |error| {
        let write_data: String = format!("User error func => {error:?}\n");
        write_data
    });
    log.async_trace("async trace data => ", |trace| {
        let write_data: String = format!("User trace func => {trace:#?}\n");
        write_data
    })
    .await;
    log.async_debug("async debug data => ", |debug| {
        let write_data: String = format!("User debug func => {debug:#?}\n");
        write_data
    })
    .await;
    log.async_info("async info data => ", |info| {
        let write_data: String = format!("User info func => {info:?}\n");
        write_data
    })
    .await;
    log.async_warn("async warn data => ", |warn| {
        let write_data: String = format!("User warn func => {warn:#?}\n");
        write_data
    })
    .await;
    log.async_error("async error data => ", |error| {
        let write_data: String = format!("User error func => {error:?}\n");
        write_data
    })
    .await;
}
#[cfg(test)]
#[tokio::test]
async fn test_more_log_second() {
    use crate::*;
    for _ in 0..10 {
        let log: FileLogger = FileLogger::new("./logs", 512_000);
        log.trace("trace data!\n", common_log);
        log.async_trace("async trace data!\n", common_log).await;
        log.debug("debug data!\n", common_log);
        log.async_debug("async debug data!\n", common_log).await;
        log.info("info data!\n", common_log);
        log.async_info("async info data!\n", common_log).await;
        log.warn("warn data!\n", common_log);
        log.async_warn("async warn data!\n", common_log).await;
        log.error("error data!\n", common_log);
        log.async_error("async error data!\n", common_log).await;
    }
}
```
# Path: hyperlane-log/src/log/trait.rs
```rust
pub trait FileLoggerFuncTrait<T: AsRef<str>>: Fn(T) -> String + Send + Sync {}
```
# Path: hyperlane-log/src/log/const.rs
```rust
pub const DEFAULT_LOG_DIR: &str = "./logs";
pub const LOG_EXTENSION: &str = "log";
pub const DEFAULT_LOG_FILE_START_IDX: usize = 1;
pub const DEFAULT_LOG_FILE_SIZE: usize = 1_024_000_000;
pub const DISABLE_LOG_FILE_SIZE: usize = 0;
pub(crate) const ROOT_PATH: &str = "/";
pub(crate) const POINT: &str = ".";
pub(crate) const BR: &str = "\n";
pub const TRACE_DIR: &str = "trace";
pub const DEBUG_DIR: &str = "debug";
pub const INFO_DIR: &str = "info";
pub const WARN_DIR: &str = "warn";
pub const ERROR_DIR: &str = "error";
```
# Path: hyperlane-log/src/log/mod.rs
```rust
pub(crate) mod r#const;
pub(crate) mod r#fn;
pub(crate) mod r#impl;
pub(crate) mod r#struct;
pub(crate) mod r#trait;
pub use r#const::*;
pub use r#fn::*;
pub use r#struct::*;
pub use r#trait::*;
```
# Path: hyperlane-log/src/log/struct.rs
```rust
#[derive(Clone)]
pub struct FileLogger {
    pub(super) path: String,
    pub(super) limit_file_size: usize,
}
```
# Path: hyperlane-log/src/log/fn.rs
```rust
use crate::*;
pub(crate) fn get_second_element_from_filename(dir_path: &str) -> usize {
    let mut res_idx: usize = DEFAULT_LOG_FILE_START_IDX;
    if let Ok(entries) = read_dir(dir_path) {
        for entry in entries.filter_map(Result::ok) {
            let file_name: String = entry.file_name().to_string_lossy().to_string();
            let parts: Vec<&str> = file_name.split(POINT).collect();
            if parts.len() > 1
                && let Ok(second_element) = parts[1].parse::<usize>()
            {
                res_idx = second_element.max(res_idx);
            }
        }
    }
    res_idx.max(DEFAULT_LOG_FILE_START_IDX)
}
#[inline(always)]
pub(crate) fn get_file_name(idx: usize) -> String {
    format!(
        "{}{}{}{}{}{}",
        ROOT_PATH,
        date(),
        POINT,
        idx,
        POINT,
        LOG_EXTENSION
    )
}
#[inline(always)]
pub(crate) fn get_file_dir_name() -> String {
    format!("{}{}", ROOT_PATH, date())
}
pub(crate) fn get_log_path(system_dir: &str, base_path: &str, limit_file_size: &usize) -> String {
    let mut combined_path: String = base_path.trim_end_matches(ROOT_PATH).to_string();
    if !system_dir.starts_with(ROOT_PATH) {
        combined_path.push_str(ROOT_PATH);
    }
    combined_path.push_str(
        system_dir
            .trim_start_matches(ROOT_PATH)
            .trim_end_matches(ROOT_PATH),
    );
    combined_path.push_str(&get_file_dir_name());
    let idx: usize = get_second_element_from_filename(&combined_path);
    let mut combined_path_clone: String = combined_path.clone();
    combined_path.push_str(&get_file_name(idx));
    let file_size: usize = get_file_size(&combined_path).unwrap_or_default() as usize;
    if &file_size <= limit_file_size {
        return combined_path;
    }
    combined_path_clone.push_str(&get_file_name(idx + 1));
    combined_path_clone
}
#[inline(always)]
pub fn common_log<T: AsRef<str>>(data: T) -> String {
    let mut log_string: String = String::new();
    for line in data.as_ref().lines() {
        let line_string: String = format!("{} {}{}", time(), line, BR);
        log_string.push_str(&line_string);
    }
    log_string
}
#[inline(always)]
pub fn log_handler<T: AsRef<str>>(log_data: T) -> String {
    common_log(log_data)
}
```
# Path: hyperlane-log/src/log/impl.rs
```rust
use crate::*;
impl<F, T> FileLoggerFuncTrait<T> for F
where
    F: Fn(T) -> String + Send + Sync,
    T: AsRef<str>,
{
}
impl Default for FileLogger {
    #[inline(always)]
    fn default() -> Self {
        Self {
            path: DEFAULT_LOG_DIR.to_owned(),
            limit_file_size: DEFAULT_LOG_FILE_SIZE,
        }
    }
}
impl FileLogger {
    #[inline(always)]
    pub fn new<P: AsRef<str>>(path: P, limit_file_size: usize) -> Self {
        Self {
            path: path.as_ref().to_owned(),
            limit_file_size,
        }
    }
    #[inline(always)]
    pub fn path<P: AsRef<str>>(&mut self, path: P) -> &mut Self {
        self.path = path.as_ref().to_owned();
        self
    }
    #[inline(always)]
    pub fn limit_file_size(&mut self, limit_file_size: usize) -> &mut Self {
        self.limit_file_size = limit_file_size;
        self
    }
    #[inline(always)]
    pub fn is_enable(&self) -> bool {
        self.limit_file_size != DISABLE_LOG_FILE_SIZE
    }
    #[inline(always)]
    pub fn is_disable(&self) -> bool {
        !self.is_enable()
    }
    fn write_sync<T, L>(&self, data: T, func: L, dir: &str) -> &Self
    where
        T: AsRef<str>,
        L: FileLoggerFuncTrait<T>,
    {
        if self.is_disable() {
            return self;
        }
        let out: String = func(data);
        let path: String = get_log_path(dir, &self.path, &self.limit_file_size);
        let _ = append_to_file(&path, out.as_bytes());
        self
    }
    async fn write_async<T, L>(&self, data: T, func: L, dir: &str) -> &Self
    where
        T: AsRef<str>,
        L: FileLoggerFuncTrait<T>,
    {
        if self.is_disable() {
            return self;
        }
        let out: String = func(data);
        let path: String = get_log_path(dir, &self.path, &self.limit_file_size);
        let _ = async_append_to_file(&path, out.as_bytes()).await;
        self
    }
    pub fn trace<T, L>(&self, data: T, func: L) -> &Self
    where
        T: AsRef<str>,
        L: FileLoggerFuncTrait<T>,
    {
        self.write_sync(data, func, TRACE_DIR)
    }
    pub async fn async_trace<T, L>(&self, data: T, func: L) -> &Self
    where
        T: AsRef<str>,
        L: FileLoggerFuncTrait<T>,
    {
        self.write_async(data, func, TRACE_DIR).await
    }
    pub fn debug<T, L>(&self, data: T, func: L) -> &Self
    where
        T: AsRef<str>,
        L: FileLoggerFuncTrait<T>,
    {
        self.write_sync(data, func, DEBUG_DIR)
    }
    pub async fn async_debug<T, L>(&self, data: T, func: L) -> &Self
    where
        T: AsRef<str>,
        L: FileLoggerFuncTrait<T>,
    {
        self.write_async(data, func, DEBUG_DIR).await
    }
    pub fn info<T, L>(&self, data: T, func: L) -> &Self
    where
        T: AsRef<str>,
        L: FileLoggerFuncTrait<T>,
    {
        self.write_sync(data, func, INFO_DIR)
    }
    pub async fn async_info<T, L>(&self, data: T, func: L) -> &Self
    where
        T: AsRef<str>,
        L: FileLoggerFuncTrait<T>,
    {
        self.write_async(data, func, INFO_DIR).await
    }
    pub fn warn<T, L>(&self, data: T, func: L) -> &Self
    where
        T: AsRef<str>,
        L: FileLoggerFuncTrait<T>,
    {
        self.write_sync(data, func, WARN_DIR)
    }
    pub async fn async_warn<T, L>(&self, data: T, func: L) -> &Self
    where
        T: AsRef<str>,
        L: FileLoggerFuncTrait<T>,
    {
        self.write_async(data, func, WARN_DIR).await
    }
    pub fn error<T, L>(&self, data: T, func: L) -> &Self
    where
        T: AsRef<str>,
        L: FileLoggerFuncTrait<T>,
    {
        self.write_sync(data, func, ERROR_DIR)
    }
    pub async fn async_error<T, L>(&self, data: T, func: L) -> &Self
    where
        T: AsRef<str>,
        L: FileLoggerFuncTrait<T>,
    {
        self.write_async(data, func, ERROR_DIR).await
    }
}
```
# Path: hyperlane/README.md
## hyperlane
[Official Documentation](https://docs.ltpp.vip/hyperlane/)
[Api Docs](https://docs.rs/hyperlane/latest/hyperlane/)
> A lightweight, high-performance, and cross-platform Rust HTTP server library built on Tokio. It simplifies modern web service development by providing built-in support for middleware, WebSocket, Server-Sent Events (SSE), and raw TCP communication. With a unified and ergonomic API across Windows, Linux, and MacOS, it enables developers to build robust, scalable, and event-driven network applications with minimal overhead and maximum flexibility.
## Installation
To use this crate, you can run cmd:
```shell
cargo add hyperlane
```
## Quick start
- [hyperlane-quick-start git](https://github.com/hyperlane-dev/hyperlane-quick-start)
- [hyperlane-quick-start docs](https://docs.ltpp.vip/hyperlane/quick-start/)
```sh
git clone https://github.com/hyperlane-dev/hyperlane-quick-start.git
```
## Contact
# Path: hyperlane/src/lib.rs
```rust
mod attribute;
mod config;
mod context;
mod error;
mod hook;
mod panic;
mod route;
mod server;
#[cfg(test)]
mod tests;
pub use attribute::*;
pub use config::*;
pub use context::*;
pub use error::*;
pub use hook::*;
pub use panic::*;
pub use route::*;
pub use server::*;
pub use http_type::*;
pub use inventory;
pub(crate) use std::{
    any::Any,
    borrow::Borrow,
    cmp::Ordering,
    collections::{HashMap, HashSet},
    future::Future,
    hash::{Hash, Hasher},
    io::{self, Write, stderr, stdout},
    net::SocketAddr,
    pin::Pin,
    sync::Arc,
};
pub(crate) use inventory::collect;
pub(crate) use lombok_macros::*;
pub(crate) use regex::Regex;
pub(crate) use serde::{Deserialize, Serialize, de::DeserializeOwned};
pub(crate) use tokio::{
    net::{TcpListener, TcpStream},
    spawn,
    sync::{
        RwLockReadGuard, RwLockWriteGuard,
        watch::{Receiver, Sender, channel},
    },
    task::{JoinError, JoinHandle},
};
#[cfg(test)]
pub(crate) use std::time::{Duration, Instant};
```
# Path: hyperlane/src/hook/trait.rs
```rust
use crate::*;
pub trait FnContextSendSync<R>: Fn(Context) -> R + Send + Sync {}
pub trait FnContextPinBoxSendSync<T>: FnContextSendSync<SendableAsyncTask<T>> {}
pub trait FnContextSendSyncStatic<Fut, T>: FnContextSendSync<Fut> + 'static
where
    Fut: Future<Output = T> + Send,
{
}
```
# Path: hyperlane/src/hook/mod.rs
```rust
pub(crate) mod r#enum;
pub(crate) mod r#fn;
pub(crate) mod r#impl;
pub(crate) mod r#struct;
pub(crate) mod r#trait;
pub(crate) mod r#type;
pub use r#enum::*;
pub use r#fn::*;
pub use r#struct::*;
pub use r#trait::*;
pub use r#type::*;
```
# Path: hyperlane/src/hook/enum.rs
```rust
use crate::*;
#[derive(Clone, Debug, Copy, DisplayDebug)]
pub enum HookType {
    TaskPanic(Option<isize>, ServerHookHandlerFactory),
    RequestError(Option<isize>, ServerHookHandlerFactory),
    RequestMiddleware(Option<isize>, ServerHookHandlerFactory),
    Route(&'static str, ServerHookHandlerFactory),
    ResponseMiddleware(Option<isize>, ServerHookHandlerFactory),
}
```
# Path: hyperlane/src/hook/struct.rs
```rust
use crate::*;
#[derive(Clone, Copy, Debug, DisplayDebug, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct DefaultServerHook;
#[derive(Clone, CustomDebug, DisplayDebug, Getter, Setter)]
pub struct ServerControlHook {
    #[debug(skip)]
    #[get(pub)]
    #[set(pub(crate))]
    pub(super) wait_hook: SharedAsyncTaskFactory<()>,
    #[debug(skip)]
    #[get(pub)]
    #[set(pub(crate))]
    pub(super) shutdown_hook: SharedAsyncTaskFactory<()>,
}
```
# Path: hyperlane/src/hook/fn.rs
```rust
use crate::*;
#[inline(always)]
pub fn server_hook_factory<R>() -> ServerHookHandler
where
    R: ServerHook,
{
    Arc::new(move |ctx: &Context| -> SendableAsyncTask<()> {
        let ctx: Context = ctx.clone();
        Box::pin(async move {
            R::new(&ctx).await.handle(&ctx).await;
        })
    })
}
#[inline(always)]
pub fn assert_hook_unique_order(list: Vec<HookType>) {
    let mut seen: HashSet<(HookType, isize)> = HashSet::new();
    list.iter().for_each(|hook| {
        if let Some(order) = hook.try_get_order()
            && !seen.insert((*hook, order))
        {
            panic!("Duplicate hook detected: {} with order {}", hook, order);
        }
    });
}
```
# Path: hyperlane/src/hook/impl.rs
```rust
use crate::*;
impl<F, R> FnContextSendSync<R> for F where F: Fn(Context) -> R + Send + Sync {}
impl<F, T> FnContextPinBoxSendSync<T> for F where F: FnContextSendSync<SendableAsyncTask<T>> {}
impl<F, Fut, T> FnContextSendSyncStatic<Fut, T> for F
where
    F: FnContextSendSync<Fut> + 'static,
    Fut: Future<Output = T> + Send,
{
}
impl<T, R> FutureSendStatic<R> for T where T: Future<Output = R> + Send + 'static {}
impl<T, O> FutureSend<O> for T where T: Future<Output = O> + Send {}
impl<T, O> FnPinBoxFutureSend<O> for T where T: Fn() -> SendableAsyncTask<O> + Send + Sync {}
impl Default for ServerControlHook {
    #[inline(always)]
    fn default() -> Self {
        Self {
            wait_hook: Arc::new(|| Box::pin(async {})),
            shutdown_hook: Arc::new(|| Box::pin(async {})),
        }
    }
}
impl ServerControlHook {
    pub async fn wait(&self) {
        self.get_wait_hook()().await;
    }
    pub async fn shutdown(&self) {
        self.get_shutdown_hook()().await;
    }
}
impl PartialEq for HookType {
    #[inline(always)]
    fn eq(&self, other: &Self) -> bool {
        match (self, other) {
            (HookType::TaskPanic(order1, factory1), HookType::TaskPanic(order2, factory2)) => {
                order1 == order2 && std::ptr::fn_addr_eq(*factory1, *factory2)
            }
            (
                HookType::RequestError(order1, factory1),
                HookType::RequestError(order2, factory2),
            ) => order1 == order2 && std::ptr::fn_addr_eq(*factory1, *factory2),
            (
                HookType::RequestMiddleware(order1, factory1),
                HookType::RequestMiddleware(order2, factory2),
            ) => order1 == order2 && std::ptr::fn_addr_eq(*factory1, *factory2),
            (HookType::Route(path1, factory1), HookType::Route(path2, factory2)) => {
                path1 == path2 && std::ptr::fn_addr_eq(*factory1, *factory2)
            }
            (
                HookType::ResponseMiddleware(order1, factory1),
                HookType::ResponseMiddleware(order2, factory2),
            ) => order1 == order2 && std::ptr::fn_addr_eq(*factory1, *factory2),
            _ => false,
        }
    }
}
impl Eq for HookType {}
impl Hash for HookType {
    #[inline(always)]
    fn hash<H: Hasher>(&self, state: &mut H) {
        match self {
            HookType::TaskPanic(order, factory) => {
                0u8.hash(state);
                order.hash(state);
                (factory as *const fn() -> ServerHookHandler).hash(state);
            }
            HookType::RequestError(order, factory) => {
                1u8.hash(state);
                order.hash(state);
                (factory as *const fn() -> ServerHookHandler).hash(state);
            }
            HookType::RequestMiddleware(order, factory) => {
                2u8.hash(state);
                order.hash(state);
                (factory as *const fn() -> ServerHookHandler).hash(state);
            }
            HookType::Route(path, factory) => {
                3u8.hash(state);
                path.hash(state);
                (factory as *const fn() -> ServerHookHandler).hash(state);
            }
            HookType::ResponseMiddleware(order, factory) => {
                4u8.hash(state);
                order.hash(state);
                (factory as *const fn() -> ServerHookHandler).hash(state);
            }
        }
    }
}
impl HookType {
    #[inline(always)]
    pub fn try_get_order(&self) -> Option<isize> {
        match *self {
            HookType::RequestMiddleware(order, _)
            | HookType::ResponseMiddleware(order, _)
            | HookType::TaskPanic(order, _)
            | HookType::RequestError(order, _) => order,
            _ => None,
        }
    }
    #[inline(always)]
    pub fn try_get_hook(&self) -> Option<ServerHookHandlerFactory> {
        match *self {
            HookType::RequestMiddleware(_, hook)
            | HookType::ResponseMiddleware(_, hook)
            | HookType::TaskPanic(_, hook)
            | HookType::RequestError(_, hook) => Some(hook),
            _ => None,
        }
    }
}
impl ServerHook for DefaultServerHook {
    async fn new(_: &Context) -> Self {
        Self
    }
    async fn handle(self, _: &Context) {}
}
```
# Path: hyperlane/src/hook/type.rs
```rust
use crate::*;
pub type HookHandler<T> = Arc<dyn FnContextPinBoxSendSync<T>>;
pub type HookHandlerChain<T> = Vec<HookHandler<T>>;
pub type AsyncTask = Pin<Box<dyn Future<Output = ()> + Send + 'static>>;
pub type SendableAsyncTask<T> = Pin<Box<dyn Future<Output = T> + Send>>;
pub type SharedAsyncTaskFactory<T> = Arc<dyn FnPinBoxFutureSend<T>>;
pub type ServerHookHandlerFactory = fn() -> ServerHookHandler;
pub type ServerHookHandler = Arc<dyn Fn(&Context) -> SendableAsyncTask<()> + Send + Sync>;
pub type ServerHookList = Vec<ServerHookHandler>;
pub type ServerHookMap = HashMapXxHash3_64<String, ServerHookHandler>;
pub type ServerHookPatternRoute = HashMapXxHash3_64<usize, Vec<(RoutePattern, ServerHookHandler)>>;
```
# Path: hyperlane/src/server/mod.rs
```rust
pub(crate) mod r#impl;
pub(crate) mod r#struct;
pub(crate) mod r#type;
pub use r#struct::*;
pub(crate) use r#type::*;
```
# Path: hyperlane/src/server/struct.rs
```rust
use crate::*;
#[derive(Clone, CustomDebug, DisplayDebug, Getter)]
pub(crate) struct HandlerState {
    pub(super) stream: ArcRwLockStream,
    pub(super) request_config: RequestConfig,
}
#[derive(Data, Clone, CustomDebug, DisplayDebug)]
pub(crate) struct ServerInner {
    #[get(pub(super))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    pub(super) config: ServerConfigInner,
    #[get(pub(super))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    pub(super) route_matcher: RouteMatcher,
    #[debug(skip)]
    #[get(pub(super))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    pub(super) request_error: ServerHookList,
    #[debug(skip)]
    #[get(pub(super))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    pub(super) task_panic: ServerHookList,
    #[debug(skip)]
    #[get(pub(super))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    pub(super) request_middleware: ServerHookList,
    #[debug(skip)]
    #[get(pub(super))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    pub(super) response_middleware: ServerHookList,
}
#[derive(Clone, Getter, CustomDebug, DisplayDebug, Default)]
pub struct Server(#[get(pub(super))] pub(super) SharedServerState);
```
# Path: hyperlane/src/server/impl.rs
```rust
use crate::*;
impl Default for ServerInner {
    #[inline(always)]
    fn default() -> Self {
        Self {
            config: ServerConfigInner::default(),
            task_panic: vec![],
            request_error: vec![],
            route_matcher: RouteMatcher::new(),
            request_middleware: vec![],
            response_middleware: vec![],
        }
    }
}
impl PartialEq for ServerInner {
    fn eq(&self, other: &Self) -> bool {
        self.config == other.config
            && self.route_matcher == other.route_matcher
            && self.task_panic.len() == other.task_panic.len()
            && self.request_error.len() == other.request_error.len()
            && self.request_middleware.len() == other.request_middleware.len()
            && self.response_middleware.len() == other.response_middleware.len()
            && self
                .task_panic
                .iter()
                .zip(other.task_panic.iter())
                .all(|(a, b)| Arc::ptr_eq(a, b))
            && self
                .request_error
                .iter()
                .zip(other.request_error.iter())
                .all(|(a, b)| Arc::ptr_eq(a, b))
            && self
                .request_middleware
                .iter()
                .zip(other.request_middleware.iter())
                .all(|(a, b)| Arc::ptr_eq(a, b))
            && self
                .response_middleware
                .iter()
                .zip(other.response_middleware.iter())
                .all(|(a, b)| Arc::ptr_eq(a, b))
    }
}
impl Eq for ServerInner {}
impl PartialEq for Server {
    #[inline(always)]
    fn eq(&self, other: &Self) -> bool {
        if Arc::ptr_eq(self.get_0(), other.get_0()) {
            return true;
        }
        if let (Ok(s), Ok(o)) = (self.get_0().try_read(), other.get_0().try_read()) {
            *s == *o
        } else {
            false
        }
    }
}
impl Eq for Server {}
impl HandlerState {
    #[inline(always)]
    pub(super) fn new(stream: ArcRwLockStream, request_config: RequestConfig) -> Self {
        Self {
            stream,
            request_config,
        }
    }
}
impl Server {
    pub async fn new() -> Self {
        let server: ServerInner = ServerInner::default();
        Self(arc_rwlock(server))
    }
    pub async fn from(config: ServerConfig) -> Self {
        let server: Self = Self::new().await;
        server.config(config).await;
        server
    }
    pub(super) async fn read(&self) -> ServerStateReadGuard<'_> {
        self.get_0().read().await
    }
    async fn write(&self) -> ServerStateWriteGuard<'_> {
        self.get_0().write().await
    }
    pub async fn get_route_matcher(&self) -> RouteMatcher {
        self.read().await.get_route_matcher().clone()
    }
    pub async fn handle_hook(&self, hook: HookType) {
        match hook {
            HookType::TaskPanic(_, hook) => {
                self.write().await.get_mut_task_panic().push(hook());
            }
            HookType::RequestError(_, hook) => {
                self.write().await.get_mut_request_error().push(hook());
            }
            HookType::RequestMiddleware(_, hook) => {
                self.write().await.get_mut_request_middleware().push(hook());
            }
            HookType::Route(path, hook) => {
                self.write()
                    .await
                    .get_mut_route_matcher()
                    .add(path, hook())
                    .unwrap();
            }
            HookType::ResponseMiddleware(_, hook) => {
                self.write()
                    .await
                    .get_mut_response_middleware()
                    .push(hook());
            }
        };
    }
    pub async fn config_str<C: ToString>(&self, config_str: C) -> &Self {
        let config: ServerConfig = ServerConfig::from_json_str(&config_str.to_string()).unwrap();
        self.write().await.set_config(config.get_inner().await);
        self
    }
    pub async fn config(&self, config: ServerConfig) -> &Self {
        self.write().await.set_config(config.get_inner().await);
        self
    }
    pub async fn task_panic<S>(&self) -> &Self
    where
        S: ServerHook,
    {
        self.write()
            .await
            .get_mut_task_panic()
            .push(server_hook_factory::<S>());
        self
    }
    pub async fn request_error<S>(&self) -> &Self
    where
        S: ServerHook,
    {
        self.write()
            .await
            .get_mut_request_error()
            .push(server_hook_factory::<S>());
        self
    }
    pub async fn route<S>(&self, path: impl ToString) -> &Self
    where
        S: ServerHook,
    {
        self.write()
            .await
            .get_mut_route_matcher()
            .add(&path.to_string(), server_hook_factory::<S>())
            .unwrap();
        self
    }
    pub async fn request_middleware<S>(&self) -> &Self
    where
        S: ServerHook,
    {
        self.write()
            .await
            .get_mut_request_middleware()
            .push(server_hook_factory::<S>());
        self
    }
    pub async fn response_middleware<S>(&self) -> &Self
    where
        S: ServerHook,
    {
        self.write()
            .await
            .get_mut_response_middleware()
            .push(server_hook_factory::<S>());
        self
    }
    #[inline(always)]
    pub fn format_host_port<H: ToString>(host: H, port: u16) -> String {
        format!("{}{COLON}{port}", host.to_string())
    }
    #[inline(always)]
    pub fn try_flush_stdout() -> io::Result<()> {
        stdout().flush()
    }
    #[inline(always)]
    pub fn flush_stdout() {
        stdout().flush().unwrap();
    }
    #[inline(always)]
    pub fn try_flush_stderr() -> io::Result<()> {
        stderr().flush()
    }
    #[inline(always)]
    pub fn flush_stderr() {
        stderr().flush().unwrap();
    }
    #[inline(always)]
    pub fn try_flush_stdout_and_stderr() -> io::Result<()> {
        Self::try_flush_stdout()?;
        Self::try_flush_stderr()
    }
    #[inline(always)]
    pub fn flush_stdout_and_stderr() {
        Self::flush_stdout();
        Self::flush_stderr();
    }
    async fn handle_panic_with_context(&self, ctx: &Context, panic: &PanicData) {
        let panic_clone: PanicData = panic.clone();
        ctx.cancel_aborted().await.set_task_panic(panic_clone).await;
        for hook in self.read().await.get_task_panic().iter() {
            Box::pin(self.task_handler(ctx, hook, false)).await;
            if ctx.get_aborted().await {
                return;
            }
        }
    }
    async fn handle_task_panic(&self, ctx: &Context, join_error: JoinError) {
        let panic: PanicData = PanicData::from_join_error(join_error);
        ctx.set_response_status_code(HttpStatus::InternalServerError.code())
            .await;
        self.handle_panic_with_context(ctx, &panic).await;
    }
    async fn task_handler(&self, ctx: &Context, hook: &ServerHookHandler, progress: bool) {
        if let Err(join_error) = spawn(hook(ctx)).await
            && join_error.is_panic()
        {
            if progress {
                Box::pin(self.handle_task_panic(ctx, join_error)).await;
            } else {
                eprintln!("Panic occurred in panic handler: {:?}", join_error);
                let _ = Self::try_flush_stdout_and_stderr();
            }
        }
    }
    async fn create_tcp_listener(&self) -> Result<TcpListener, ServerError> {
        let config: ServerConfigInner = self.read().await.get_config().clone();
        let host: String = config.get_host().clone();
        let port: u16 = *config.get_port();
        let addr: String = Self::format_host_port(host, port);
        TcpListener::bind(&addr)
            .await
            .map_err(|error| ServerError::TcpBind(error.to_string()))
    }
    async fn accept_connections(&self, tcp_listener: &TcpListener) -> Result<(), ServerError> {
        while let Ok((stream, _socket_addr)) = tcp_listener.accept().await {
            self.configure_stream(&stream).await;
            let stream: ArcRwLockStream = ArcRwLockStream::from_stream(stream);
            self.spawn_connection_handler(stream).await;
        }
        Ok(())
    }
    async fn configure_stream(&self, stream: &TcpStream) {
        let server_inner: ServerStateReadGuard = self.read().await;
        let config: &ServerConfigInner = server_inner.get_config();
        if let Some(nodelay) = config.get_nodelay() {
            let _ = stream.set_nodelay(*nodelay);
        }
        if let Some(ttl) = config.get_ttl() {
            let _ = stream.set_ttl(*ttl);
        }
    }
    async fn spawn_connection_handler(&self, stream: ArcRwLockStream) {
        let server: Server = self.clone();
        let request_config: RequestConfig = *self.read().await.get_config().get_request_config();
        spawn(async move {
            server.handle_connection(stream, request_config).await;
        });
    }
    pub async fn handle_request_error(&self, ctx: &Context, error: &RequestError) {
        ctx.cancel_aborted()
            .await
            .set_request_error_data(error.clone())
            .await;
        for hook in self.read().await.get_request_error().iter() {
            self.task_handler(ctx, hook, true).await;
            if ctx.get_aborted().await {
                return;
            }
        }
    }
    async fn handle_connection(&self, stream: ArcRwLockStream, request_config: RequestConfig) {
        match Request::http_from_stream(&stream, &request_config).await {
            Ok(request) => {
                let hook: HandlerState = HandlerState::new(stream, request_config);
                self.handle_http_requests(&hook, &request).await;
            }
            Err(error) => {
                self.handle_request_error(&stream.into(), &error).await;
            }
        }
    }
    async fn request_hook(&self, state: &HandlerState, request: &Request) -> bool {
        let route: &str = request.get_path();
        let ctx: &Context = &Context::new(state.get_stream(), request);
        let keep_alive: bool = request.is_enable_keep_alive();
        if self.handle_request_middleware(ctx).await {
            return ctx.is_keep_alive(keep_alive).await;
        }
        if self.handle_route_matcher(ctx, route).await {
            return ctx.is_keep_alive(keep_alive).await;
        }
        if self.handle_response_middleware(ctx).await {
            return ctx.is_keep_alive(keep_alive).await;
        }
        if let Some(panic) = ctx.try_get_task_panic_data().await {
            ctx.set_response_status_code(HttpStatus::InternalServerError.code())
                .await;
            self.handle_panic_with_context(ctx, &panic).await;
        }
        ctx.is_keep_alive(keep_alive).await
    }
    async fn handle_http_requests(&self, state: &HandlerState, request: &Request) {
        if !self.request_hook(state, request).await {
            return;
        }
        let stream: &ArcRwLockStream = state.get_stream();
        let request_config: &RequestConfig = state.get_request_config();
        loop {
            match Request::http_from_stream(stream, request_config).await {
                Ok(new_request) => {
                    if !self.request_hook(state, &new_request).await {
                        return;
                    }
                }
                Err(error) => {
                    self.handle_request_error(&state.get_stream().into(), &error)
                        .await;
                    return;
                }
            }
        }
    }
    pub(super) async fn handle_request_middleware(&self, ctx: &Context) -> bool {
        for hook in self.read().await.get_request_middleware().iter() {
            self.task_handler(ctx, hook, true).await;
            if ctx.get_aborted().await {
                return true;
            }
        }
        false
    }
    pub(super) async fn handle_route_matcher(&self, ctx: &Context, path: &str) -> bool {
        if let Some(hook) = self
            .read()
            .await
            .get_route_matcher()
            .try_resolve_route(ctx, path)
            .await
        {
            self.task_handler(ctx, &hook, true).await;
            if ctx.get_aborted().await {
                return true;
            }
        }
        false
    }
    pub(super) async fn handle_response_middleware(&self, ctx: &Context) -> bool {
        for hook in self.read().await.get_response_middleware().iter() {
            self.task_handler(ctx, hook, true).await;
            if ctx.get_aborted().await {
                return true;
            }
        }
        false
    }
    pub async fn run(&self) -> Result<ServerControlHook, ServerError> {
        let tcp_listener: TcpListener = self.create_tcp_listener().await?;
        let server: Server = self.clone();
        let (wait_sender, wait_receiver) = channel(());
        let (shutdown_sender, mut shutdown_receiver) = channel(());
        let accept_connections: JoinHandle<()> = spawn(async move {
            let _ = server.accept_connections(&tcp_listener).await;
            let _ = wait_sender.send(());
        });
        let wait_hook: SharedAsyncTaskFactory<()> = Arc::new(move || {
            let mut wait_receiver_clone: Receiver<()> = wait_receiver.clone();
            Box::pin(async move {
                let _ = wait_receiver_clone.changed().await;
            })
        });
        let shutdown_hook: SharedAsyncTaskFactory<()> = Arc::new(move || {
            let shutdown_sender_clone: Sender<()> = shutdown_sender.clone();
            Box::pin(async move {
                let _ = shutdown_sender_clone.send(());
            })
        });
        spawn(async move {
            let _ = shutdown_receiver.changed().await;
            accept_connections.abort();
        });
        let mut server_control_hook: ServerControlHook = ServerControlHook::default();
        server_control_hook.set_shutdown_hook(shutdown_hook);
        server_control_hook.set_wait_hook(wait_hook);
        Ok(server_control_hook)
    }
}
```
# Path: hyperlane/src/server/type.rs
```rust
use crate::*;
pub(crate) type SharedServerState = ArcRwLock<ServerInner>;
pub(crate) type SharedServerConfig = ArcRwLock<ServerConfigInner>;
pub(crate) type ServerStateReadGuard<'a> = RwLockReadGuard<'a, ServerInner>;
pub(crate) type ServerStateWriteGuard<'a> = RwLockWriteGuard<'a, ServerInner>;
```
# Path: hyperlane/src/panic/mod.rs
```rust
pub(crate) mod r#impl;
pub(crate) mod r#struct;
pub use r#struct::*;
```
# Path: hyperlane/src/panic/struct.rs
```rust
use crate::*;
#[derive(CustomDebug, Default, PartialEq, Eq, Clone, Getter, DisplayDebug, Setter)]
pub struct PanicData {
    #[get(pub)]
    #[set(pub(crate))]
    pub(super) message: Option<String>,
    #[get(pub)]
    #[set(pub(crate))]
    pub(super) location: Option<String>,
    #[get(pub)]
    #[set(pub(crate))]
    pub(super) payload: Option<String>,
}
```
# Path: hyperlane/src/panic/impl.rs
```rust
use crate::*;
impl PanicData {
    #[inline(always)]
    pub(crate) fn new(
        message: Option<String>,
        location: Option<String>,
        payload: Option<String>,
    ) -> Self {
        Self {
            message,
            location,
            payload,
        }
    }
    #[inline(always)]
    fn try_extract_panic_message(panic_payload: &dyn Any) -> Option<String> {
        if let Some(s) = panic_payload.downcast_ref::<&str>() {
            Some(s.to_string())
        } else {
            panic_payload.downcast_ref::<String>().cloned()
        }
    }
    pub(crate) fn from_join_error(join_error: JoinError) -> Self {
        let default_message: String = join_error.to_string();
        let mut message: Option<String> = if let Ok(panic_join_error) = join_error.try_into_panic()
        {
            Self::try_extract_panic_message(&panic_join_error)
        } else {
            None
        };
        if (message.is_none() || message.clone().unwrap_or_default().is_empty())
            && !default_message.is_empty()
        {
            message = Some(default_message);
        }
        let panic: PanicData = PanicData::new(message, None, None);
        panic
    }
}
```
# Path: hyperlane/src/context/mod.rs
```rust
pub(crate) mod r#impl;
pub(crate) mod r#struct;
pub(crate) mod r#type;
pub use r#struct::*;
pub(crate) use r#type::*;
```
# Path: hyperlane/src/context/struct.rs
```rust
use crate::*;
#[derive(Clone, Data, Default, CustomDebug, DisplayDebug)]
pub(crate) struct ContextInner {
    #[get(pub(super))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    aborted: bool,
    #[get(pub(super))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    closed: bool,
    #[get(pub(super))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    stream: Option<ArcRwLockStream>,
    #[get(pub(super))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    request: Request,
    #[get(pub(super))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    response: Response,
    #[get(pub(super))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    route_params: RouteParams,
    #[get(pub(super))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    attributes: ThreadSafeAttributeStore,
}
#[derive(Clone, Default, Getter, CustomDebug, DisplayDebug)]
pub struct Context(#[get(pub(super))] pub(super) ArcRwLock<ContextInner>);
```
# Path: hyperlane/src/context/impl.rs
```rust
use crate::*;
impl From<ContextInner> for Context {
    #[inline(always)]
    fn from(ctx: ContextInner) -> Self {
        Self(arc_rwlock(ctx))
    }
}
impl From<&ArcRwLockStream> for Context {
    #[inline(always)]
    fn from(stream: &ArcRwLockStream) -> Self {
        let request: Request = Request::default();
        let mut internal_ctx: ContextInner = ContextInner::default();
        internal_ctx
            .set_stream(Some(stream.clone()))
            .set_request(request.clone())
            .get_mut_response()
            .set_version(request.get_version().clone());
        internal_ctx.into()
    }
}
impl From<ArcRwLockStream> for Context {
    #[inline(always)]
    fn from(stream: ArcRwLockStream) -> Self {
        (&stream).into()
    }
}
impl Context {
    #[inline(always)]
    pub(crate) fn new(stream: &ArcRwLockStream, request: &Request) -> Context {
        let mut internal_ctx: ContextInner = ContextInner::default();
        internal_ctx
            .set_stream(Some(stream.clone()))
            .set_request(request.clone())
            .get_mut_response()
            .set_version(request.get_version().clone());
        internal_ctx.into()
    }
    async fn read(&self) -> ContextReadGuard<'_> {
        self.get_0().read().await
    }
    async fn write(&self) -> ContextWriteGuard<'_> {
        self.get_0().write().await
    }
    pub async fn http_from_stream(
        &self,
        request_config: RequestConfig,
    ) -> Result<Request, RequestError> {
        if self.get_aborted().await {
            return Err(RequestError::RequestAborted(HttpStatus::BadRequest));
        }
        if let Some(stream) = self.try_get_stream().await.as_ref() {
            let request_res: Result<Request, RequestError> =
                Request::http_from_stream(stream, &request_config).await;
            if let Ok(request) = request_res.as_ref() {
                self.set_request(request).await;
            }
            return request_res;
        };
        Err(RequestError::GetTcpStream(HttpStatus::BadRequest))
    }
    pub async fn ws_from_stream(
        &self,
        request_config: RequestConfig,
    ) -> Result<Request, RequestError> {
        if self.get_aborted().await {
            return Err(RequestError::RequestAborted(HttpStatus::BadRequest));
        }
        if let Some(stream) = self.try_get_stream().await.as_ref() {
            let mut last_request: Request = self.get_request().await;
            let request_res: Result<Request, RequestError> =
                last_request.ws_from_stream(stream, &request_config).await;
            match request_res.as_ref() {
                Ok(request) => {
                    self.set_request(request).await;
                }
                Err(_) => {
                    self.set_request(&last_request).await;
                }
            }
            return request_res;
        };
        Err(RequestError::GetTcpStream(HttpStatus::BadRequest))
    }
    pub async fn get_aborted(&self) -> bool {
        *self.read().await.get_aborted()
    }
    pub async fn set_aborted(&self, aborted: bool) -> &Self {
        self.write().await.set_aborted(aborted);
        self
    }
    pub async fn aborted(&self) -> &Self {
        self.set_aborted(true).await;
        self
    }
    pub async fn cancel_aborted(&self) -> &Self {
        self.set_aborted(false).await;
        self
    }
    pub async fn get_closed(&self) -> bool {
        *self.read().await.get_closed()
    }
    pub async fn set_closed(&self, closed: bool) -> &Self {
        self.write().await.set_closed(closed);
        self
    }
    pub async fn closed(&self) -> &Self {
        self.set_closed(true).await;
        self
    }
    pub async fn cancel_closed(&self) -> &Self {
        self.set_closed(false).await;
        self
    }
    pub async fn is_terminated(&self) -> bool {
        self.get_aborted().await || self.get_closed().await
    }
    pub async fn is_keep_alive(&self, keep_alive: bool) -> bool {
        !self.get_closed().await && keep_alive
    }
    pub async fn try_get_stream(&self) -> Option<ArcRwLockStream> {
        self.read().await.get_stream().clone()
    }
    pub async fn get_stream(&self) -> ArcRwLockStream {
        self.try_get_stream().await.unwrap()
    }
    pub async fn try_get_socket_addr(&self) -> Option<SocketAddr> {
        self.try_get_stream()
            .await
            .as_ref()?
            .read()
            .await
            .peer_addr()
            .ok()
    }
    pub async fn get_socket_addr(&self) -> SocketAddr {
        self.try_get_socket_addr().await.unwrap()
    }
    pub async fn try_get_socket_addr_string(&self) -> Option<String> {
        self.try_get_socket_addr()
            .await
            .map(|data| data.to_string())
    }
    pub async fn get_socket_addr_string(&self) -> String {
        self.get_socket_addr().await.to_string()
    }
    pub async fn try_get_socket_host(&self) -> Option<SocketHost> {
        self.try_get_socket_addr()
            .await
            .map(|socket_addr: SocketAddr| socket_addr.ip())
    }
    pub async fn get_socket_host(&self) -> SocketHost {
        self.try_get_socket_host().await.unwrap()
    }
    pub async fn try_get_socket_port(&self) -> Option<SocketPort> {
        self.try_get_socket_addr()
            .await
            .map(|socket_addr: SocketAddr| socket_addr.port())
    }
    pub async fn get_socket_port(&self) -> SocketPort {
        self.try_get_socket_port().await.unwrap()
    }
    pub async fn get_request(&self) -> Request {
        self.read().await.get_request().clone()
    }
    pub(crate) async fn set_request(&self, request_data: &Request) -> &Self {
        self.write().await.set_request(request_data.clone());
        self
    }
    pub async fn with_request<F, Fut, R>(&self, func: F) -> R
    where
        F: Fn(Request) -> Fut,
        Fut: FutureSendStatic<R>,
    {
        func(self.read().await.get_request().clone()).await
    }
    pub async fn get_request_string(&self) -> String {
        self.read().await.get_request().get_string()
    }
    pub async fn get_request_version(&self) -> RequestVersion {
        self.read().await.get_request().get_version().clone()
    }
    pub async fn get_request_method(&self) -> RequestMethod {
        self.read().await.get_request().get_method().clone()
    }
    pub async fn get_request_host(&self) -> RequestHost {
        self.read().await.get_request().get_host().clone()
    }
    pub async fn get_request_path(&self) -> RequestPath {
        self.read().await.get_request().get_path().clone()
    }
    pub async fn get_request_querys(&self) -> RequestQuerys {
        self.read().await.get_request().get_querys().clone()
    }
    pub async fn try_get_request_query<K>(&self, key: K) -> Option<RequestQuerysValue>
    where
        K: AsRef<str>,
    {
        self.read().await.get_request().try_get_query(key)
    }
    pub async fn get_request_query<K>(&self, key: K) -> RequestQuerysValue
    where
        K: AsRef<str>,
    {
        self.read().await.get_request().get_query(key)
    }
    pub async fn get_request_body(&self) -> RequestBody {
        self.read().await.get_request().get_body().clone()
    }
    pub async fn get_request_body_string(&self) -> String {
        self.read().await.get_request().get_body_string()
    }
    pub async fn try_get_request_body_json<J>(&self) -> Result<J, serde_json::Error>
    where
        J: DeserializeOwned,
    {
        self.read().await.get_request().try_get_body_json()
    }
    pub async fn get_request_body_json<J>(&self) -> J
    where
        J: DeserializeOwned,
    {
        self.read().await.get_request().get_body_json()
    }
    pub async fn get_request_headers(&self) -> RequestHeaders {
        self.read().await.get_request().get_headers().clone()
    }
    pub async fn get_request_headers_length(&self) -> usize {
        self.read().await.get_request().get_headers_length()
    }
    pub async fn try_get_request_header<K>(&self, key: K) -> Option<RequestHeadersValue>
    where
        K: AsRef<str>,
    {
        self.read().await.get_request().try_get_header(key)
    }
    pub async fn get_request_header<K>(&self, key: K) -> RequestHeadersValue
    where
        K: AsRef<str>,
    {
        self.read().await.get_request().get_header(key)
    }
    pub async fn try_get_request_header_front<K>(&self, key: K) -> Option<RequestHeadersValueItem>
    where
        K: AsRef<str>,
    {
        self.read().await.get_request().try_get_header_front(key)
    }
    pub async fn get_request_header_front<K>(&self, key: K) -> RequestHeadersValueItem
    where
        K: AsRef<str>,
    {
        self.read().await.get_request().get_header_front(key)
    }
    pub async fn try_get_request_header_back<K>(&self, key: K) -> Option<RequestHeadersValueItem>
    where
        K: AsRef<str>,
    {
        self.read().await.get_request().try_get_header_back(key)
    }
    pub async fn get_request_header_back<K>(&self, key: K) -> RequestHeadersValueItem
    where
        K: AsRef<str>,
    {
        self.read().await.get_request().get_header_back(key)
    }
    pub async fn try_get_request_header_len<K>(&self, key: K) -> Option<usize>
    where
        K: AsRef<str>,
    {
        self.read().await.get_request().try_get_header_length(key)
    }
    pub async fn get_request_header_len<K>(&self, key: K) -> usize
    where
        K: AsRef<str>,
    {
        self.read().await.get_request().get_header_length(key)
    }
    pub async fn get_request_headers_values_length(&self) -> usize {
        self.read().await.get_request().get_headers_values_length()
    }
    pub async fn get_request_has_header<K>(&self, key: K) -> bool
    where
        K: AsRef<str>,
    {
        self.read().await.get_request().has_header(key)
    }
    pub async fn get_request_has_header_value<K, V>(&self, key: K, value: V) -> bool
    where
        K: AsRef<str>,
        V: AsRef<str>,
    {
        self.read().await.get_request().has_header_value(key, value)
    }
    pub async fn get_request_cookies(&self) -> Cookies {
        self.try_get_request_header_back(COOKIE)
            .await
            .map(|data| Cookie::parse(&data))
            .unwrap_or_default()
    }
    pub async fn try_get_request_cookie<K>(&self, key: K) -> Option<CookieValue>
    where
        K: AsRef<str>,
    {
        self.get_request_cookies().await.get(key.as_ref()).cloned()
    }
    pub async fn get_request_cookie<K>(&self, key: K) -> CookieValue
    where
        K: AsRef<str>,
    {
        self.try_get_request_cookie(key).await.unwrap()
    }
    pub async fn get_request_upgrade_type(&self) -> UpgradeType {
        self.read().await.get_request().get_upgrade_type()
    }
    pub async fn get_request_is_ws(&self) -> bool {
        self.read().await.get_request().is_ws()
    }
    pub async fn get_request_is_h2c(&self) -> bool {
        self.read().await.get_request().is_h2c()
    }
    pub async fn get_request_is_tls(&self) -> bool {
        self.read().await.get_request().is_tls()
    }
    pub async fn get_request_is_unknown_upgrade(&self) -> bool {
        self.read().await.get_request().is_unknown_upgrade()
    }
    pub async fn get_request_is_http1_1_or_higher(&self) -> bool {
        self.read().await.get_request().is_http1_1_or_higher()
    }
    pub async fn get_request_is_http0_9(&self) -> bool {
        self.read().await.get_request().is_http0_9()
    }
    pub async fn get_request_is_http1_0(&self) -> bool {
        self.read().await.get_request().is_http1_0()
    }
    pub async fn get_request_is_http1_1(&self) -> bool {
        self.read().await.get_request().is_http1_1()
    }
    pub async fn get_request_is_http2(&self) -> bool {
        self.read().await.get_request().is_http2()
    }
    pub async fn get_request_is_http3(&self) -> bool {
        self.read().await.get_request().is_http3()
    }
    pub async fn get_request_is_unknown_version(&self) -> bool {
        self.read().await.get_request().is_unknown_version()
    }
    pub async fn get_request_is_http(&self) -> bool {
        self.read().await.get_request().is_http()
    }
    pub async fn get_request_is_get(&self) -> bool {
        self.read().await.get_request().is_get()
    }
    pub async fn get_request_is_post(&self) -> bool {
        self.read().await.get_request().is_post()
    }
    pub async fn get_request_is_put(&self) -> bool {
        self.read().await.get_request().is_put()
    }
    pub async fn get_request_is_delete(&self) -> bool {
        self.read().await.get_request().is_delete()
    }
    pub async fn get_request_is_patch(&self) -> bool {
        self.read().await.get_request().is_patch()
    }
    pub async fn get_request_is_head(&self) -> bool {
        self.read().await.get_request().is_head()
    }
    pub async fn get_request_is_options(&self) -> bool {
        self.read().await.get_request().is_options()
    }
    pub async fn get_request_is_connect(&self) -> bool {
        self.read().await.get_request().is_connect()
    }
    pub async fn get_request_is_trace(&self) -> bool {
        self.read().await.get_request().is_trace()
    }
    pub async fn get_request_is_unknown_method(&self) -> bool {
        self.read().await.get_request().is_unknown_method()
    }
    pub async fn get_request_is_enable_keep_alive(&self) -> bool {
        self.read().await.get_request().is_enable_keep_alive()
    }
    pub async fn get_request_is_disable_keep_alive(&self) -> bool {
        self.read().await.get_request().is_disable_keep_alive()
    }
    pub async fn get_response(&self) -> Response {
        self.read().await.get_response().clone()
    }
    pub async fn set_response<T>(&self, response: T) -> &Self
    where
        T: Borrow<Response>,
    {
        self.write().await.set_response(response.borrow().clone());
        self
    }
    pub async fn with_response<F, Fut, R>(&self, func: F) -> R
    where
        F: Fn(Response) -> Fut,
        Fut: FutureSendStatic<R>,
    {
        func(self.read().await.get_response().clone()).await
    }
    pub async fn get_response_string(&self) -> String {
        self.read().await.get_response().get_string()
    }
    pub async fn get_response_version(&self) -> ResponseVersion {
        self.read().await.get_response().get_version().clone()
    }
    pub async fn set_response_version(&self, version: ResponseVersion) -> &Self {
        self.write().await.get_mut_response().set_version(version);
        self
    }
    pub async fn get_response_headers(&self) -> ResponseHeaders {
        self.read().await.get_response().get_headers().clone()
    }
    pub async fn try_get_response_header<K>(&self, key: K) -> Option<ResponseHeadersValue>
    where
        K: AsRef<str>,
    {
        self.read().await.get_response().try_get_header(key)
    }
    pub async fn get_response_header<K>(&self, key: K) -> ResponseHeadersValue
    where
        K: AsRef<str>,
    {
        self.read().await.get_response().get_header(key)
    }
    pub async fn set_response_header<K, V>(&self, key: K, value: V) -> &Self
    where
        K: AsRef<str>,
        V: AsRef<str>,
    {
        self.write().await.get_mut_response().set_header(key, value);
        self
    }
    pub async fn try_get_response_header_front<K>(&self, key: K) -> Option<ResponseHeadersValueItem>
    where
        K: AsRef<str>,
    {
        self.read().await.get_response().try_get_header_front(key)
    }
    pub async fn get_response_header_front<K>(&self, key: K) -> ResponseHeadersValueItem
    where
        K: AsRef<str>,
    {
        self.read().await.get_response().get_header_front(key)
    }
    pub async fn try_get_response_header_back<K>(&self, key: K) -> Option<ResponseHeadersValueItem>
    where
        K: AsRef<str>,
    {
        self.read().await.get_response().try_get_header_back(key)
    }
    pub async fn get_response_header_back<K>(&self, key: K) -> ResponseHeadersValueItem
    where
        K: AsRef<str>,
    {
        self.read().await.get_response().get_header_back(key)
    }
    pub async fn get_response_has_header<K>(&self, key: K) -> bool
    where
        K: AsRef<str>,
    {
        self.read().await.get_response().has_header(key)
    }
    pub async fn get_response_header_value<K, V>(&self, key: K, value: V) -> bool
    where
        K: AsRef<str>,
        V: AsRef<str>,
    {
        self.read()
            .await
            .get_response()
            .has_header_value(key, value)
    }
    pub async fn get_response_headers_length(&self) -> usize {
        self.read().await.get_response().get_headers_length()
    }
    pub async fn try_get_response_header_length<K>(&self, key: K) -> Option<usize>
    where
        K: AsRef<str>,
    {
        self.read().await.get_response().try_get_header_length(key)
    }
    pub async fn get_response_header_length<K>(&self, key: K) -> usize
    where
        K: AsRef<str>,
    {
        self.read().await.get_response().get_header_length(key)
    }
    pub async fn get_response_headers_values_length(&self) -> usize {
        self.read().await.get_response().get_headers_values_length()
    }
    pub async fn add_response_header<K, V>(&self, key: K, value: V) -> &Self
    where
        K: AsRef<str>,
        V: AsRef<str>,
    {
        self.write().await.get_mut_response().add_header(key, value);
        self
    }
    pub async fn remove_response_header<K>(&self, key: K) -> &Self
    where
        K: AsRef<str>,
    {
        self.write().await.get_mut_response().remove_header(key);
        self
    }
    pub async fn remove_response_header_value<K, V>(&self, key: K, value: V) -> &Self
    where
        K: AsRef<str>,
        V: AsRef<str>,
    {
        self.write()
            .await
            .get_mut_response()
            .remove_header_value(key, value);
        self
    }
    pub async fn clear_response_headers(&self) -> &Self {
        self.write().await.get_mut_response().clear_headers();
        self
    }
    pub async fn get_response_cookies(&self) -> Cookies {
        self.try_get_response_header_back(COOKIE)
            .await
            .map(|data| Cookie::parse(&data))
            .unwrap_or_default()
    }
    pub async fn try_get_response_cookie<K>(&self, key: K) -> Option<CookieValue>
    where
        K: AsRef<str>,
    {
        self.get_response_cookies().await.get(key.as_ref()).cloned()
    }
    pub async fn get_response_cookie<K>(&self, key: K) -> CookieValue
    where
        K: AsRef<str>,
    {
        self.try_get_response_cookie(key).await.unwrap()
    }
    pub async fn get_response_body(&self) -> ResponseBody {
        self.read().await.get_response().get_body().clone()
    }
    pub async fn set_response_body<B>(&self, body: B) -> &Self
    where
        B: AsRef<[u8]>,
    {
        self.write().await.get_mut_response().set_body(body);
        self
    }
    pub async fn get_response_body_string(&self) -> String {
        self.read().await.get_response().get_body_string()
    }
    pub async fn try_get_response_body_json<J>(&self) -> Result<J, serde_json::Error>
    where
        J: DeserializeOwned,
    {
        self.read().await.get_response().try_get_body_json()
    }
    pub async fn get_response_body_json<J>(&self) -> J
    where
        J: DeserializeOwned,
    {
        self.read().await.get_response().get_body_json()
    }
    pub async fn get_response_reason_phrase(&self) -> ResponseReasonPhrase {
        self.read().await.get_response().get_reason_phrase().clone()
    }
    pub async fn set_response_reason_phrase<P>(&self, reason_phrase: P) -> &Self
    where
        P: AsRef<str>,
    {
        self.write()
            .await
            .get_mut_response()
            .set_reason_phrase(reason_phrase);
        self
    }
    pub async fn get_response_status_code(&self) -> ResponseStatusCode {
        *self.read().await.get_response().get_status_code()
    }
    pub async fn set_response_status_code(&self, status_code: ResponseStatusCode) -> &Self {
        self.write()
            .await
            .get_mut_response()
            .set_status_code(status_code);
        self
    }
    pub async fn get_route_params(&self) -> RouteParams {
        self.read().await.get_route_params().clone()
    }
    pub(crate) async fn set_route_params(&self, params: RouteParams) -> &Self {
        self.write().await.set_route_params(params);
        self
    }
    pub async fn try_get_route_param<T>(&self, name: T) -> Option<String>
    where
        T: AsRef<str>,
    {
        self.read()
            .await
            .get_route_params()
            .get(name.as_ref())
            .cloned()
    }
    pub async fn get_route_param<T>(&self, name: T) -> String
    where
        T: AsRef<str>,
    {
        self.try_get_route_param(name).await.unwrap()
    }
    pub async fn get_attributes(&self) -> ThreadSafeAttributeStore {
        self.read().await.get_attributes().clone()
    }
    pub async fn try_get_attribute<K, V>(&self, key: K) -> Option<V>
    where
        K: AsRef<str>,
        V: AnySendSyncClone,
    {
        self.read()
            .await
            .get_attributes()
            .get(&Attribute::External(key.as_ref().to_owned()).to_string())
            .and_then(|arc| arc.downcast_ref::<V>())
            .cloned()
    }
    pub async fn get_attribute<K, V>(&self, key: K) -> V
    where
        K: AsRef<str>,
        V: AnySendSyncClone,
    {
        self.try_get_attribute(key).await.unwrap()
    }
    pub async fn set_attribute<K, V>(&self, key: K, value: V) -> &Self
    where
        K: AsRef<str>,
        V: AnySendSyncClone,
    {
        self.write().await.get_mut_attributes().insert(
            Attribute::External(key.as_ref().to_owned()).to_string(),
            Arc::new(value),
        );
        self
    }
    pub async fn remove_attribute<K>(&self, key: K) -> &Self
    where
        K: AsRef<str>,
    {
        self.write()
            .await
            .get_mut_attributes()
            .remove(&Attribute::External(key.as_ref().to_owned()).to_string());
        self
    }
    pub async fn clear_attribute(&self) -> &Self {
        self.write().await.get_mut_attributes().clear();
        self
    }
    async fn try_get_internal_attribute<V>(&self, key: InternalAttribute) -> Option<V>
    where
        V: AnySendSyncClone,
    {
        self.read()
            .await
            .get_attributes()
            .get(&Attribute::Internal(key).to_string())
            .and_then(|arc| arc.downcast_ref::<V>())
            .cloned()
    }
    async fn get_internal_attribute<V>(&self, key: InternalAttribute) -> V
    where
        V: AnySendSyncClone,
    {
        self.try_get_internal_attribute(key).await.unwrap()
    }
    async fn set_internal_attribute<V>(&self, key: InternalAttribute, value: V) -> &Self
    where
        V: AnySendSyncClone,
    {
        self.write()
            .await
            .get_mut_attributes()
            .insert(Attribute::Internal(key).to_string(), Arc::new(value));
        self
    }
    pub(crate) async fn set_task_panic(&self, panic_data: PanicData) -> &Self {
        self.set_internal_attribute(InternalAttribute::TaskPanicData, panic_data)
            .await
    }
    pub async fn try_get_task_panic_data(&self) -> Option<PanicData> {
        self.try_get_internal_attribute(InternalAttribute::TaskPanicData)
            .await
    }
    pub async fn get_task_panic_data(&self) -> PanicData {
        self.get_internal_attribute(InternalAttribute::TaskPanicData)
            .await
    }
    pub(crate) async fn set_request_error_data(&self, request_error: RequestError) -> &Self {
        self.set_internal_attribute(InternalAttribute::RequestErrorData, request_error)
            .await
    }
    pub async fn try_get_request_error_data(&self) -> Option<RequestError> {
        self.try_get_internal_attribute(InternalAttribute::RequestErrorData)
            .await
    }
    pub async fn get_request_error_data(&self) -> RequestError {
        self.get_internal_attribute(InternalAttribute::RequestErrorData)
            .await
    }
    pub async fn set_hook<K, F, Fut>(&self, key: K, hook: F) -> &Self
    where
        K: ToString,
        F: FnContextSendSyncStatic<Fut, ()>,
        Fut: FutureSendStatic<()>,
    {
        let hook_fn: HookHandler<()> =
            Arc::new(move |ctx: Context| -> SendableAsyncTask<()> { Box::pin(hook(ctx)) });
        self.set_internal_attribute(InternalAttribute::Hook(key.to_string()), hook_fn)
            .await
    }
    pub async fn try_get_hook<K>(&self, key: K) -> Option<HookHandler<()>>
    where
        K: ToString,
    {
        self.try_get_internal_attribute(InternalAttribute::Hook(key.to_string()))
            .await
    }
    pub async fn get_hook<K>(&self, key: K) -> HookHandler<()>
    where
        K: ToString,
    {
        self.get_internal_attribute(InternalAttribute::Hook(key.to_string()))
            .await
    }
    pub async fn try_send(&self) -> Result<(), ResponseError> {
        if self.is_terminated().await {
            return Err(ResponseError::Terminated);
        }
        let response_data: ResponseData = self.write().await.get_mut_response().build();
        if let Some(stream) = self.try_get_stream().await {
            return stream.try_send(response_data).await;
        }
        Err(ResponseError::NotFoundStream)
    }
    pub async fn send(&self) {
        self.try_send().await.unwrap();
    }
    pub async fn try_send_body(&self) -> Result<(), ResponseError> {
        if self.is_terminated().await {
            return Err(ResponseError::Terminated);
        }
        let response_body: ResponseBody = self.get_response_body().await;
        self.try_send_body_with_data(response_body).await
    }
    pub async fn send_body(&self) {
        self.try_send_body().await.unwrap();
    }
    pub async fn try_send_body_with_data<D>(&self, data: D) -> Result<(), ResponseError>
    where
        D: AsRef<[u8]>,
    {
        if self.is_terminated().await {
            return Err(ResponseError::Terminated);
        }
        if let Some(stream) = self.try_get_stream().await {
            return stream.try_send_body(data).await;
        }
        Err(ResponseError::NotFoundStream)
    }
    pub async fn send_body_with_data<D>(&self, data: D)
    where
        D: AsRef<[u8]>,
    {
        self.try_send_body_with_data(data).await.unwrap();
    }
    pub async fn try_send_body_list<I, D>(&self, data_iter: I) -> Result<(), ResponseError>
    where
        I: IntoIterator<Item = D>,
        D: AsRef<[u8]>,
    {
        if self.is_terminated().await {
            return Err(ResponseError::Terminated);
        }
        if let Some(stream) = self.try_get_stream().await {
            return stream.try_send_body_list(data_iter).await;
        }
        Err(ResponseError::NotFoundStream)
    }
    pub async fn send_body_list<I, D>(&self, data_iter: I)
    where
        I: IntoIterator<Item = D>,
        D: AsRef<[u8]>,
    {
        self.try_send_body_list(data_iter).await.unwrap();
    }
    pub async fn try_send_body_list_with_data<I, D>(
        &self,
        data_iter: I,
    ) -> Result<(), ResponseError>
    where
        I: IntoIterator<Item = D>,
        D: AsRef<[u8]>,
    {
        if self.is_terminated().await {
            return Err(ResponseError::Terminated);
        }
        if let Some(stream) = self.try_get_stream().await {
            return stream.try_send_body_list(data_iter).await;
        }
        Err(ResponseError::NotFoundStream)
    }
    pub async fn send_body_list_with_data<I, D>(&self, data_iter: I)
    where
        I: IntoIterator<Item = D>,
        D: AsRef<[u8]>,
    {
        self.try_send_body_list_with_data(data_iter).await.unwrap()
    }
    pub async fn try_flush(&self) -> Result<(), ResponseError> {
        if self.is_terminated().await {
            return Err(ResponseError::Terminated);
        }
        if let Some(stream) = self.try_get_stream().await {
            return stream.try_flush().await;
        }
        Err(ResponseError::NotFoundStream)
    }
    pub async fn flush(&self) {
        self.try_flush().await.unwrap();
    }
}
```
# Path: hyperlane/src/context/type.rs
```rust
use crate::*;
pub(crate) type ContextWriteGuard<'a> = RwLockWriteGuard<'a, ContextInner>;
pub(crate) type ContextReadGuard<'a> = RwLockReadGuard<'a, ContextInner>;
```
# Path: hyperlane/src/attribute/mod.rs
```rust
pub(crate) mod r#enum;
pub(crate) mod r#impl;
pub(crate) mod r#type;
pub use r#type::*;
pub(crate) use r#enum::*;
```
# Path: hyperlane/src/attribute/enum.rs
```rust
use crate::*;
#[derive(CustomDebug, Clone, PartialEq, Eq, Hash, DisplayDebug)]
pub(crate) enum Attribute {
    External(String),
    Internal(InternalAttribute),
}
#[derive(CustomDebug, Clone, PartialEq, Eq, Hash, DisplayDebug)]
pub(crate) enum InternalAttribute {
    TaskPanicData,
    RequestErrorData,
    Hook(String),
}
```
# Path: hyperlane/src/attribute/impl.rs
```rust
use crate::*;
impl From<&str> for Attribute {
    #[inline(always)]
    fn from(key: &str) -> Self {
        Attribute::External(key.to_string())
    }
}
impl From<String> for Attribute {
    #[inline(always)]
    fn from(key: String) -> Self {
        Attribute::External(key)
    }
}
impl From<InternalAttribute> for Attribute {
    #[inline(always)]
    fn from(key: InternalAttribute) -> Self {
        Attribute::Internal(key)
    }
}
```
# Path: hyperlane/src/attribute/type.rs
```rust
use crate::*;
pub type ThreadSafeAttributeStore = HashMap<String, ArcAnySendSync>;
```
# Path: hyperlane/src/tests/server.rs
```rust
use crate::*;
#[tokio::test]
async fn server_partial_eq() {
    let server1: Server = Server::new().await;
    let server2: Server = Server::new().await;
    assert_eq!(server1, server2);
    let server1_clone: Server = server1.clone();
    assert_eq!(server1, server1_clone);
}
#[tokio::test]
async fn server_inner_partial_eq() {
    let inner1: ServerInner = ServerInner::default();
    let inner2: ServerInner = ServerInner::default();
    assert_eq!(inner1, inner2);
}
struct TaskPanicHook {
    response_body: String,
    content_type: String,
}
impl ServerHook for TaskPanicHook {
    async fn new(ctx: &Context) -> Self {
        let error: PanicData = ctx.try_get_task_panic_data().await.unwrap_or_default();
        let response_body: String = error.to_string();
        let content_type: String = ContentType::format_content_type_with_charset(TEXT_PLAIN, UTF8);
        Self {
            response_body,
            content_type,
        }
    }
    async fn handle(self, ctx: &Context) {
        ctx.set_response_version(HttpVersion::Http1_1)
            .await
            .set_response_status_code(500)
            .await
            .clear_response_headers()
            .await
            .set_response_header(SERVER, HYPERLANE)
            .await
            .set_response_header(CONTENT_TYPE, &self.content_type)
            .await
            .set_response_body(&self.response_body)
            .await
            .send()
            .await;
    }
}
struct RequestErrorHook {
    response_status_code: ResponseStatusCode,
    response_body: String,
}
impl ServerHook for RequestErrorHook {
    async fn new(ctx: &Context) -> Self {
        let request_error: RequestError =
            ctx.try_get_request_error_data().await.unwrap_or_default();
        Self {
            response_status_code: request_error.get_http_status_code(),
            response_body: request_error.to_string(),
        }
    }
    async fn handle(self, ctx: &Context) {
        ctx.set_response_version(HttpVersion::Http1_1)
            .await
            .set_response_status_code(self.response_status_code)
            .await
            .set_response_body(self.response_body)
            .await
            .send()
            .await;
    }
}
struct SendBodyMiddleware {
    socket_addr: String,
}
impl ServerHook for SendBodyMiddleware {
    async fn new(ctx: &Context) -> Self {
        let socket_addr: String = ctx.get_socket_addr_string().await;
        Self { socket_addr }
    }
    async fn handle(self, ctx: &Context) {
        ctx.set_response_version(HttpVersion::Http1_1)
            .await
            .set_response_status_code(200)
            .await
            .set_response_header(SERVER, HYPERLANE)
            .await
            .set_response_header(CONNECTION, KEEP_ALIVE)
            .await
            .set_response_header(CONTENT_TYPE, TEXT_PLAIN)
            .await
            .set_response_header(ACCESS_CONTROL_ALLOW_ORIGIN, WILDCARD_ANY)
            .await
            .set_response_header("SocketAddr", &self.socket_addr)
            .await;
    }
}
struct UpgradeMiddleware;
impl ServerHook for UpgradeMiddleware {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &Context) {
        if !ctx.get_request().await.is_ws() {
            return;
        }
        if let Some(key) = &ctx.try_get_request_header_back(SEC_WEBSOCKET_KEY).await {
            let accept_key: String = WebSocketFrame::generate_accept_key(key);
            ctx.set_response_version(HttpVersion::Http1_1)
                .await
                .set_response_status_code(101)
                .await
                .set_response_header(UPGRADE, WEBSOCKET)
                .await
                .set_response_header(CONNECTION, UPGRADE)
                .await
                .set_response_header(SEC_WEBSOCKET_ACCEPT, &accept_key)
                .await
                .set_response_body(&vec![])
                .await
                .send()
                .await;
        }
    }
}
struct ResponseMiddleware;
impl ServerHook for ResponseMiddleware {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &Context) {
        if ctx.get_request().await.is_ws() {
            return;
        }
        ctx.send().await;
    }
}
struct RootRoute {
    response_body: String,
    cookie1: String,
    cookie2: String,
}
impl ServerHook for RootRoute {
    async fn new(ctx: &Context) -> Self {
        let path: RequestPath = ctx.get_request_path().await;
        let response_body: String = format!("Hello hyperlane => {}", path);
        let cookie1: String = CookieBuilder::new("key1", "value1").http_only().build();
        let cookie2: String = CookieBuilder::new("key2", "value2").http_only().build();
        Self {
            response_body,
            cookie1,
            cookie2,
        }
    }
    async fn handle(self, ctx: &Context) {
        ctx.add_response_header(SET_COOKIE, &self.cookie1)
            .await
            .add_response_header(SET_COOKIE, &self.cookie2)
            .await
            .set_response_body(&self.response_body)
            .await;
    }
}
struct SseRoute;
impl ServerHook for SseRoute {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &Context) {
        ctx.set_response_header(CONTENT_TYPE, TEXT_EVENT_STREAM)
            .await
            .send()
            .await;
        for i in 0..10 {
            ctx.set_response_body(&format!("data:{}{}", i, HTTP_DOUBLE_BR))
                .await
                .send_body()
                .await;
        }
        ctx.closed().await;
    }
}
struct WebsocketRoute;
impl WebsocketRoute {
    async fn send_body_hook(&self, ctx: &Context) {
        if ctx.get_request().await.is_ws() {
            let body: ResponseBody = ctx.get_response_body().await;
            let frame_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(&body);
            ctx.send_body_list_with_data(&frame_list).await;
        } else {
            ctx.send_body().await;
        }
    }
}
impl ServerHook for WebsocketRoute {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &Context) {
        loop {
            match ctx.ws_from_stream(RequestConfig::default()).await {
                Ok(_) => {
                    let request_body: Vec<u8> = ctx.get_request_body().await;
                    ctx.set_response_body(&request_body).await;
                    self.send_body_hook(ctx).await;
                    continue;
                }
                Err(error) => {
                    ctx.set_response_body(&error.to_string()).await;
                    self.send_body_hook(ctx).await;
                    return;
                }
            }
        }
    }
}
struct DynamicRoute {
    params: RouteParams,
}
impl ServerHook for DynamicRoute {
    async fn new(ctx: &Context) -> Self {
        Self {
            params: ctx.get_route_params().await,
        }
    }
    async fn handle(mut self, _ctx: &Context) {
        self.params.insert("key".to_owned(), "value".to_owned());
        panic!("Test panic {:?}", self.params);
    }
}
#[tokio::test]
async fn main() {
    let server: Server = Server::new().await;
    server.task_panic::<TaskPanicHook>().await;
    server.request_error::<RequestErrorHook>().await;
    server.request_middleware::<SendBodyMiddleware>().await;
    server.request_middleware::<UpgradeMiddleware>().await;
    server.response_middleware::<ResponseMiddleware>().await;
    server.route::<RootRoute>("/").await;
    server.route::<SseRoute>("/sse").await;
    server.route::<WebsocketRoute>("/websocket").await;
    server.route::<DynamicRoute>("/dynamic/{routing}").await;
    server.route::<DynamicRoute>("/regex/{file:^.*$}").await;
    let server_control_hook_1: ServerControlHook = server.run().await.unwrap_or_default();
    let server_control_hook_2: ServerControlHook = server_control_hook_1.clone();
    tokio::spawn(async move {
        tokio::time::sleep(std::time::Duration::from_secs(60)).await;
        server_control_hook_2.shutdown().await;
    });
    server_control_hook_1.wait().await;
}
```
# Path: hyperlane/src/tests/route.rs
```rust
use crate::*;
#[cfg(test)]
async fn assert_panic_message_contains<F, Fut>(future_factory: F, expected_msg: &str)
where
    F: Fn() -> Fut + Send + 'static,
    Fut: Future<Output = ()> + Send + 'static,
{
    let result: Result<(), JoinError> = spawn(future_factory()).await;
    assert!(
        result.is_err(),
        "Expected panic, but task completed successfully"
    );
    let join_err: JoinError = result.unwrap_err();
    if !join_err.is_panic() {
        panic!("Task failed but was not a panic");
    }
    let panic_payload: Box<dyn Any + Send> = join_err.into_panic();
    let panic_msg: &str = if let Some(s) = panic_payload.downcast_ref::<&str>() {
        s
    } else if let Some(s) = panic_payload.downcast_ref::<String>() {
        s.as_str()
    } else {
        "Unknown panic type"
    };
    assert!(
        panic_msg.contains(expected_msg),
        "Expected panic message to contain: '{}', but got: '{}'",
        expected_msg,
        panic_msg
    );
}
#[cfg(test)]
struct TestRoute {
    data: String,
}
#[cfg(test)]
impl ServerHook for TestRoute {
    async fn new(_ctx: &Context) -> Self {
        Self {
            data: String::new(),
        }
    }
    async fn handle(mut self, _ctx: &Context) {
        self.data = String::from("test");
    }
}
#[tokio::test]
async fn empty_route() {
    assert_panic_message_contains(
        || async {
            let _server: &Server = Server::new().await.route::<TestRoute>(EMPTY_STR).await;
        },
        &RouteError::EmptyPattern.to_string(),
    )
    .await;
}
#[tokio::test]
async fn duplicate_route() {
    assert_panic_message_contains(
        || async {
            let _server: &Server = Server::new()
                .await
                .route::<TestRoute>(ROOT_PATH)
                .await
                .route::<TestRoute>(ROOT_PATH)
                .await;
        },
        &RouteError::DuplicatePattern(ROOT_PATH.to_string()).to_string(),
    )
    .await;
}
#[tokio::test]
async fn get_route() {
    let server: Server = Server::new().await;
    server
        .route::<TestRoute>(ROOT_PATH)
        .await
        .route::<TestRoute>("/dynamic/{routing}")
        .await
        .route::<TestRoute>("/regex/{file:^.*$}")
        .await;
    let route_matcher: RouteMatcher = server.get_route_matcher().await;
    for key in route_matcher.get_static_route().keys() {
        println!("Static route: {key}");
    }
    for value in route_matcher.get_dynamic_route().values() {
        for (route_pattern, _) in value {
            println!("Dynamic route: {route_pattern}");
        }
    }
    for value in route_matcher.get_regex_route().values() {
        for (route_pattern, _) in value {
            println!("Regex route: {route_pattern}");
        }
    }
}
#[tokio::test]
async fn segment_count_optimization() {
    let server: Server = Server::new().await;
    server.route::<TestRoute>("/users/{id}").await;
    server.route::<TestRoute>("/users/{id}/posts").await;
    server
        .route::<TestRoute>("/users/{id}/posts/{post_id}")
        .await;
    server.route::<TestRoute>("/api/v1/users/{id}").await;
    let route_matcher: RouteMatcher = server.get_route_matcher().await;
    assert!(
        route_matcher.get_dynamic_route().contains_key(&2),
        "Should have 2-segment routes"
    );
    assert!(
        route_matcher.get_dynamic_route().contains_key(&3),
        "Should have 3-segment routes"
    );
    assert!(
        route_matcher.get_dynamic_route().contains_key(&4),
        "Should have 4-segment routes"
    );
    assert_eq!(route_matcher.get_dynamic_route().get(&2).unwrap().len(), 1);
    assert_eq!(route_matcher.get_dynamic_route().get(&3).unwrap().len(), 1);
    assert_eq!(route_matcher.get_dynamic_route().get(&4).unwrap().len(), 2);
}
#[tokio::test]
async fn regex_route_segment_count() {
    let server: Server = Server::new().await;
    server.route::<TestRoute>("/files/{path:.*}").await;
    server.route::<TestRoute>("/api/{version:\\d+}/users").await;
    server
        .route::<TestRoute>("/api/{version:\\d+}/posts/{id:\\d+}")
        .await;
    let route_matcher: RouteMatcher = server.get_route_matcher().await;
    assert!(
        route_matcher.get_regex_route().contains_key(&2),
        "Should have 2-segment regex routes"
    );
    assert!(
        route_matcher.get_regex_route().contains_key(&3),
        "Should have 3-segment regex routes"
    );
    assert!(
        route_matcher.get_regex_route().contains_key(&4),
        "Should have 4-segment regex routes"
    );
}
#[tokio::test]
async fn mixed_route_types() {
    let server: Server = Server::new().await;
    server.route::<TestRoute>("/").await;
    server.route::<TestRoute>("/about").await;
    server.route::<TestRoute>("/users/{id}").await;
    server.route::<TestRoute>("/posts/{slug}").await;
    server.route::<TestRoute>("/files/{path:.*}").await;
    let route_matcher: RouteMatcher = server.get_route_matcher().await;
    assert_eq!(route_matcher.get_static_route().len(), 2);
    assert!(route_matcher.get_dynamic_route().contains_key(&2));
    assert!(route_matcher.get_regex_route().contains_key(&2));
}
#[tokio::test]
async fn large_dynamic_routes() {
    const ROUTE_COUNT: u32 = 1000;
    let server: Server = Server::new().await;
    let start_insert: Instant = Instant::now();
    for i in 0..ROUTE_COUNT {
        let path: String = format!("/api/resource{i}/{{id}}");
        server.route::<TestRoute>(&path).await;
    }
    let insert_duration: Duration = start_insert.elapsed();
    println!(
        "Inserted {} dynamic routes in: {:?}",
        ROUTE_COUNT, insert_duration
    );
    let route_matcher: RouteMatcher = server.get_route_matcher().await;
    assert!(!route_matcher.get_dynamic_route().is_empty());
    let ctx: Context = Context::default();
    let start_match: Instant = Instant::now();
    for i in 0..ROUTE_COUNT {
        let path: String = format!("/api/resource{i}/123");
        let _ = route_matcher.try_resolve_route(&ctx, &path).await;
    }
    let match_duration: Duration = start_match.elapsed();
    println!(
        "Matched {} dynamic routes in: {:?}",
        ROUTE_COUNT, match_duration
    );
    println!(
        "Average per dynamic route match: {:?}",
        match_duration / ROUTE_COUNT
    );
}
#[tokio::test]
async fn large_regex_routes() {
    const ROUTE_COUNT: u32 = 1000;
    let server: Server = Server::new().await;
    let start_insert: Instant = Instant::now();
    for i in 0..ROUTE_COUNT {
        let path: String = format!("/api/resource{i}/{{id:[0-9]+}}");
        server.route::<TestRoute>(&path).await;
    }
    let insert_duration: Duration = start_insert.elapsed();
    println!(
        "Inserted {} regex routes in: {:?}",
        ROUTE_COUNT, insert_duration
    );
    let route_matcher: RouteMatcher = server.get_route_matcher().await;
    assert!(!route_matcher.get_regex_route().is_empty());
    let ctx: Context = Context::default();
    let start_match: Instant = Instant::now();
    for i in 0..ROUTE_COUNT {
        let path: String = format!("/api/resource{i}/123");
        let _ = route_matcher.try_resolve_route(&ctx, &path).await;
    }
    let match_duration: Duration = start_match.elapsed();
    println!(
        "Matched {} regex routes in: {:?}",
        ROUTE_COUNT, match_duration
    );
    println!(
        "Average per regex route match: {:?}",
        match_duration / ROUTE_COUNT
    );
}
#[tokio::test]
async fn large_tail_regex_routes() {
    const ROUTE_COUNT: u32 = 1000;
    let server: Server = Server::new().await;
    let start_insert: Instant = Instant::now();
    for i in 0..ROUTE_COUNT {
        let path: String = format!("/api/resource{i}/{{path:.*}}");
        server.route::<TestRoute>(&path).await;
    }
    let insert_duration: Duration = start_insert.elapsed();
    println!(
        "Inserted {} tail regex routes in: {:?}",
        ROUTE_COUNT, insert_duration
    );
    let route_matcher: RouteMatcher = server.get_route_matcher().await;
    assert!(!route_matcher.get_regex_route().is_empty());
    let ctx: Context = Context::default();
    let start_match: Instant = Instant::now();
    for i in 0..ROUTE_COUNT {
        let path: String = format!("/api/resource{i}/some/nested/path");
        let _ = route_matcher.try_resolve_route(&ctx, &path).await;
    }
    let match_duration: Duration = start_match.elapsed();
    println!(
        "Matched {} tail regex routes in: {:?}",
        ROUTE_COUNT, match_duration
    );
    println!(
        "Average per tail regex route match: {:?}",
        match_duration / ROUTE_COUNT
    );
}
```
# Path: hyperlane/src/tests/error.rs
```rust
use crate::*;
#[tokio::test]
async fn server_error() {
    let tcp_bind_error: ServerError = ServerError::TcpBind("address in use".to_string());
    let new_tcp_bind_error: ServerError = ServerError::TcpBind("address in use".to_string());
    assert_eq!(tcp_bind_error, new_tcp_bind_error);
    let unknown_error: ServerError = ServerError::Unknown("something went wrong".to_string());
    let new_unknown_error: ServerError = ServerError::Unknown("something went wrong".to_string());
    assert_eq!(unknown_error, new_unknown_error);
    let request: Request = Request::default();
    let invalid_http_request_error: ServerError = ServerError::InvalidHttpRequest(request.clone());
    let new_invalid_http_request_error: ServerError = ServerError::InvalidHttpRequest(request);
    assert_eq!(invalid_http_request_error, new_invalid_http_request_error);
    let other_error: ServerError = ServerError::Other("other error".to_string());
    let new_other_error: ServerError = ServerError::Other("other error".to_string());
    assert_eq!(other_error, new_other_error);
}
#[tokio::test]
async fn route_error() {
    let empty_pattern_error: RouteError = RouteError::EmptyPattern;
    assert_eq!(empty_pattern_error, RouteError::EmptyPattern);
    let duplicate_pattern_error: RouteError = RouteError::DuplicatePattern("/home".to_string());
    let new_duplicate_pattern_error: RouteError = RouteError::DuplicatePattern("/home".to_string());
    assert_eq!(duplicate_pattern_error, new_duplicate_pattern_error);
    let invalid_regex_pattern_error: RouteError = RouteError::InvalidRegexPattern("[".to_string());
    let new_invalid_regex_pattern_error: RouteError =
        RouteError::InvalidRegexPattern("[".to_string());
    assert_eq!(invalid_regex_pattern_error, new_invalid_regex_pattern_error);
}
```
# Path: hyperlane/src/tests/mod.rs
```rust
mod attribute;
mod config;
mod context;
mod error;
mod panic;
mod route;
mod send;
mod server;
```
# Path: hyperlane/src/tests/attribute.rs
```rust
use crate::*;
#[tokio::test]
async fn get_panic_from_context() {
    let ctx: Context = Context::default();
    let set_panic: PanicData = PanicData::new(
        Some("test".to_string()),
        Some("test".to_string()),
        Some("test".to_string()),
    );
    ctx.set_task_panic(set_panic.clone()).await;
    let get_panic: PanicData = ctx.try_get_task_panic_data().await.unwrap();
    assert_eq!(set_panic, get_panic);
}
#[tokio::test]
async fn context_attributes() {
    let ctx: Context = Context::default();
    ctx.set_attribute("key1", "value1".to_string()).await;
    let value: Option<String> = ctx.try_get_attribute("key1").await;
    assert_eq!(value, Some("value1".to_string()));
    ctx.remove_attribute("key1").await;
    let value: Option<String> = ctx.try_get_attribute("key1").await;
    assert_eq!(value, None);
    ctx.set_attribute("key2", 123).await;
    ctx.clear_attribute().await;
    let value: Option<i32> = ctx.try_get_attribute("key2").await;
    assert_eq!(value, None);
}
#[tokio::test]
async fn get_panic_from_join_error() {
    let message: &'static str = "Test panic message";
    let join_handle: JoinHandle<()> = spawn(async {
        panic!("{}", message.to_string());
    });
    let join_error: JoinError = join_handle.await.unwrap_err();
    let panic_struct: PanicData = PanicData::from_join_error(join_error);
    assert!(!panic_struct.get_message().is_none());
    assert!(
        panic_struct
            .get_message()
            .clone()
            .unwrap_or_default()
            .contains(message)
    );
}
#[tokio::test]
async fn run_set_func() {
    let ctx: Context = Context::default();
    const KEY: &str = "string";
    const PARAM: &str = "test";
    let func: &(dyn Fn(&str) -> String + Send + Sync) = &|msg: &str| msg.to_string();
    ctx.set_attribute(KEY, func).await;
    let get_key: &(dyn Fn(&str) -> String + Send + Sync) =
        ctx.try_get_attribute(KEY).await.unwrap();
    assert_eq!(get_key(PARAM), func(PARAM));
}
#[tokio::test]
async fn send_body_hook() {
    let ctx: Context = Context::default();
    async fn send_body_hook_fn(ctx: Context) {
        let _ = ctx.send_body().await;
    }
    ctx.set_hook("send_body", send_body_hook_fn).await;
    assert!(ctx.try_get_hook("send_body").await.is_some());
}
```
# Path: hyperlane/src/tests/context.rs
```rust
use crate::*;
#[tokio::test]
async fn context_aborted_and_closed() {
    let ctx: Context = Context::default();
    assert!(!ctx.get_aborted().await);
    ctx.aborted().await;
    assert!(ctx.get_aborted().await);
    ctx.cancel_aborted().await;
    assert!(!ctx.get_aborted().await);
    assert!(!ctx.get_closed().await);
    ctx.closed().await;
    assert!(ctx.get_closed().await);
    ctx.cancel_closed().await;
    assert!(!ctx.get_closed().await);
    assert!(!ctx.is_terminated().await);
    ctx.aborted().await;
    assert!(ctx.is_terminated().await);
    ctx.cancel_aborted().await;
    ctx.closed().await;
    assert!(ctx.is_terminated().await);
}
#[tokio::test]
async fn context_route_params() {
    let ctx: Context = Context::default();
    let mut params: RouteParams = RouteParams::default();
    params.insert("id".to_string(), "123".to_string());
    ctx.set_route_params(params).await;
    let id: Option<String> = ctx.try_get_route_param("id").await;
    assert_eq!(id, Some("123".to_string()));
    let name: Option<String> = ctx.try_get_route_param("name").await;
    assert_eq!(name, None);
}
#[tokio::test]
async fn context_request_and_response() {
    let ctx: Context = Context::default();
    let request: Request = Request::default();
    ctx.set_request(&request).await;
    let fetched_request: Request = ctx.get_request().await;
    assert_eq!(request.get_string(), fetched_request.get_string());
    let response: Response = Response::default();
    ctx.set_response(&response).await;
    let fetched_response: Response = ctx.get_response().await;
    assert_eq!(response.get_string(), fetched_response.get_string());
}
```
# Path: hyperlane/src/tests/config.rs
```rust
use crate::*;
#[tokio::test]
async fn config_from_str() {
    let config_str: &'static str = r#"
        {
            "host": "0.0.0.0",
            "port": 80,           
            "request_config": {
                "buffer_size": 8192,
                "max_request_line_length": 8192,
                "max_path_length": 8192,
                "max_query_length": 8192,
                "max_header_line_length": 8192,
                "max_header_count": 100,
                "max_header_key_length": 8192,
                "max_header_value_length": 8192,
                "max_body_size": 2097152,
                "max_ws_frame_size": 65536,
                "max_ws_frames": 6000,
                "http_read_timeout_ms": 6000,
                "ws_read_timeout_ms": 1800000
            },
            "nodelay": true,            
            "ttl": 64
        }
    "#;
    let config: ServerConfig = ServerConfig::from_json_str(config_str).unwrap();
    let new_config: ServerConfig = ServerConfig::new().await;
    new_config
        .host("0.0.0.0")
        .await
        .port(80)
        .await
        .request_config(RequestConfig::default())
        .await
        .enable_nodelay()
        .await
        .ttl(64)
        .await;
    assert_eq!(config, new_config);
}
```
# Path: hyperlane/src/tests/send.rs
```rust
use crate::*;
#[allow(dead_code)]
struct TestSendRoute;
impl ServerHook for TestSendRoute {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    async fn handle(self, _ctx: &Context) {}
}
#[tokio::test]
async fn server_send_sync() {
    fn assert_send<T: Send>() {}
    fn assert_sync<T: Sync>() {}
    fn assert_send_sync<T: Send + Sync>() {}
    assert_send::<Server>();
    assert_sync::<Server>();
    assert_send_sync::<Server>();
}
#[tokio::test]
async fn server_clone_across_threads() {
    let server: Server = Server::new()
        .await
        .route::<TestSendRoute>("/test")
        .await
        .clone();
    let server_clone: Server = server.clone();
    let handle: JoinHandle<&'static str> = spawn(async move {
        let _server_in_thread: Server = server_clone;
        "success"
    });
    let result: &'static str = handle.await.unwrap();
    assert_eq!(result, "success");
}
#[tokio::test]
async fn server_share_across_threads() {
    let server: Arc<Server> = Arc::new(
        Server::new()
            .await
            .route::<TestSendRoute>("/test")
            .await
            .clone(),
    );
    let server1: Arc<Server> = server.clone();
    let server2: Arc<Server> = server.clone();
    let handle1: JoinHandle<&'static str> = spawn(async move {
        let _server_in_thread1: Arc<Server> = server1;
        "thread1"
    });
    let handle2: JoinHandle<&'static str> = spawn(async move {
        let _server_in_thread2: Arc<Server> = server2;
        "thread2"
    });
    let result1: &'static str = handle1.await.unwrap();
    let result2: &'static str = handle2.await.unwrap();
    assert_eq!(result1, "thread1");
    assert_eq!(result2, "thread2");
}
```
# Path: hyperlane/src/tests/panic.rs
```rust
use crate::*;
#[test]
fn panic_new() {
    let panic: PanicData = PanicData::new(
        Some("message".to_string()),
        Some("location".to_string()),
        Some("payload".to_string()),
    );
    assert_eq!(panic.get_message(), &Some("message".to_string()));
    assert_eq!(panic.get_location(), &Some("location".to_string()));
    assert_eq!(panic.get_payload(), &Some("payload".to_string()));
}
#[tokio::test]
async fn from_join_error() {
    let handle: JoinHandle<()> = tokio::spawn(async {
        panic!("test panic");
    });
    let result: Result<(), JoinError> = handle.await;
    assert!(result.is_err());
    if let Err(join_error) = result {
        let is_panic: bool = PanicData::from_join_error(join_error)
            .get_message()
            .clone()
            .unwrap_or_default()
            .contains("test panic");
        assert!(is_panic);
    }
}
```
# Path: hyperlane/src/config/mod.rs
```rust
pub(crate) mod r#impl;
pub(crate) mod r#struct;
pub(crate) mod r#type;
pub use r#struct::*;
pub(super) use r#type::*;
```
# Path: hyperlane/src/config/struct.rs
```rust
use crate::*;
#[derive(Clone, Data, CustomDebug, DisplayDebug, PartialEq, Eq, Deserialize, Serialize)]
pub(crate) struct ServerConfigInner {
    #[get(pub(crate))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    pub(super) host: String,
    #[get(pub(crate))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    pub(super) port: u16,
    #[get(pub(crate))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    pub(super) request_config: RequestConfig,
    #[get(pub(crate))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    pub(super) nodelay: Option<bool>,
    #[get(pub(crate))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    pub(super) ttl: Option<u32>,
}
#[derive(Clone, Getter, CustomDebug, DisplayDebug)]
pub struct ServerConfig(#[get(pub(super))] pub(super) SharedServerConfig);
```
# Path: hyperlane/src/config/impl.rs
```rust
use crate::*;
impl Default for ServerConfigInner {
    #[inline(always)]
    fn default() -> Self {
        Self {
            host: DEFAULT_HOST.to_owned(),
            port: DEFAULT_WEB_PORT,
            request_config: RequestConfig::default(),
            nodelay: DEFAULT_NODELAY,
            ttl: DEFAULT_TTI,
        }
    }
}
impl Default for ServerConfig {
    #[inline(always)]
    fn default() -> Self {
        Self(arc_rwlock(ServerConfigInner::default()))
    }
}
impl PartialEq for ServerConfig {
    #[inline(always)]
    fn eq(&self, other: &Self) -> bool {
        if Arc::ptr_eq(self.get_0(), other.get_0()) {
            return true;
        }
        if let (Ok(s), Ok(o)) = (self.get_0().try_read(), other.get_0().try_read()) {
            *s == *o
        } else {
            false
        }
    }
}
impl Eq for ServerConfig {}
impl ServerConfig {
    #[inline(always)]
    pub async fn new() -> Self {
        Self::default()
    }
    async fn read(&self) -> ConfigReadGuard<'_> {
        self.get_0().read().await
    }
    async fn write(&self) -> ConfigWriteGuard<'_> {
        self.get_0().write().await
    }
    pub(crate) async fn get_inner(&self) -> ServerConfigInner {
        self.read().await.clone()
    }
    pub async fn host<H: ToString>(&self, host: H) -> &Self {
        self.write().await.set_host(host.to_string());
        self
    }
    pub async fn port(&self, port: u16) -> &Self {
        self.write().await.set_port(port);
        self
    }
    pub async fn request_config(&self, request_config: RequestConfig) -> &Self {
        self.write().await.set_request_config(request_config);
        self
    }
    pub async fn nodelay(&self, nodelay: bool) -> &Self {
        self.write().await.set_nodelay(Some(nodelay));
        self
    }
    pub async fn enable_nodelay(&self) -> &Self {
        self.nodelay(true).await
    }
    pub async fn disable_nodelay(&self) -> &Self {
        self.nodelay(false).await
    }
    pub async fn ttl(&self, ttl: u32) -> &Self {
        self.write().await.set_ttl(Some(ttl));
        self
    }
    pub fn from_json_str(config_str: &str) -> Result<ServerConfig, serde_json::Error> {
        serde_json::from_str(config_str).map(|config: ServerConfigInner| Self(arc_rwlock(config)))
    }
}
```
# Path: hyperlane/src/config/type.rs
```rust
use crate::*;
pub(crate) type ConfigReadGuard<'a> = RwLockReadGuard<'a, ServerConfigInner>;
pub(crate) type ConfigWriteGuard<'a> = RwLockWriteGuard<'a, ServerConfigInner>;
```
# Path: hyperlane/src/error/mod.rs
```rust
pub(crate) mod r#enum;
pub use r#enum::*;
```
# Path: hyperlane/src/error/enum.rs
```rust
use crate::*;
#[derive(CustomDebug, DisplayDebug, PartialEq, Eq, Clone)]
pub enum ServerError {
    TcpBind(String),
    Unknown(String),
    HttpRead(String),
    InvalidHttpRequest(Request),
    Other(String),
}
#[derive(CustomDebug, DisplayDebug, PartialEq, Eq, Clone)]
pub enum RouteError {
    EmptyPattern,
    DuplicatePattern(String),
    InvalidRegexPattern(String),
}
```
# Path: hyperlane/src/route/mod.rs
```rust
pub(crate) mod r#enum;
pub(crate) mod r#impl;
pub(crate) mod r#struct;
pub(crate) mod r#type;
pub use r#struct::*;
pub use r#type::*;
pub use r#enum::*;
```
# Path: hyperlane/src/route/enum.rs
```rust
use crate::*;
#[derive(Clone, CustomDebug, DisplayDebug)]
pub enum RouteSegment {
    Static(String),
    Dynamic(String),
    Regex(String, Regex),
}
```
# Path: hyperlane/src/route/struct.rs
```rust
use crate::*;
#[derive(Debug, Clone, Getter, DisplayDebug)]
pub struct RoutePattern(
    #[get]
    pub(super) RouteSegmentList,
);
#[derive(Clone, CustomDebug, Getter, GetterMut, DisplayDebug, Setter)]
pub struct RouteMatcher {
    #[get]
    #[set(skip)]
    #[get_mut(pub(super))]
    #[debug(skip)]
    pub(super) static_route: ServerHookMap,
    #[get]
    #[set(skip)]
    #[get_mut(pub(super))]
    #[debug(skip)]
    pub(super) dynamic_route: ServerHookPatternRoute,
    #[get]
    #[set(skip)]
    #[get_mut(pub(super))]
    #[debug(skip)]
    pub(super) regex_route: ServerHookPatternRoute,
}
```
# Path: hyperlane/src/route/impl.rs
```rust
use crate::*;
collect!(HookType);
impl Default for RouteMatcher {
    #[inline(always)]
    fn default() -> Self {
        Self {
            static_route: hash_map_xx_hash3_64(),
            dynamic_route: hash_map_xx_hash3_64(),
            regex_route: hash_map_xx_hash3_64(),
        }
    }
}
impl PartialEq for RoutePattern {
    #[inline(always)]
    fn eq(&self, other: &Self) -> bool {
        self.get_0() == other.get_0()
    }
}
impl Eq for RoutePattern {}
impl Hash for RoutePattern {
    #[inline(always)]
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.get_0().hash(state);
    }
}
impl PartialOrd for RoutePattern {
    #[inline(always)]
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}
impl Ord for RoutePattern {
    #[inline(always)]
    fn cmp(&self, other: &Self) -> Ordering {
        self.get_0().cmp(other.get_0())
    }
}
impl PartialEq for RouteMatcher {
    fn eq(&self, other: &Self) -> bool {
        if self.get_static_route().len() != other.get_static_route().len() {
            return false;
        }
        for key in self.get_static_route().keys() {
            if !other.get_static_route().contains_key(key) {
                return false;
            }
        }
        if self.get_dynamic_route().len() != other.get_dynamic_route().len() {
            return false;
        }
        for (segment_count, routes) in self.get_dynamic_route() {
            match other.get_dynamic_route().get(segment_count) {
                Some(other_routes) if routes.len() == other_routes.len() => {
                    for (pattern, _) in routes {
                        if !other_routes.iter().any(|(p, _)| p == pattern) {
                            return false;
                        }
                    }
                }
                _ => return false,
            }
        }
        if self.get_regex_route().len() != other.get_regex_route().len() {
            return false;
        }
        for (segment_count, routes) in self.get_regex_route() {
            match other.get_regex_route().get(segment_count) {
                Some(other_routes) if routes.len() == other_routes.len() => {
                    for (pattern, _) in routes {
                        if !other_routes.iter().any(|(p, _)| p == pattern) {
                            return false;
                        }
                    }
                }
                _ => return false,
            }
        }
        true
    }
}
impl Eq for RouteMatcher {}
impl Eq for RouteSegment {}
impl PartialOrd for RouteSegment {
    #[inline(always)]
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}
impl Ord for RouteSegment {
    #[inline(always)]
    fn cmp(&self, other: &Self) -> Ordering {
        match (self, other) {
            (Self::Static(s1), Self::Static(s2)) => s1.cmp(s2),
            (Self::Dynamic(d1), Self::Dynamic(d2)) => d1.cmp(d2),
            (Self::Regex(n1, r1), Self::Regex(n2, r2)) => {
                n1.cmp(n2).then_with(|| r1.as_str().cmp(r2.as_str()))
            }
            (Self::Static(_), _) => Ordering::Less,
            (_, Self::Static(_)) => Ordering::Greater,
            (Self::Dynamic(_), _) => Ordering::Less,
            (_, Self::Dynamic(_)) => Ordering::Greater,
        }
    }
}
impl PartialEq for RouteSegment {
    #[inline(always)]
    fn eq(&self, other: &Self) -> bool {
        match (self, other) {
            (Self::Static(l0), Self::Static(r0)) => l0 == r0,
            (Self::Dynamic(l0), Self::Dynamic(r0)) => l0 == r0,
            (Self::Regex(l0, l1), Self::Regex(r0, r1)) => l0 == r0 && l1.as_str() == r1.as_str(),
            _ => false,
        }
    }
}
impl Hash for RouteSegment {
    #[inline(always)]
    fn hash<H: Hasher>(&self, state: &mut H) {
        match self {
            Self::Static(s) => {
                0u8.hash(state);
                s.hash(state);
            }
            Self::Dynamic(d) => {
                1u8.hash(state);
                d.hash(state);
            }
            Self::Regex(name, regex) => {
                2u8.hash(state);
                name.hash(state);
                regex.as_str().hash(state);
            }
        }
    }
}
impl RoutePattern {
    pub(crate) fn new(route: &str) -> Result<RoutePattern, RouteError> {
        Ok(Self(Self::parse_route(route)?))
    }
    fn parse_route(route: &str) -> Result<RouteSegmentList, RouteError> {
        if route.is_empty() {
            return Err(RouteError::EmptyPattern);
        }
        let route: &str = route.trim_start_matches(DEFAULT_HTTP_PATH);
        if route.is_empty() {
            return Ok(Vec::new());
        }
        let estimated_segments: usize = route.matches(DEFAULT_HTTP_PATH).count() + 1;
        let mut segments: RouteSegmentList = Vec::with_capacity(estimated_segments);
        for segment in route.split(DEFAULT_HTTP_PATH) {
            if segment.starts_with(LEFT_BRACKET) && segment.ends_with(RIGHT_BRACKET) {
                let content: &str = &segment[1..segment.len() - 1];
                if let Some((name, pattern)) = content.split_once(COLON) {
                    match Regex::new(pattern) {
                        Ok(regex) => {
                            segments.push(RouteSegment::Regex(name.to_owned(), regex));
                        }
                        Err(error) => {
                            return Err(RouteError::InvalidRegexPattern(format!(
                                "Invalid regex pattern '{}{}{}",
                                pattern, COLON, error
                            )));
                        }
                    }
                } else {
                    segments.push(RouteSegment::Dynamic(content.to_owned()));
                }
            } else {
                segments.push(RouteSegment::Static(segment.to_owned()));
            }
        }
        Ok(segments)
    }
    pub(crate) fn try_match_path(&self, path: &str) -> Option<RouteParams> {
        let path: &str = path.trim_start_matches(DEFAULT_HTTP_PATH);
        let route_segments_len: usize = self.get_0().len();
        let is_tail_regex: bool = matches!(self.get_0().last(), Some(RouteSegment::Regex(_, _)));
        if path.is_empty() {
            if route_segments_len == 0 {
                return Some(hash_map_xx_hash3_64());
            }
            return None;
        }
        let mut path_segments: PathComponentList = Vec::with_capacity(route_segments_len);
        let path_bytes: &[u8] = path.as_bytes();
        let path_separator_byte: u8 = DEFAULT_HTTP_PATH_BYTES[0];
        let mut segment_start: usize = 0;
        for (i, &byte) in path_bytes.iter().enumerate() {
            if byte == path_separator_byte {
                if segment_start < i {
                    path_segments.push(&path[segment_start..i]);
                }
                segment_start = i + 1;
            }
        }
        if segment_start < path.len() {
            path_segments.push(&path[segment_start..]);
        }
        let path_segments_len: usize = path_segments.len();
        if (!is_tail_regex && path_segments_len != route_segments_len)
            || (is_tail_regex && path_segments_len < route_segments_len - 1)
        {
            return None;
        }
        let mut params: RouteParams = hash_map_xx_hash3_64();
        for (idx, segment) in self.get_0().iter().enumerate() {
            match segment {
                RouteSegment::Static(expected_path) => {
                    if path_segments.get(idx).copied() != Some(expected_path.as_str()) {
                        return None;
                    }
                }
                RouteSegment::Dynamic(param_name) => {
                    params.insert(param_name.clone(), path_segments.get(idx)?.to_string());
                }
                RouteSegment::Regex(param_name, regex) => {
                    let segment_value: String = if idx == route_segments_len - 1 {
                        path_segments[idx..].join(DEFAULT_HTTP_PATH)
                    } else {
                        match path_segments.get(idx) {
                            Some(val) => val.to_string(),
                            None => return None,
                        }
                    };
                    if let Some(mat) = regex.find(&segment_value) {
                        if mat.start() != 0 || mat.end() != segment_value.len() {
                            return None;
                        }
                    } else {
                        return None;
                    }
                    params.insert(param_name.clone(), segment_value);
                    if idx == route_segments_len - 1 {
                        return Some(params);
                    }
                }
            }
        }
        Some(params)
    }
    #[inline(always)]
    pub(crate) fn is_static(&self) -> bool {
        self.get_0()
            .iter()
            .all(|seg| matches!(seg, RouteSegment::Static(_)))
    }
    #[inline(always)]
    pub(crate) fn is_dynamic(&self) -> bool {
        self.get_0()
            .iter()
            .any(|seg| matches!(seg, RouteSegment::Dynamic(_)))
            && self
                .get_0()
                .iter()
                .all(|seg| !matches!(seg, RouteSegment::Regex(_, _)))
    }
    #[inline(always)]
    pub(crate) fn segment_count(&self) -> usize {
        self.get_0().len()
    }
    #[inline(always)]
    pub(crate) fn has_tail_regex(&self) -> bool {
        matches!(self.get_0().last(), Some(RouteSegment::Regex(_, _)))
    }
}
impl RouteMatcher {
    #[inline(always)]
    pub(crate) fn new() -> Self {
        Self::default()
    }
    #[inline(always)]
    fn count_path_segments(path: &str) -> usize {
        let path: &str = path.trim_start_matches(DEFAULT_HTTP_PATH);
        if path.is_empty() {
            return 0;
        }
        path.matches(DEFAULT_HTTP_PATH).count() + 1
    }
    pub(crate) fn add(&mut self, pattern: &str, hook: ServerHookHandler) -> Result<(), RouteError> {
        let route_pattern: RoutePattern = RoutePattern::new(pattern)?;
        if route_pattern.is_static() {
            if self.get_static_route().contains_key(pattern) {
                return Err(RouteError::DuplicatePattern(pattern.to_owned()));
            }
            self.get_mut_static_route()
                .insert(pattern.to_string(), hook);
            return Ok(());
        }
        let target_map: &mut ServerHookPatternRoute = if route_pattern.is_dynamic() {
            self.get_mut_dynamic_route()
        } else {
            self.get_mut_regex_route()
        };
        let segment_count: usize = route_pattern.segment_count();
        let routes_for_count: &mut Vec<(RoutePattern, ServerHookHandler)> =
            target_map.entry(segment_count).or_default();
        match routes_for_count.binary_search_by(|(p, _)| p.cmp(&route_pattern)) {
            Ok(_) => return Err(RouteError::DuplicatePattern(pattern.to_owned())),
            Err(pos) => routes_for_count.insert(pos, (route_pattern, hook)),
        }
        Ok(())
    }
    pub(crate) async fn try_resolve_route(
        &self,
        ctx: &Context,
        path: &str,
    ) -> Option<ServerHookHandler> {
        if let Some(hook) = self.get_static_route().get(path) {
            ctx.set_route_params(RouteParams::default()).await;
            return Some(hook.clone());
        }
        let path_segment_count: usize = Self::count_path_segments(path);
        if let Some(routes) = self.get_dynamic_route().get(&path_segment_count) {
            for (pattern, hook) in routes {
                if let Some(params) = pattern.try_match_path(path) {
                    ctx.set_route_params(params).await;
                    return Some(hook.clone());
                }
            }
        }
        if let Some(routes) = self.get_regex_route().get(&path_segment_count) {
            for (pattern, hook) in routes {
                if let Some(params) = pattern.try_match_path(path) {
                    ctx.set_route_params(params).await;
                    return Some(hook.clone());
                }
            }
        }
        for (&segment_count, routes) in self.get_regex_route() {
            if segment_count == path_segment_count {
                continue;
            }
            for (pattern, hook) in routes {
                if pattern.has_tail_regex()
                    && path_segment_count >= segment_count
                    && let Some(params) = pattern.try_match_path(path)
                {
                    ctx.set_route_params(params).await;
                    return Some(hook.clone());
                }
            }
        }
        None
    }
}
```
# Path: hyperlane/src/route/type.rs
```rust
use crate::*;
pub type RouteParams = HashMapXxHash3_64<String, String>;
pub type RouteSegmentList = Vec<RouteSegment>;
pub(crate) type PathComponentList<'a> = Vec<&'a str>;
```
# Path: hyperlane-time/README.md
## hyperlane-time
[Official Documentation](https://docs.ltpp.vip/hyperlane-time/)
[Api Docs](https://docs.rs/hyperlane-time/latest/hyperlane_time/)
> A library for fetching the current time based on the system's locale settings.
## Installation
To use this crate, you can run cmd:
```shell
cargo add hyperlane-time
```
## Contact
# Path: hyperlane-time/src/lib.rs
```rust
pub(crate) mod time;
pub use time::r#fn::*;
pub(crate) use time::r#enum::*;
pub(crate) use std::{
    env, fmt,
    fmt::Write,
    str::FromStr,
    time::{Duration, SystemTime, UNIX_EPOCH},
};
```
# Path: hyperlane-time/src/time/mod.rs
```rust
pub(crate) mod cfg;
pub(crate) mod r#enum;
pub(crate) mod r#fn;
pub(crate) mod r#impl;
```
# Path: hyperlane-time/src/time/enum.rs
```rust
#[derive(Debug, Default, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum Lang {
    EnUsUtf8,
    #[default]
    ZhCnUtf8,
    FrFrUtf8,
    DeDeUtf8,
    EsEsUtf8,
    ItItUtf8,
    JaJpUtf8,
    KoKrUtf8,
    PtPtUtf8,
    RuRuUtf8,
    ArSaUtf8,
    HiInUtf8,
    ThThUtf8,
    ViVnUtf8,
    NlNlUtf8,
    SvSeUtf8,
    FiFiUtf8,
}
```
# Path: hyperlane-time/src/time/fn.rs
```rust
use crate::*;
pub const LEAP_YEAR: [u64; 12] = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
pub const COMMON_YEAR: [u64; 12] = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
pub const DAYS: [&str; 7] = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
pub const MONTHS: [&str; 12] = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];
pub fn from_env_var() -> Lang {
    let lang: Lang = env::var("LANG")
        .unwrap_or_default()
        .parse::<Lang>()
        .unwrap_or_default();
    lang
}
#[inline(always)]
pub fn is_leap_year(year: u64) -> bool {
    (year.is_multiple_of(4) && !year.is_multiple_of(100)) || year.is_multiple_of(400)
}
pub fn time() -> String {
    let (year, month, day, hour, minute, second, _, _) = calculate_time();
    let mut date_time: String = String::new();
    write!(
        &mut date_time,
        "{year:04}-{month:02}-{day:02} {hour:02}:{minute:02}:{second:02}"
    )
    .unwrap_or_default();
    date_time
}
pub fn date() -> String {
    let (year, month, day, _, _, _, _, _) = calculate_time();
    let mut date_time: String = String::new();
    write!(&mut date_time, "{year:04}-{month:02}-{day:02}").unwrap_or_default();
    date_time
}
pub fn compute_date(mut days_since_epoch: u64) -> (u64, u64, u64) {
    let mut year: u64 = 1970;
    loop {
        let days_in_year: u64 = if is_leap_year(year) { 366 } else { 365 };
        if days_since_epoch < days_in_year {
            break;
        }
        days_since_epoch -= days_in_year as u64;
        year += 1;
    }
    let mut month: u64 = 0;
    for (i, &days) in COMMON_YEAR.iter().enumerate() {
        let days_in_month = if i == 1 && is_leap_year(year) {
            days + 1
        } else {
            days
        };
        if days_since_epoch < days_in_month as u64 {
            month = i as u64 + 1;
            return (year, month, days_since_epoch + 1);
        }
        days_since_epoch -= days_in_month as u64;
    }
    (year, month, 1)
}
pub fn gmt() -> String {
    let now: SystemTime = SystemTime::now();
    let duration_since_epoch: Duration = now.duration_since(UNIX_EPOCH).unwrap();
    let timestamp: u64 = duration_since_epoch.as_secs();
    let seconds_in_day: u64 = 86_400;
    let days_since_epoch: u64 = timestamp / seconds_in_day;
    let seconds_of_day: u64 = timestamp % seconds_in_day;
    let hours: u64 = seconds_of_day / 3600;
    let minutes: u64 = (seconds_of_day % 3600) / 60;
    let seconds: u64 = seconds_of_day % 60;
    let (year, month, day) = compute_date(days_since_epoch);
    let weekday: usize = ((days_since_epoch + 4) % 7) as usize;
    format!(
        "{}, {:02} {} {} {:02}:{:02}:{:02} GMT",
        DAYS[weekday],
        day,
        MONTHS[month as usize - 1],
        year,
        hours,
        minutes,
        seconds
    )
}
pub fn year() -> u64 {
    calculate_time().0
}
pub fn month() -> u64 {
    calculate_time().1
}
pub fn day() -> u64 {
    calculate_time().2
}
pub fn hour() -> u64 {
    calculate_time().3
}
pub fn minute() -> u64 {
    calculate_time().4
}
pub fn second() -> u64 {
    calculate_time().5
}
pub fn millis() -> u64 {
    calculate_time().6
}
pub fn micros() -> u64 {
    calculate_time().7
}
pub fn calculate_time() -> (u64, u64, u64, u64, u64, u64, u64, u64) {
    let start: SystemTime = SystemTime::now();
    let duration: Duration = start.duration_since(UNIX_EPOCH).unwrap();
    let total_seconds: u64 = duration.as_secs();
    let nanoseconds: u64 = duration.subsec_nanos() as u64;
    let milliseconds: u64 = nanoseconds / 1_000_000;
    let microseconds: u64 = nanoseconds / 1_000;
    let mut total_days: u64 = total_seconds / 86400;
    let mut year: u64 = 1970;
    while total_days >= if is_leap_year(year) { 366 } else { 365 } {
        total_days -= if is_leap_year(year) { 366 } else { 365 };
        year += 1;
    }
    let mut month: u64 = 1;
    let month_days: [u64; 12] = if is_leap_year(year) {
        LEAP_YEAR
    } else {
        COMMON_YEAR
    };
    while total_days >= month_days[month as usize - 1] {
        total_days -= month_days[month as usize - 1];
        month += 1;
    }
    let day: u64 = total_days + 1;
    let remaining_seconds: u64 = total_seconds % 86400;
    let timezone_offset: u64 = from_env_var().value();
    let hour: u64 = ((remaining_seconds + timezone_offset) / 3600) % 24;
    let minute: u64 = (remaining_seconds % 3600) / 60;
    let second: u64 = remaining_seconds % 60;
    (
        year,
        month,
        day,
        hour,
        minute,
        second,
        milliseconds,
        microseconds,
    )
}
pub fn time_millis() -> String {
    let (year, month, day, hour, minute, second, millisecond, _) = calculate_time();
    let mut date_time: String = String::new();
    write!(
        &mut date_time,
        "{year:04}-{month:02}-{day:02} {hour:02}:{minute:02}:{second:02}.{millisecond:03}"
    )
    .unwrap_or_default();
    date_time
}
pub fn time_micros() -> String {
    let (year, month, day, hour, minute, second, _, microseconds) = calculate_time();
    let mut date_time: String = String::new();
    write!(
        &mut date_time,
        "{year:04}-{month:02}-{day:02} {hour:02}:{minute:02}:{second:02}.{microseconds:06}"
    )
    .unwrap_or_default();
    date_time
}
pub fn timestamp() -> u64 {
    let timezone_offset: u64 = from_env_var().value();
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_secs()
        .saturating_add(timezone_offset)
}
pub fn timestamp_millis() -> u64 {
    let timezone_offset: u64 = from_env_var().value();
    let duration: Duration = SystemTime::now().duration_since(UNIX_EPOCH).unwrap();
    (duration.as_secs().saturating_add(timezone_offset)) * 1000 + duration.subsec_millis() as u64
}
pub fn timestamp_micros() -> u64 {
    let timezone_offset: u64 = from_env_var().value();
    let duration: Duration = SystemTime::now().duration_since(UNIX_EPOCH).unwrap();
    (duration.as_secs().saturating_add(timezone_offset)) * 1_000_000
        + duration.subsec_micros() as u64
}
```
# Path: hyperlane-time/src/time/impl.rs
```rust
use crate::*;
impl fmt::Display for Lang {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        let lang_str: &str = match self {
            Lang::EnUsUtf8 => "English (US)",
            Lang::ZhCnUtf8 => "中文 (中国)",
            Lang::FrFrUtf8 => "Français (France)",
            Lang::DeDeUtf8 => "Deutsch (Deutschland)",
            Lang::EsEsUtf8 => "Español (España)",
            Lang::ItItUtf8 => "Italiano (Italia)",
            Lang::JaJpUtf8 => "日本語 (日本)",
            Lang::KoKrUtf8 => "한국어 (한국)",
            Lang::PtPtUtf8 => "Português (Portugal)",
            Lang::RuRuUtf8 => "Русский (Россия)",
            Lang::ArSaUtf8 => "العربية (السعودية)",
            Lang::HiInUtf8 => "हिन्दी (भारत)",
            Lang::ThThUtf8 => "ภาษาไทย (ประเทศไทย)",
            Lang::ViVnUtf8 => "Tiếng Việt (Việt Nam)",
            Lang::NlNlUtf8 => "Nederlands (Nederland)",
            Lang::SvSeUtf8 => "Svenska (Sverige)",
            Lang::FiFiUtf8 => "Suomi (Suomi)",
        };
        write!(f, "{lang_str}")
    }
}
impl Lang {
    pub fn value(&self) -> u64 {
        match self {
            Lang::EnUsUtf8 => 0,     
            Lang::ZhCnUtf8 => 28800, 
            Lang::FrFrUtf8 => 3600,  
            Lang::DeDeUtf8 => 3600,  
            Lang::EsEsUtf8 => 3600,  
            Lang::ItItUtf8 => 3600,  
            Lang::JaJpUtf8 => 32400, 
            Lang::KoKrUtf8 => 32400, 
            Lang::PtPtUtf8 => 3600,  
            Lang::RuRuUtf8 => 10800, 
            Lang::ArSaUtf8 => 10800, 
            Lang::HiInUtf8 => 19800, 
            Lang::ThThUtf8 => 25200, 
            Lang::ViVnUtf8 => 25200, 
            Lang::NlNlUtf8 => 3600,  
            Lang::SvSeUtf8 => 3600,  
            Lang::FiFiUtf8 => 3600,  
        }
    }
}
impl FromStr for Lang {
    type Err = ();
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s {
            "en_US.UTF-8" => Ok(Lang::EnUsUtf8),
            "zh_CN.UTF-8" => Ok(Lang::ZhCnUtf8),
            "fr_FR.UTF-8" => Ok(Lang::FrFrUtf8),
            "de_DE.UTF-8" => Ok(Lang::DeDeUtf8),
            "es_ES.UTF-8" => Ok(Lang::EsEsUtf8),
            "it_IT.UTF-8" => Ok(Lang::ItItUtf8),
            "ja_JP.UTF-8" => Ok(Lang::JaJpUtf8),
            "ko_KR.UTF-8" => Ok(Lang::KoKrUtf8),
            "pt_PT.UTF-8" => Ok(Lang::PtPtUtf8),
            "ru_RU.UTF-8" => Ok(Lang::RuRuUtf8),
            "ar_SA.UTF-8" => Ok(Lang::ArSaUtf8),
            "hi_IN.UTF-8" => Ok(Lang::HiInUtf8),
            "th_TH.UTF-8" => Ok(Lang::ThThUtf8),
            "vi_VN.UTF-8" => Ok(Lang::ViVnUtf8),
            "nl_NL.UTF-8" => Ok(Lang::NlNlUtf8),
            "sv_SE.UTF-8" => Ok(Lang::SvSeUtf8),
            "fi_FI.UTF-8" => Ok(Lang::FiFiUtf8),
            _ => Err(()),
        }
    }
}
```
# Path: hyperlane-time/src/time/cfg.rs
```rust
#[test]
fn test_lang() {
    use crate::*;
    println!("test_lang: {}", from_env_var());
}
#[test]
fn test_now_time() {
    use crate::*;
    println!("test_now_time: {}", time());
}
#[test]
fn test_methods() {
    use crate::*;
    println!("Current Time: {}", time());
    println!("Current Date: {}", date());
    println!("GMT Date: {}", gmt());
    println!("Timestamp (s): {}", timestamp());
    println!("Timestamp (ms): {}", timestamp_millis());
    println!("Timestamp (μs): {}", timestamp_micros());
    println!("Current Year: {}", year());
    println!("Current Month: {}", month());
    println!("Current Day: {}", day());
    println!("Current Hour: {}", hour());
    println!("Current Minute: {}", minute());
    println!("Current Second: {}", second());
    println!("Current Millis: {}", millis());
    println!("Current Micros: {}", micros());
    println!("Is Leap Year (1949): {}", is_leap_year(1949));
    println!("Calculate Current Time: {:?}", calculate_time());
    println!("Compute Date (10000 days): {:?}", compute_date(10000));
    println!("Current Time with Millis: {}", time_millis());
    println!("Current Time with Micros: {}", time_micros());
}
```
# Path: hyperlane-macros/README.md
## hyperlane-macros
[Official Documentation](https://docs.ltpp.vip/hyperlane-macros/)
[Api Docs](https://docs.rs/hyperlane-macros/latest/hyperlane_macros/)
> A comprehensive collection of procedural macros for building HTTP servers with enhanced functionality. This crate provides attribute macros that simplify HTTP request handling, protocol validation, response management, and request data extraction.
## Installation
To use this crate, you can run cmd:
```shell
cargo add hyperlane-macros
```
## Available Macros
### Hyperlane Macro
- `#[hyperlane(server: Server)]` - Creates a new `Server` instance with the specified variable name and type, and automatically registers other hooks and routes defined within the crate.
- `#[hyperlane(config: ServerConfig)]` - Creates a new `ServerConfig` instance with the specified variable name and type.
- `#[hyperlane(var1: Type1, var2: Type2, ...)]` - Supports multiple instance initialization in a single call
### HTTP Method Macros
- `#[methods(method1, method2, ...)]` - Accepts multiple HTTP methods
- `#[get]` - GET method handler
- `#[post]` - POST method handler
- `#[put]` - PUT method handler
- `#[delete]` - DELETE method handler
- `#[patch]` - PATCH method handler
- `#[head]` - HEAD method handler
- `#[options]` - OPTIONS method handler
- `#[connect]` - CONNECT method handler
- `#[trace]` - TRACE method handler
### Protocol Check Macros
- `#[ws]` - WebSocket check, ensures function only executes for WebSocket upgrade requests
- `#[http]` - HTTP check, ensures function only executes for standard HTTP requests
- `#[h2c]` - HTTP/2 Cleartext check, ensures function only executes for HTTP/2 cleartext requests
- `#[http0_9]` - HTTP/0.9 check, ensures function only executes for HTTP/0.9 protocol requests
- `#[http1_0]` - HTTP/1.0 check, ensures function only executes for HTTP/1.0 protocol requests
- `#[http1_1]` - HTTP/1.1 check, ensures function only executes for HTTP/1.1 protocol requests
- `#[http1_1_or_higher]` - HTTP/1.1 or higher version check, ensures function only executes for HTTP/1.1 or newer protocol versions
- `#[http2]` - HTTP/2 check, ensures function only executes for HTTP/2 protocol requests
- `#[http3]` - HTTP/3 check, ensures function only executes for HTTP/3 protocol requests
- `#[tls]` - TLS check, ensures function only executes for TLS-secured connections
### Response Setting Macros
- `#[response_status_code(code)]` - Set response status code (supports literals and global constants)
- `#[response_reason_phrase("phrase")]` - Set response reason phrase (supports literals and global constants)
- `#[response_header("key", "value")]` - Add response header (supports literals and global constants)
- `#[response_header("key" => "value")]` - Set response header (supports literals and global constants)
- `#[response_body("data")]` - Set response body (supports literals and global constants)
- `#[response_version(version)]` - Set response HTTP version (supports literals and global constants)
- `#[clear_response_headers]` - Clear all response headers
### Send Operation Macros
- `#[try_send]` - Try to send complete response (headers and body) after function execution (returns Result)
- `#[send]` - Send complete response (headers and body) after function execution (**panics on failure**)
- `#[try_send_body]` - Try to send only response body after function execution (returns Result)
- `#[send_body]` - Send only response body after function execution (**panics on failure**)
- `#[try_send_body_with_data("data")]` - Try to send only response body with specified data after function execution (returns Result)
- `#[send_body_with_data("data")]` - Send only response body with specified data after function execution (**panics on failure**)
### Flush Macros
- `#[try_flush]` - Try to flush response stream after function execution to ensure immediate data transmission (returns Result)
- `#[flush]` - Flush response stream after function execution to ensure immediate data transmission (**panics on failure**)
### Aborted Macros
- `#[aborted]` - Handle aborted requests, providing cleanup logic for prematurely terminated connections
### Closed Operation Macros
- `#[closed]` - Handle closed streams, providing cleanup logic for completed connections
### Conditional Macros
- `#[filter(condition)]` - Continues execution only if the `condition` (a code block returning a boolean) is `true`.
- `#[reject(condition)]` - Continues execution only if the `condition` (a code block returning a boolean) is `false`.
### Request Body Macros
- `#[request_body(variable_name)]` - Extract raw request body into specified variable with RequestBody type
- `#[request_body(var1, var2, ...)]` - Supports multiple request body variables
- `#[request_body_json(variable_name: type)]` - Parse request body as JSON into specified variable and type
- `#[request_body_json(var1: Type1, var2: Type2, ...)]` - Supports multiple JSON body parsing
### Attribute Macros
- `#[attribute_option(key => variable_name: type)]` - Extract a specific attribute by key into a typed variable
- `#[attribute_option("key1" => var1: Type1, "key2" => var2: Type2, ...)]` - Supports multiple attribute extraction
- `#[attribute(key => variable_name: type)]` - Extract a specific attribute by key into a typed variable
- `#[attribute("key1" => var1: Type1, "key2" => var2: Type2, ...)]` - Supports multiple attribute extraction
### Attributes Macros
- `#[attributes(variable_name)]` - Get all attributes as a HashMap for comprehensive attribute access
- `#[attributes(var1, var2, ...)]` - Supports multiple attribute collections
### Panic Data Macros
- `#[task_panic_data_option(variable_name)]` - Extract panic data into a variable wrapped in Option type
- `#[task_panic_data_option(var1, var2, ...)]` - Supports multiple panic data variables
- `#[task_panic_data(variable_name)]` - Extract panic data into a variable with panic on missing value
- `#[task_panic_data(var1, var2, ...)]` - Supports multiple panic data variables
### Request Error Data Macros
- `#[request_error_data_option(variable_name)]` - Extract request error data into a variable wrapped in Option type
- `#[request_error_data_option(var1, var2, ...)]` - Supports multiple request error data variables
- `#[request_error_data(variable_name)]` - Extract request error data into a variable with panic on missing value
- `#[request_error_data(var1, var2, ...)]` - Supports multiple request error data variables
### Route Param Macros
- `#[route_param_option(key => variable_name)]` - Extract a specific route parameter by key into a variable
- `#[route_param_option("key1" => var1, "key2" => var2, ...)]` - Supports multiple route parameter extraction
- `#[route_param(key => variable_name)]` - Extract a specific route parameter by key into a variable
- `#[route_param("key1" => var1, "key2" => var2, ...)]` - Supports multiple route parameter extraction
### Route Params Macros
- `#[route_params(variable_name)]` - Get all route parameters as a collection
- `#[route_params(var1, var2, ...)]` - Supports multiple route parameter collections
### Request Query Macros
- `#[request_query_option(key => variable_name)]` - Extract a specific query parameter by key from the URL query string
- `#[request_query_option("key1" => var1, "key2" => var2, ...)]` - Supports multiple query parameter extraction
- `#[request_query(key => variable_name)]` - Extract a specific query parameter by key from the URL query string
- `#[request_query("key1" => var1, "key2" => var2, ...)]` - Supports multiple query parameter extraction
### Request Querys Macros
- `#[request_querys(variable_name)]` - Get all query parameters as a collection
- `#[request_querys(var1, var2, ...)]` - Supports multiple query parameter collections
### Request Header Macros
- `#[request_header_option(key => variable_name)]` - Extract a specific HTTP header by name from the request
- `#[request_header_option(KEY1 => var1, KEY2 => var2, ...)]` - Supports multiple header extraction
- `#[request_header(key => variable_name)]` - Extract a specific HTTP header by name from the request
- `#[request_header(KEY1 => var1, KEY2 => var2, ...)]` - Supports multiple header extraction
### Request Headers Macros
- `#[request_headers(variable_name)]` - Get all HTTP headers as a collection
- `#[request_headers(var1, var2, ...)]` - Supports multiple header collections
### Request Cookie Macros
- `#[request_cookie_option(key => variable_name)]` - Extract a specific cookie value by key from the request cookie header
- `#[request_cookie_option("key1" => var1, "key2" => var2, ...)]` - Supports multiple cookie extraction
- `#[request_cookie(key => variable_name)]` - Extract a specific cookie value by key from the request cookie header
- `#[request_cookie("key1" => var1, "key2" => var2, ...)]` - Supports multiple cookie extraction
### Request Cookies Macros
- `#[request_cookies(variable_name)]` - Get all cookies as a raw string from the cookie header
- `#[request_cookies(var1, var2, ...)]` - Supports multiple cookie collections
### Request Version Macros
- `#[request_version(variable_name)]` - Extract the HTTP request version into a variable
- `#[request_version(var1, var2, ...)]` - Supports multiple request version variables
### Request Path Macros
- `#[request_path(variable_name)]` - Extract the HTTP request path into a variable
- `#[request_path(var1, var2, ...)]` - Supports multiple request path variables
### Host Macros
- `#[host("hostname")]` - Restrict function execution to requests with a specific host header value
- `#[host("host1", "host2", ...)]` - Supports multiple host checks
- `#[reject_host("hostname")]` - Reject requests that match a specific host header value
- `#[reject_host("host1", "host2", ...)]` - Supports multiple host rejections
### Referer Macros
- `#[referer("url")]` - Restrict function execution to requests with a specific referer header value
- `#[referer("url1", "url2", ...)]` - Supports multiple referer checks
- `#[reject_referer("url")]` - Reject requests that match a specific referer header value
- `#[reject_referer("url1", "url2", ...)]` - Supports multiple referer rejections
### Hook Macros
- `#[prologue_hooks(function_name)]` - Execute specified function before the main handler function
- `#[epilogue_hooks(function_name)]` - Execute specified function after the main handler function
- `#[task_panic]` - Execute function when a panic occurs within the server
- `#[request_error]` - Execute function when a request error occurs within the server
- `#[prologue_macros(macro1, macro2, ...)]` - Injects a list of macros before the decorated function.
- `#[epilogue_macros(macro1, macro2, ...)]` - Injects a list of macros after the decorated function.
### Middleware Macros
- `#[request_middleware]` - Register a function as a request middleware
- `#[request_middleware(order)]` - Register a function as a request middleware with specified order
- `#[response_middleware]` - Register a function as a response middleware
- `#[response_middleware(order)]` - Register a function as a response middleware with specified order
- `#[task_panic]` - Register a function as a panic hook
- `#[task_panic(order)]` - Register a function as a panic hook with specified order
- `#[request_error]` - Register a function as a request error hook
- `#[request_error(order)]` - Register a function as a request error hook with specified order
### Stream Processing Macros
- `#[http_from_stream]` - Wraps function body with HTTP stream processing, using default request config. The function body only executes if data is successfully read from the HTTP stream.
- `#[http_from_stream(request_config)]` - Wraps function body with HTTP stream processing using specified request config.
- `#[http_from_stream(variable_name)]` - Wraps function body with HTTP stream processing, storing data in specified variable name.
- `#[http_from_stream(request_config, variable_name)]` - Wraps function body with HTTP stream processing using specified request config and variable name.
- `#[http_from_stream(variable_name, request_config)]` - Wraps function body with HTTP stream processing using specified variable name and request config (reversed order).
- `#[ws_from_stream]` - Wraps function body with WebSocket stream processing, using default request config. The function body only executes if data is successfully read from the WebSocket stream.
- `#[ws_from_stream(request_config)]` - Wraps function body with WebSocket stream processing using specified request config.
- `#[ws_from_stream(variable_name)]` - Wraps function body with WebSocket stream processing, storing data in specified variable name.
- `#[ws_from_stream(request_config, variable_name)]` - Wraps function body with WebSocket stream processing using specified request config and variable name.
- `#[ws_from_stream(variable_name, request_config)]` - Wraps function body with WebSocket stream processing using specified variable name and request config (reversed order).
### Response Header Macros
### Response Body Macros
### Route Macros
- `#[route("path")]` - Register a route handler for the given path using the default server (Prerequisite: requires the #[hyperlane(server: Server)] macro)
### Helper Tips
- **Request related macros** (data extraction) use **`get`** operations - they retrieve/query data from the request
- **Response related macros** (data setting) use **`set`** operations - they assign/configure response data
- **Hook macros** For hook-related macros that support an `order` parameter, if `order` is not specified, the hook will have higher priority than hooks with a specified `order` (applies only to macros like `#[request_middleware]`, `#[response_middleware]`, `#[task_panic]`)
- **Multi-parameter support** Most data extraction macros support multiple parameters in a single call (e.g., `#[request_body(var1, var2)]`, `#[request_query("k1" => v1, "k2" => v2)]`). This reduces macro repetition and improves code readability.
### Best Practice Warning
- Request related macros are mostly query functions, while response related macros are mostly assignment functions.
- When using `prologue_hooks` or `epilogue_hooks` macros, it is not recommended to combine them with other macros (such as `#[get]`, `#[post]`, `#[http]`, etc.) on the same function. These macros should be placed in the hook functions themselves. If you are not clear about how macros are expanded, combining them may lead to problematic code behavior.
## Contact
# Path: hyperlane-macros/debug/src/main.rs
```rust
use hyperlane::*;
use hyperlane_macros::*;
use serde::{Deserialize, Serialize};
const STEP: &str = "step";
const TEST_ATTRIBUTE_KEY: &str = "test_attribute_key";
const CUSTOM_STATUS_CODE: i32 = 200;
const CUSTOM_REASON: &str = "Accepted";
const CUSTOM_HEADER_NAME: &str = "X-Custom-Header";
const CUSTOM_HEADER_VALUE: &str = "custom-value";
const RESPONSE_DATA: &str = "{\"status\": \"success\"}";
#[derive(Debug, Serialize, Deserialize, Clone)]
struct TestData {
    name: String,
    age: u32,
}
#[task_panic]
#[task_panic(1)]
#[task_panic("2")]
struct TakPanicHook;
impl ServerHook for TakPanicHook {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(
        task_panic_data_option(task_panic_data_option),
        task_panic_data(task_panic_data)
    )]
    #[epilogue_macros(
        response_version(HttpVersion::Http1_1),
        response_status_code(500),
        response_body(format!("{task_panic_data} {task_panic_data_option:?}")),
        send
    )]
    async fn handle(self, ctx: &Context) {}
}
#[request_error]
#[request_error(1)]
#[request_error("2")]
struct RequestErrorHook;
impl ServerHook for RequestErrorHook {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(
        request_error_data_option(request_error_data_option),
        request_error_data(request_error_data)
    )]
    #[epilogue_macros(
        response_version(HttpVersion::Http1_1),
        response_status_code(500),
        response_body(format!("{request_error_data} {request_error_data_option:?}")),
        send
    )]
    async fn handle(self, ctx: &Context) {}
}
#[request_middleware]
struct RequestMiddleware;
impl ServerHook for RequestMiddleware {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[epilogue_macros(
        response_version(HttpVersion::Http1_1),
        response_status_code(200),
        response_header(SERVER => HYPERLANE),
        response_header(CONNECTION => KEEP_ALIVE),
        response_header(CONTENT_TYPE => TEXT_PLAIN),
        response_header(ACCESS_CONTROL_ALLOW_ORIGIN => WILDCARD_ANY),
        response_header(STEP => "request_middleware"),
    )]
    async fn handle(self, ctx: &Context) {}
}
#[request_middleware(1)]
struct UpgradeHook;
impl ServerHook for UpgradeHook {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[epilogue_macros(
        ws,
        response_body(&vec![]),
        response_status_code(101),
        response_header(UPGRADE => WEBSOCKET),
        response_header(CONNECTION => UPGRADE),
        response_header(SEC_WEBSOCKET_ACCEPT => &WebSocketFrame::generate_accept_key(ctx.get_request_header_back(SEC_WEBSOCKET_KEY).await)),
        response_header(STEP => "upgrade_hook"),
        send
    )]
    async fn handle(self, ctx: &Context) {}
}
#[request_middleware(2)]
struct ConnectedHook;
impl ServerHook for ConnectedHook {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[response_status_code(200)]
    #[response_header(SERVER => HYPERLANE)]
    #[response_version(HttpVersion::Http1_1)]
    #[response_header(ACCESS_CONTROL_ALLOW_ORIGIN => WILDCARD_ANY)]
    #[response_header(STEP => "connected_hook")]
    async fn handle(self, ctx: &Context) {}
}
#[response_middleware]
struct ResponseMiddleware1;
impl ServerHook for ResponseMiddleware1 {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[response_header(STEP => "response_middleware_1")]
    async fn handle(self, ctx: &Context) {}
}
#[response_middleware(2)]
struct ResponseMiddleware2;
impl ServerHook for ResponseMiddleware2 {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(
        reject(ctx.get_request().await.is_ws()),
        response_header(STEP => "response_middleware_2")
    )]
    #[epilogue_macros(try_send, flush)]
    async fn handle(self, ctx: &Context) {}
}
#[response_middleware("3")]
struct ResponseMiddleware3;
impl ServerHook for ResponseMiddleware3 {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(
        ws,
        response_header(STEP => "response_middleware_3")
    )]
    #[epilogue_macros(try_send, flush)]
    async fn handle(self, ctx: &Context) {}
}
struct PrologueHooks;
impl ServerHook for PrologueHooks {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[get]
    #[http]
    async fn handle(self, _ctx: &Context) {}
}
struct EpilogueHooks;
impl ServerHook for EpilogueHooks {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[response_status_code(200)]
    async fn handle(self, ctx: &Context) {}
}
async fn prologue_hooks_fn(ctx: Context) {
    let hook = PrologueHooks::new(&ctx).await;
    hook.handle(&ctx).await;
}
async fn epilogue_hooks_fn(ctx: Context) {
    let hook = EpilogueHooks::new(&ctx).await;
    hook.handle(&ctx).await;
}
#[route("/response")]
struct Response;
impl ServerHook for Response {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[response_body(&RESPONSE_DATA)]
    #[response_reason_phrase(CUSTOM_REASON)]
    #[response_status_code(CUSTOM_STATUS_CODE)]
    #[response_header(CUSTOM_HEADER_NAME => CUSTOM_HEADER_VALUE)]
    async fn handle(self, ctx: &Context) {}
}
#[route("/connect")]
struct Connect;
impl ServerHook for Connect {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(connect, response_body("connect"))]
    async fn handle(self, ctx: &Context) {}
}
#[route("/delete")]
struct Delete;
impl ServerHook for Delete {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(delete, response_body("delete"))]
    async fn handle(self, ctx: &Context) {}
}
#[route("/head")]
struct Head;
impl ServerHook for Head {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(head, response_body("head"))]
    async fn handle(self, ctx: &Context) {}
}
#[route("/options")]
struct Options;
impl ServerHook for Options {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(options, response_body("options"))]
    async fn handle(self, ctx: &Context) {}
}
#[route("/patch")]
struct Patch;
impl ServerHook for Patch {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(patch, response_body("patch"))]
    async fn handle(self, ctx: &Context) {}
}
#[route("/put")]
struct Put;
impl ServerHook for Put {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(put, response_body("put"))]
    async fn handle(self, ctx: &Context) {}
}
#[route("/trace")]
struct Trace;
impl ServerHook for Trace {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(trace, response_body("trace"))]
    async fn handle(self, ctx: &Context) {}
}
#[route("/h2c")]
struct H2c;
impl ServerHook for H2c {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(h2c, response_body("h2c"))]
    async fn handle(self, ctx: &Context) {}
}
#[route("/http")]
struct HttpOnly;
impl ServerHook for HttpOnly {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(http, response_body("http"))]
    async fn handle(self, ctx: &Context) {}
}
#[route("/http0_9")]
struct Http09;
impl ServerHook for Http09 {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(http0_9, response_body("http0_9"))]
    async fn handle(self, ctx: &Context) {}
}
#[route("/http1_0")]
struct Http10;
impl ServerHook for Http10 {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(http1_0, response_body("http1_0"))]
    async fn handle(self, ctx: &Context) {}
}
#[route("/http1_1")]
struct Http11;
impl ServerHook for Http11 {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(http1_1, response_body("http1_1"))]
    async fn handle(self, ctx: &Context) {}
}
#[route("/http2")]
struct Http2;
impl ServerHook for Http2 {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(http2, response_body("http2"))]
    async fn handle(self, ctx: &Context) {}
}
#[route("/http3")]
struct Http3;
impl ServerHook for Http3 {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(http3, response_body("http3"))]
    async fn handle(self, ctx: &Context) {}
}
#[route("/tls")]
struct Tls;
impl ServerHook for Tls {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(tls, response_body("tls"))]
    async fn handle(self, ctx: &Context) {}
}
#[route("/http1_1_or_higher")]
struct Http11OrHigher;
impl ServerHook for Http11OrHigher {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(http1_1_or_higher, response_body("http1_1_or_higher"))]
    async fn handle(self, ctx: &Context) {}
}
#[route("/unknown_method")]
struct UnknownMethod;
impl ServerHook for UnknownMethod {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(
        clear_response_headers,
        filter(ctx.get_request().await.is_unknown_method()),
        response_body("unknown_method")
    )]
    async fn handle(self, ctx: &Context) {}
}
#[route("/get")]
struct Get;
impl ServerHook for Get {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(ws, get, response_body("get"))]
    async fn handle(self, ctx: &Context) {}
}
#[route("/post")]
struct Post;
impl ServerHook for Post {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(post, response_body("post"), try_send)]
    async fn handle(self, ctx: &Context) {}
}
#[route("/ws1")]
struct Websocket1;
impl ServerHook for Websocket1 {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[ws]
    #[ws_from_stream]
    async fn handle(self, ctx: &Context) {
        let body: RequestBody = ctx.get_request_body().await;
        let body_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(&body);
        ctx.send_body_list_with_data(&body_list).await;
    }
}
#[route("/ws2")]
struct Websocket2;
impl ServerHook for Websocket2 {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[ws]
    #[ws_from_stream(request)]
    async fn handle(self, ctx: &Context) {
        let body: &RequestBody = request.get_body();
        let body_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(body);
        ctx.send_body_list_with_data(&body_list).await;
    }
}
#[route("/ws3")]
struct Websocket3;
impl ServerHook for Websocket3 {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[ws]
    #[ws_from_stream(RequestConfig::default(), request)]
    async fn handle(self, ctx: &Context) {
        let body: &RequestBody = request.get_body();
        let body_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(body);
        ctx.send_body_list_with_data(&body_list).await;
    }
}
#[route("/ws4")]
struct Websocket4;
impl ServerHook for Websocket4 {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[ws]
    #[ws_from_stream(request, RequestConfig::default())]
    async fn handle(self, ctx: &Context) {
        let body: &RequestBody = request.get_body();
        let body_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(body);
        ctx.send_body_list_with_data(&body_list).await;
    }
}
#[route("/ws5")]
struct Websocket5;
impl ServerHook for Websocket5 {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[ws]
    #[ws_from_stream(RequestConfig::default())]
    async fn handle(self, ctx: &Context) {
        let body: RequestBody = ctx.get_request_body().await;
        let body_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(&body);
        ctx.send_body_list_with_data(&body_list).await;
    }
}
#[route("/hook")]
struct Hook;
impl ServerHook for Hook {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_hooks(prologue_hooks_fn)]
    #[epilogue_hooks(epilogue_hooks_fn)]
    #[response_body("Testing hook macro")]
    async fn handle(self, ctx: &Context) {}
}
#[route("/get_post")]
struct GetPost;
impl ServerHook for GetPost {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[closed]
    #[prologue_macros(
        http,
        methods(get, post),
        response_body("get_post"),
        response_status_code(200),
        response_reason_phrase("OK")
    )]
    async fn handle(self, ctx: &Context) {}
}
#[route("/attributes")]
struct Attributes;
impl ServerHook for Attributes {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[response_body(&format!("request attributes: {request_attributes:?}"))]
    #[attributes(request_attributes)]
    async fn handle(self, ctx: &Context) {}
}
#[route("/route_params/:test")]
struct RouteParams;
impl ServerHook for RouteParams {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[response_body(&format!("request route params: {request_route_params:?}"))]
    #[route_params(request_route_params)]
    async fn handle(self, ctx: &Context) {}
}
#[route("/route_param_option/:test")]
struct RouteParamOption;
impl ServerHook for RouteParamOption {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[response_body(&format!("route param: {request_route_param_option1:?} {request_route_param_option2:?} {request_route_param_option3:?}"))]
    #[route_param_option("test1" => request_route_param_option1)]
    #[route_param_option("test2" => request_route_param_option2, "test3" => request_route_param_option3)]
    async fn handle(self, ctx: &Context) {}
}
#[route("/route_param/:test")]
struct RouteParam;
impl ServerHook for RouteParam {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[response_body(&format!("route param: {request_route_param1} {request_route_param2} {request_route_param3}"))]
    #[route_param("test1" => request_route_param1)]
    #[route_param("test2" => request_route_param2, "test3" => request_route_param3)]
    async fn handle(self, ctx: &Context) {}
}
#[route("/host")]
struct Host;
impl ServerHook for Host {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[host("localhost")]
    #[epilogue_macros(
        response_body("host string literal: localhost"),
        send,
        http_from_stream
    )]
    #[prologue_macros(response_body("host string literal: localhost"), send)]
    async fn handle(self, ctx: &Context) {}
}
#[route("/request_query_option")]
struct RequestQueryOption;
impl ServerHook for RequestQueryOption {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[epilogue_macros(
        request_query_option("test" => request_query_option),
        response_body(&format!("request query: {request_query_option:?}")),
        send,
        http_from_stream(RequestConfig::default())
    )]
    #[prologue_macros(
        request_query_option("test" => request_query_option),
        response_body(&format!("request query: {request_query_option:?}")),
        send
    )]
    async fn handle(self, ctx: &Context) {}
}
#[route("/request_query")]
struct RequestQuery;
impl ServerHook for RequestQuery {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[epilogue_macros(
        request_query("test" => request_query),
        response_body(&format!("request query: {request_query}")),
        send,
        http_from_stream(RequestConfig::default())
    )]
    #[prologue_macros(
        request_query("test" => request_query),
        response_body(&format!("request query: {request_query}")),
        send
    )]
    async fn handle(self, ctx: &Context) {}
}
#[route("/request_header_option")]
struct RequestHeaderOption;
impl ServerHook for RequestHeaderOption {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[epilogue_macros(
        request_header_option(HOST => request_header_option),
        response_body(&format!("request header: {request_header_option:?}")),
        send,
        http_from_stream(_request)
    )]
    #[prologue_macros(
        request_header_option(HOST => request_header_option),
        response_body(&format!("request header: {request_header_option:?}")),
        send
    )]
    async fn handle(self, ctx: &Context) {}
}
#[route("/request_header")]
struct RequestHeader;
impl ServerHook for RequestHeader {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[epilogue_macros(
        request_header(HOST => request_header),
        response_body(&format!("request header: {request_header}")),
        send,
        http_from_stream(_request)
    )]
    #[prologue_macros(
        request_header(HOST => request_header),
        response_body(&format!("request header: {request_header}")),
        send
    )]
    async fn handle(self, ctx: &Context) {}
}
#[route("/request_querys")]
struct RequestQuerys;
impl ServerHook for RequestQuerys {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[epilogue_macros(
        request_querys(request_querys),
        response_body(&format!("request querys: {request_querys:?}")),
        send,
        http_from_stream(RequestConfig::default(), _request)
    )]
    #[prologue_macros(
        request_querys(request_querys),
        response_body(&format!("request querys: {request_querys:?}")),
        send
    )]
    async fn handle(self, ctx: &Context) {}
}
#[route("/request_headers")]
struct RequestHeaders;
impl ServerHook for RequestHeaders {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[epilogue_macros(
        request_headers(request_headers),
        response_body(&format!("request headers: {request_headers:?}")),
        send,
        http_from_stream(_request, RequestConfig::default())
    )]
    #[prologue_macros(
        request_headers(request_headers),
        response_body(&format!("request headers: {request_headers:?}")),
        send
    )]
    async fn handle(self, ctx: &Context) {}
}
#[route("/request_body")]
struct RequestBodyRoute;
impl ServerHook for RequestBodyRoute {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[response_body(&format!("raw body: {raw_body:?}"))]
    #[request_body(raw_body)]
    async fn handle(self, ctx: &Context) {}
}
#[route("/reject_host")]
struct RejectHost;
impl ServerHook for RejectHost {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(
        reject_host("filter.localhost"),
        response_body("host filter string literal")
    )]
    async fn handle(self, ctx: &Context) {}
}
#[route("/attribute_option")]
struct AttributeOption;
impl ServerHook for AttributeOption {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[response_body(&format!("request attribute: {request_attribute_option:?}"))]
    #[attribute_option(TEST_ATTRIBUTE_KEY => request_attribute_option: TestData)]
    async fn handle(self, ctx: &Context) {}
}
#[route("/attribute")]
struct Attribute;
impl ServerHook for Attribute {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[response_body(&format!("request attribute: {request_attribute:?}"))]
    #[attribute(TEST_ATTRIBUTE_KEY => request_attribute: TestData)]
    async fn handle(self, ctx: &Context) {}
}
#[route("/request_body_json_result")]
struct RequestBodyJsonResult;
impl ServerHook for RequestBodyJsonResult {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[response_body(&format!("request data: {request_data_result:?}"))]
    #[request_body_json_result(request_data_result: TestData)]
    async fn handle(self, ctx: &Context) {}
}
#[route("/request_body_json")]
struct RequestBodyJson;
impl ServerHook for RequestBodyJson {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[response_body(&format!("request data: {request_data_result:?}"))]
    #[request_body_json(request_data_result: TestData)]
    async fn handle(self, ctx: &Context) {}
}
#[route("/referer")]
struct Referer;
impl ServerHook for Referer {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(
        referer("http://localhost"),
        response_body("referer string literal: http://localhost")
    )]
    async fn handle(self, ctx: &Context) {}
}
#[route("/reject_referer")]
struct RejectReferer;
impl ServerHook for RejectReferer {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(
        reject_referer("http://localhost"),
        response_body("referer filter string literal")
    )]
    async fn handle(self, ctx: &Context) {}
}
#[route("/cookies")]
struct Cookies;
impl ServerHook for Cookies {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[response_body(&format!("All cookies: {cookie_value:?}"))]
    #[request_cookies(cookie_value)]
    async fn handle(self, ctx: &Context) {}
}
#[route("/request_cookie_option")]
struct CookieOption;
impl ServerHook for CookieOption {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[response_body(&format!("Session cookie: {session_cookie1_option:?}, {session_cookie2_option:?}"))]
    #[request_cookie_option("test1" => session_cookie1_option, "test2" => session_cookie2_option)]
    async fn handle(self, ctx: &Context) {}
}
#[route("/request_cookie")]
struct Cookie;
impl ServerHook for Cookie {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[response_body(&format!("Session cookie: {session_cookie1}, {session_cookie2}"))]
    #[request_cookie("test1" => session_cookie1, "test2" => session_cookie2)]
    async fn handle(self, ctx: &Context) {}
}
#[route("/request_version")]
struct RequestVersionTest;
impl ServerHook for RequestVersionTest {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[response_body(&format!("HTTP Version: {http_version}"))]
    #[request_version(http_version)]
    async fn handle(self, ctx: &Context) {}
}
#[route("/request_path")]
struct RequestPathTest;
impl ServerHook for RequestPathTest {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[response_body(&format!("Request Path: {request_path}"))]
    #[request_path(request_path)]
    async fn handle(self, ctx: &Context) {}
}
#[route("/response_header")]
struct ResponseHeaderTest;
impl ServerHook for ResponseHeaderTest {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[response_body("Testing header set and replace operations")]
    #[response_header("X-Add-Header", "add-value")]
    #[response_header("X-Set-Header" => "set-value")]
    async fn handle(self, ctx: &Context) {}
}
#[route("/literals")]
struct Literals;
impl ServerHook for Literals {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[response_status_code(201)]
    #[response_header(CONTENT_TYPE => APPLICATION_JSON)]
    #[response_body("{\"message\": \"Resource created\"}")]
    #[response_reason_phrase(HttpStatus::Created.to_string())]
    async fn handle(self, ctx: &Context) {}
}
#[route("/inject/response_body")]
struct InjectResponseBody;
impl ServerHook for InjectResponseBody {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &Context) {
        self.response_body_with_ref_self(ctx).await;
    }
}
impl InjectResponseBody {
    #[response_body("response body with ref self")]
    async fn response_body_with_ref_self(&self, ctx: &Context) {}
}
#[route("/inject/post_method")]
struct InjectPostMethod;
impl ServerHook for InjectPostMethod {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &Context) {
        self.post_method_with_ref_self(ctx).await;
    }
}
impl InjectPostMethod {
    #[prologue_macros(post, response_body("post method with ref self"))]
    async fn post_method_with_ref_self(&self, ctx: &Context) {}
}
#[route("/inject/send_flush")]
struct InjectSendFlush;
impl ServerHook for InjectSendFlush {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &Context) {
        self.send_and_flush_with_ref_self(ctx).await;
    }
}
impl InjectSendFlush {
    #[epilogue_macros(try_send, flush)]
    async fn send_and_flush_with_ref_self(&self, ctx: &Context) {}
}
#[route("/inject/request_body")]
struct InjectRequestBody;
impl ServerHook for InjectRequestBody {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &Context) {
        self.extract_request_body_with_ref_self(ctx).await;
    }
}
impl InjectRequestBody {
    #[request_body(_raw_body)]
    async fn extract_request_body_with_ref_self(&self, _ctx: &Context) {}
}
#[route("/inject/multiple_methods")]
struct InjectMultipleMethods;
impl ServerHook for InjectMultipleMethods {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &Context) {
        self.multiple_methods_with_ref_self(ctx).await;
    }
}
impl InjectMultipleMethods {
    #[methods(get, post)]
    async fn multiple_methods_with_ref_self(&self, ctx: &Context) {}
}
#[route("/inject/http_stream")]
struct InjectHttpStream;
impl ServerHook for InjectHttpStream {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &Context) {
        self.http_stream_handler_with_ref_self(ctx).await;
    }
}
impl InjectHttpStream {
    #[http_from_stream(RequestConfig::default(), _request)]
    async fn http_stream_handler_with_ref_self(&self, _ctx: &Context) {}
}
#[route("/inject/ws_stream")]
struct InjectWsStream;
impl ServerHook for InjectWsStream {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &Context) {
        self.websocket_stream_handler_with_ref_self(ctx).await;
    }
}
impl InjectWsStream {
    #[ws_from_stream(_request)]
    async fn websocket_stream_handler_with_ref_self(&self, _ctx: &Context) {}
}
#[route("/inject/complex_post")]
struct InjectComplexPost;
impl ServerHook for InjectComplexPost {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &Context) {
        self.complex_post_handler_with_ref_self(ctx).await;
    }
}
impl InjectComplexPost {
    #[prologue_macros(
        post,
        http,
        request_body(raw_body),
        response_status_code(201),
        response_header(CONTENT_TYPE => APPLICATION_JSON),
        response_body(&format!("Received: {raw_body:?}"))
    )]
    #[epilogue_macros(try_send, flush)]
    async fn complex_post_handler_with_ref_self(&self, ctx: &Context) {}
}
impl InjectComplexPost {
    #[post]
    async fn test_with_bool_param(_a: bool, ctx: &Context) {}
    #[get]
    async fn test_with_multiple_params(_a: bool, ctx: &Context, _b: i32) {}
}
#[route("/test/send")]
struct TestSend;
impl ServerHook for TestSend {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(
        get,
        response_status_code(200),
        response_header(CONTENT_TYPE => TEXT_PLAIN),
        response_body("Test send operation")
    )]
    #[epilogue_macros(send)]
    async fn handle(self, ctx: &Context) {}
}
#[route("/test/send_body")]
struct TestSendBody;
impl ServerHook for TestSendBody {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(
        get,
        response_status_code(200),
        response_header(CONTENT_TYPE => TEXT_PLAIN),
        response_body("Test send body operation")
    )]
    #[epilogue_macros(send_body)]
    async fn handle(self, ctx: &Context) {}
}
#[route("/test/send_body_with_data")]
struct TestSendBodyWithData;
impl ServerHook for TestSendBodyWithData {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(
        get,
        response_status_code(200),
        response_header(CONTENT_TYPE => TEXT_PLAIN)
    )]
    #[epilogue_macros(send_body_with_data("Custom data from send_body_with_data"))]
    async fn handle(self, ctx: &Context) {}
}
#[route("/test/try_send")]
struct TestTrySend;
impl ServerHook for TestTrySend {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(
        get,
        response_status_code(200),
        response_header(CONTENT_TYPE => TEXT_PLAIN),
        response_body("Test try send operation")
    )]
    #[epilogue_macros(try_send)]
    async fn handle(self, ctx: &Context) {}
}
#[route("/test/try_send_body")]
struct TestTrySendBody;
impl ServerHook for TestTrySendBody {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(
        get,
        response_status_code(200),
        response_header(CONTENT_TYPE => TEXT_PLAIN),
        response_body("Test try send body operation")
    )]
    #[epilogue_macros(try_send_body)]
    async fn handle(self, ctx: &Context) {}
}
#[route("/test/try_send_body_with_data")]
struct TestTrySendBodyWithData;
impl ServerHook for TestTrySendBodyWithData {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(
        get,
        response_status_code(200),
        response_header(CONTENT_TYPE => TEXT_PLAIN)
    )]
    #[epilogue_macros(try_send_body_with_data("Custom data from try_send_body_with_data"))]
    async fn handle(self, ctx: &Context) {}
}
#[route("/test/try_flush")]
struct TestTryFlush;
impl ServerHook for TestTryFlush {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(
        get,
        response_status_code(200),
        response_header(CONTENT_TYPE => TEXT_PLAIN),
        response_body("Test try flush operation")
    )]
    #[epilogue_macros(try_flush)]
    async fn handle(self, ctx: &Context) {}
}
#[route("/test/aborted")]
struct TestAborted;
impl ServerHook for TestAborted {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(
        get,
        response_status_code(200),
        response_header(CONTENT_TYPE => TEXT_PLAIN),
        response_body("Test aborted operation")
    )]
    #[epilogue_macros(aborted)]
    async fn handle(self, ctx: &Context) {}
}
#[route("/test/closed")]
struct TestClosed;
impl ServerHook for TestClosed {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(
        get,
        response_status_code(200),
        response_header(CONTENT_TYPE => TEXT_PLAIN),
        response_body("Test closed operation")
    )]
    #[epilogue_macros(closed)]
    async fn handle(self, ctx: &Context) {}
}
#[route("/test/flush")]
struct TestFlush;
impl ServerHook for TestFlush {
    async fn new(_ctx: &Context) -> Self {
        Self
    }
    #[prologue_macros(
        get,
        response_status_code(200),
        response_header(CONTENT_TYPE => TEXT_PLAIN),
        response_body("Test flush operation")
    )]
    #[epilogue_macros(flush)]
    async fn handle(self, ctx: &Context) {}
}
#[response_body("standalone response body")]
async fn standalone_response_body_handler(ctx: &Context) {}
#[prologue_macros(get, response_body("standalone get handler"))]
async fn standalone_get_handler(ctx: &Context) {}
#[epilogue_macros(try_send, flush)]
async fn standalone_send_and_flush_handler(ctx: &Context) {}
#[request_body(_raw_body)]
async fn standalone_request_body_extractor(ctx: &Context) {}
#[methods(get, post)]
async fn standalone_multiple_methods_handler(ctx: &Context) {}
#[http_from_stream]
async fn standalone_http_stream_handler(ctx: &Context) {}
#[ws_from_stream]
async fn standalone_websocket_stream_handler(ctx: &Context) {}
#[aborted]
async fn standalone_aborted_handler(ctx: &Context) {}
#[closed]
async fn standalone_closed_handler(ctx: &Context) {}
#[flush]
async fn standalone_flush_handler(ctx: &Context) {}
#[try_flush]
async fn standalone_try_flush_handler(ctx: &Context) {}
#[ws]
async fn standalone_ws_handler(ctx: &Context) {}
#[prologue_macros(
    get,
    http,
    response_status_code(200),
    response_header(CONTENT_TYPE => TEXT_PLAIN),
    response_body("standalone complex handler")
)]
#[epilogue_macros(try_send, flush)]
async fn standalone_complex_get_handler(ctx: &Context) {}
#[get]
async fn standalone_get_handler_with_param(_a: bool, ctx: &Context) {}
#[request_body(body1, body2, body3)]
async fn test_multi_request_body(ctx: &Context) {
    println!("body1: {:?}, body2: {:?}, body3: {:?}", body1, body2, body3);
}
#[route("/test_multi_request_body_json")]
#[derive(Debug, serde::Deserialize)]
struct User {
    name: String,
}
impl ServerHook for User {
    async fn new(_ctx: &Context) -> Self {
        Self {
            name: String::from("test"),
        }
    }
    #[prologue_macros(
        request_body_json(user1: User, user2: User),
        response_body(format!(
            "user1: {:?}, user2: {:?}",
            user1.name,
            user2.name
        )),
        try_send
    )]
    async fn handle(self, ctx: &Context) {}
}
#[attribute("key1" => attr1: String, "key2" => attr2: i32)]
async fn test_multi_attribute(ctx: &Context) {
    println!("attr1: {:?}, attr2: {:?}", attr1, attr2);
}
#[attributes(attrs1, attrs2)]
async fn test_multi_attributes(ctx: &Context) {
    println!("attrs1: {:?}, attrs2: {:?}", attrs1, attrs2);
}
#[route_params(params1, params2)]
async fn test_multi_route_params(ctx: &Context) {
    println!("params1: {:?}, params2: {:?}", params1, params2);
}
#[request_querys(querys1, querys2)]
async fn test_multi_request_querys(ctx: &Context) {
    println!("querys1: {:?}, querys2: {:?}", querys1, querys2);
}
#[request_headers(headers1, headers2)]
async fn test_multi_request_headers(ctx: &Context) {
    println!("headers1: {:?}, headers2: {:?}", headers1, headers2);
}
#[request_cookies(cookies1, cookies2)]
async fn test_multi_request_cookies(ctx: &Context) {
    println!("cookies1: {:?}, cookies2: {:?}", cookies1, cookies2);
}
#[request_version(version1, version2)]
async fn test_multi_request_version(ctx: &Context) {
    println!("version1: {:?}, version2: {:?}", version1, version2);
}
#[request_path(path1, path2)]
async fn test_multi_request_path(ctx: &Context) {
    println!("path1: {:?}, path2: {:?}", path1, path2);
}
#[host("localhost", "127.0.0.1")]
async fn test_multi_host(ctx: &Context) {
    println!("Host check passed");
}
#[reject_host("localhost", "127.0.0.1")]
async fn test_multi_reject_host(ctx: &Context) {
    println!("Reject host check passed");
}
#[referer("http://localhost", "http://127.0.0.1")]
async fn test_multi_referer(ctx: &Context) {
    println!("Referer check passed");
}
#[reject_referer("http://localhost", "http://127.0.0.1")]
async fn test_multi_reject_referer(ctx: &Context) {
    println!("Reject referer check passed");
}
#[hyperlane(server1: Server, server2: Server)]
async fn test_multi_hyperlane() {
    println!("server1 and server2 initialized");
}
#[response_status_code(200)]
async fn standalone_response_status_code_handler(_ctx: &Context) {}
#[response_reason_phrase("Custom Reason")]
async fn standalone_response_reason_phrase_handler(_ctx: &Context) {}
#[response_header(CONTENT_TYPE => APPLICATION_JSON)]
async fn standalone_response_header_handler(_ctx: &Context) {}
#[response_header("X-Custom-Header", "custom-value")]
async fn standalone_response_header_with_comma_handler(_ctx: &Context) {}
#[response_version(HttpVersion::Http1_1)]
async fn standalone_response_version_handler(_ctx: &Context) {}
#[connect]
async fn standalone_connect_handler(_ctx: &Context) {}
#[delete]
async fn standalone_delete_handler(_ctx: &Context) {}
#[head]
async fn standalone_head_handler(_ctx: &Context) {}
#[options]
async fn standalone_options_handler(_ctx: &Context) {}
#[patch]
async fn standalone_patch_handler(_ctx: &Context) {}
#[put]
async fn standalone_put_handler(_ctx: &Context) {}
#[h2c]
async fn standalone_h2c_handler(_ctx: &Context) {}
#[http0_9]
async fn standalone_http0_9_handler(_ctx: &Context) {}
#[http1_0]
async fn standalone_http1_0_handler(_ctx: &Context) {}
#[http1_1]
async fn standalone_http1_1_handler(_ctx: &Context) {}
#[http1_1_or_higher]
async fn standalone_http1_1_or_higher_handler(_ctx: &Context) {}
#[http3]
async fn standalone_http3_handler(_ctx: &Context) {}
#[tls]
async fn standalone_tls_handler(_ctx: &Context) {}
#[methods(get, post, put)]
async fn standalone_methods_multiple_handler(_ctx: &Context) {}
#[filter(_ctx.get_request().await.is_get())]
async fn standalone_filter_handler(_ctx: &Context) {}
#[reject(_ctx.get_request().await.is_post())]
async fn standalone_reject_handler(_ctx: &Context) {}
#[reject_host("example.com")]
async fn standalone_reject_host_handler(_ctx: &Context) {}
#[referer("https://example.com")]
async fn standalone_referer_handler(_ctx: &Context) {}
#[reject_referer("https://malicious.com")]
async fn standalone_reject_referer_handler(_ctx: &Context) {}
#[request_query("param" => _value)]
async fn standalone_request_query_handler(_ctx: &Context) {}
#[request_query_option("optional_param" => _optional_value)]
async fn standalone_request_query_option_handler(_ctx: &Context) {}
#[request_header(HOST => _host_value)]
async fn standalone_request_header_handler(_ctx: &Context) {}
#[request_header_option(USER_AGENT => _user_agent)]
async fn standalone_request_header_option_handler(_ctx: &Context) {}
#[request_querys(_querys)]
async fn standalone_request_querys_handler(_ctx: &Context) {}
#[request_headers(_headers)]
async fn standalone_request_headers_handler(_ctx: &Context) {}
#[request_cookies(_cookies)]
async fn standalone_request_cookies_handler(_ctx: &Context) {}
#[request_cookie("session" => _session_cookie)]
async fn standalone_request_cookie_handler(_ctx: &Context) {}
#[request_cookie_option("optional_cookie" => _optional_cookie)]
async fn standalone_request_cookie_option_handler(_ctx: &Context) {}
#[request_version(_version)]
async fn standalone_request_version_handler(_ctx: &Context) {}
#[request_path(_path)]
async fn standalone_request_path_handler(_ctx: &Context) {}
#[attribute("key" => _attr_value: String)]
async fn standalone_attribute_handler(_ctx: &Context) {}
#[attribute_option("optional_key" => _optional_attr: String)]
async fn standalone_attribute_option_handler(_ctx: &Context) {}
#[attributes(_attrs)]
async fn standalone_attributes_handler(_ctx: &Context) {}
#[route_params(_params)]
async fn standalone_route_params_handler(_ctx: &Context) {}
#[route_param("param" => _param_value)]
async fn standalone_route_param_handler(_ctx: &Context) {}
#[route_param_option("optional_param" => _optional_param_value)]
async fn standalone_route_param_option_handler(_ctx: &Context) {}
#[request_body_json(_user: TestData)]
async fn standalone_request_body_json_handler(_ctx: &Context) {}
#[request_body_json_result(_user_result: TestData)]
async fn standalone_request_body_json_result_handler(_ctx: &Context) {}
#[http_from_stream(RequestConfig::default())]
async fn standalone_http_from_stream_with_config_handler(_ctx: &Context) {}
#[ws_from_stream(RequestConfig::default())]
async fn standalone_ws_from_stream_with_config_handler(_ctx: &Context) {}
#[http_from_stream(_request)]
async fn standalone_http_from_stream_with_request_handler(_ctx: &Context) {}
#[ws_from_stream(_request)]
async fn standalone_ws_from_stream_with_request_handler(_ctx: &Context) {}
#[http_from_stream(RequestConfig::default(), _request)]
async fn standalone_http_from_stream_full_handler(_ctx: &Context) {}
#[ws_from_stream(RequestConfig::default(), _request)]
async fn standalone_ws_from_stream_full_handler(_ctx: &Context) {}
#[send]
async fn standalone_send_handler_2(_ctx: &Context) {}
#[send_body]
async fn standalone_send_body_handler_2(_ctx: &Context) {}
#[send_body_with_data("Custom send body data")]
async fn standalone_send_body_with_data_handler_2(_ctx: &Context) {}
#[try_send]
async fn standalone_try_send_handler_2(_ctx: &Context) {}
#[try_send_body]
async fn standalone_try_send_body_handler_2(_ctx: &Context) {}
#[try_send_body_with_data("Custom try send body data")]
async fn standalone_try_send_body_with_data_handler_2(_ctx: &Context) {}
#[flush]
async fn standalone_flush_handler_2(_ctx: &Context) {}
#[try_flush]
async fn standalone_try_flush_handler_2(_ctx: &Context) {}
#[aborted]
async fn standalone_aborted_handler_2(_ctx: &Context) {}
#[closed]
async fn standalone_closed_handler_2(_ctx: &Context) {}
#[clear_response_headers]
async fn standalone_clear_response_headers_handler(_ctx: &Context) {}
#[prologue_macros(
    get,
    response_status_code(200),
    response_header(CONTENT_TYPE => TEXT_PLAIN),
    response_body("prologue macros test")
)]
async fn standalone_prologue_macros_complex_handler(_ctx: &Context) {}
#[epilogue_macros(
    response_status_code(201),
    response_header(CONTENT_TYPE => APPLICATION_JSON),
    response_body("epilogue macros test"),
    try_send,
    flush
)]
async fn standalone_epilogue_macros_complex_handler(_ctx: &Context) {}
#[prologue_hooks(prologue_hooks_fn)]
async fn standalone_prologue_hooks_handler(_ctx: &Context) {}
#[epilogue_hooks(epilogue_hooks_fn)]
async fn standalone_epilogue_hooks_handler(_ctx: &Context) {}
#[hyperlane(server: Server)]
#[hyperlane(config: ServerConfig)]
#[tokio::main]
async fn main() {
    config.disable_nodelay().await;
    server.config(config).await;
    let server_control_hook_1: ServerControlHook = server.run().await.unwrap_or_default();
    let server_control_hook_2: ServerControlHook = server_control_hook_1.clone();
    tokio::spawn(async move {
        tokio::time::sleep(std::time::Duration::from_secs(60)).await;
        server_control_hook_2.shutdown().await;
    });
    server_control_hook_1.wait().await;
}
```
# Path: hyperlane-macros/src/lib.rs
```rust
mod aborted;
mod closed;
mod common;
mod filter;
mod flush;
mod from_stream;
mod hook;
mod host;
mod http;
mod hyperlane;
mod inject;
mod protocol;
mod referer;
mod reject;
mod request;
mod request_middleware;
mod response;
mod response_middleware;
mod route;
mod send;
mod stream;
pub(crate) use aborted::*;
pub(crate) use closed::*;
pub(crate) use common::*;
pub(crate) use filter::*;
pub(crate) use flush::*;
pub(crate) use from_stream::*;
pub(crate) use hook::*;
pub(crate) use host::*;
pub(crate) use http::*;
pub(crate) use hyperlane::*;
pub(crate) use inject::*;
pub(crate) use protocol::*;
pub(crate) use referer::*;
pub(crate) use reject::*;
pub(crate) use request::*;
pub(crate) use request_middleware::*;
pub(crate) use response::*;
pub(crate) use response_middleware::*;
pub(crate) use route::*;
pub(crate) use send::*;
pub(crate) use stream::*;
pub(crate) use ::hyperlane::inventory;
pub(crate) use proc_macro::TokenStream;
pub(crate) use proc_macro2::TokenStream as TokenStream2;
pub(crate) use quote::quote;
pub(crate) use syn::{
    Ident, Token,
    parse::{Parse, ParseStream, Parser, Result},
    punctuated::Punctuated,
    token::Comma,
    *,
};
inventory::collect!(InjectableMacro);
#[proc_macro_attribute]
pub fn ws_from_stream(attr: TokenStream, item: TokenStream) -> TokenStream {
    ws_from_stream_macro(attr, item)
}
#[proc_macro_attribute]
pub fn http_from_stream(attr: TokenStream, item: TokenStream) -> TokenStream {
    http_from_stream_macro(attr, item)
}
#[proc_macro_attribute]
pub fn get(_attr: TokenStream, item: TokenStream) -> TokenStream {
    get_handler(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn post(_attr: TokenStream, item: TokenStream) -> TokenStream {
    post_handler(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn put(_attr: TokenStream, item: TokenStream) -> TokenStream {
    put_handler(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn delete(_attr: TokenStream, item: TokenStream) -> TokenStream {
    delete_handler(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn patch(_attr: TokenStream, item: TokenStream) -> TokenStream {
    patch_handler(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn head(_attr: TokenStream, item: TokenStream) -> TokenStream {
    head_handler(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn options(_attr: TokenStream, item: TokenStream) -> TokenStream {
    options_handler(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn connect(_attr: TokenStream, item: TokenStream) -> TokenStream {
    connect_handler(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn trace(_attr: TokenStream, item: TokenStream) -> TokenStream {
    trace_handler(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn methods(attr: TokenStream, item: TokenStream) -> TokenStream {
    methods_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn ws(_attr: TokenStream, item: TokenStream) -> TokenStream {
    ws_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn http(_attr: TokenStream, item: TokenStream) -> TokenStream {
    http_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn response_status_code(attr: TokenStream, item: TokenStream) -> TokenStream {
    response_status_code_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn response_reason_phrase(attr: TokenStream, item: TokenStream) -> TokenStream {
    response_reason_phrase_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn response_header(attr: TokenStream, item: TokenStream) -> TokenStream {
    response_header_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn response_body(attr: TokenStream, item: TokenStream) -> TokenStream {
    response_body_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn clear_response_headers(_attr: TokenStream, item: TokenStream) -> TokenStream {
    clear_response_headers_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn response_version(attr: TokenStream, item: TokenStream) -> TokenStream {
    response_version_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn aborted(_attr: TokenStream, item: TokenStream) -> TokenStream {
    aborted_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn closed(_attr: TokenStream, item: TokenStream) -> TokenStream {
    closed_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn h2c(_attr: TokenStream, item: TokenStream) -> TokenStream {
    h2c_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn http0_9(_attr: TokenStream, item: TokenStream) -> TokenStream {
    http0_9_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn http1_0(_attr: TokenStream, item: TokenStream) -> TokenStream {
    http1_0_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn http1_1(_attr: TokenStream, item: TokenStream) -> TokenStream {
    http1_1_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn http1_1_or_higher(_attr: TokenStream, item: TokenStream) -> TokenStream {
    http1_1_or_higher_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn http2(_attr: TokenStream, item: TokenStream) -> TokenStream {
    http2_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn http3(_attr: TokenStream, item: TokenStream) -> TokenStream {
    http3_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn tls(_attr: TokenStream, item: TokenStream) -> TokenStream {
    tls_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn filter(attr: TokenStream, item: TokenStream) -> TokenStream {
    filter_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn reject(attr: TokenStream, item: TokenStream) -> TokenStream {
    reject_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn host(attr: TokenStream, item: TokenStream) -> TokenStream {
    host_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn reject_host(attr: TokenStream, item: TokenStream) -> TokenStream {
    reject_host_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn referer(attr: TokenStream, item: TokenStream) -> TokenStream {
    referer_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn reject_referer(attr: TokenStream, item: TokenStream) -> TokenStream {
    reject_referer_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn prologue_hooks(attr: TokenStream, item: TokenStream) -> TokenStream {
    prologue_hooks_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn epilogue_hooks(attr: TokenStream, item: TokenStream) -> TokenStream {
    epilogue_hooks_macro(attr, item, Position::Epilogue)
}
#[proc_macro_attribute]
pub fn request_body(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_body_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn request_body_json_result(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_body_json_result_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn request_body_json(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_body_json_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn attribute_option(attr: TokenStream, item: TokenStream) -> TokenStream {
    attribute_option_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn attribute(attr: TokenStream, item: TokenStream) -> TokenStream {
    attribute_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn attributes(attr: TokenStream, item: TokenStream) -> TokenStream {
    attributes_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn task_panic_data_option(attr: TokenStream, item: TokenStream) -> TokenStream {
    task_panic_data_option_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn task_panic_data(attr: TokenStream, item: TokenStream) -> TokenStream {
    task_panic_data_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn request_error_data_option(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_error_data_option_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn request_error_data(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_error_data_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn route_param_option(attr: TokenStream, item: TokenStream) -> TokenStream {
    route_param_option_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn route_param(attr: TokenStream, item: TokenStream) -> TokenStream {
    route_param_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn route_params(attr: TokenStream, item: TokenStream) -> TokenStream {
    route_params_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn request_query_option(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_query_option_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn request_query(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_query_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn request_querys(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_querys_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn request_header_option(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_header_option_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn request_header(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_header_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn request_headers(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_headers_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn request_cookie_option(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_cookie_option_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn request_cookie(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_cookie_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn request_cookies(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_cookies_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn request_version(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_version_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn request_path(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_path_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn hyperlane(attr: TokenStream, item: TokenStream) -> TokenStream {
    hyperlane_macro(attr, item)
}
#[proc_macro_attribute]
pub fn route(attr: TokenStream, item: TokenStream) -> TokenStream {
    route_macro(attr, item)
}
#[proc_macro_attribute]
pub fn request_middleware(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_middleware_macro(attr, item)
}
#[proc_macro_attribute]
pub fn response_middleware(attr: TokenStream, item: TokenStream) -> TokenStream {
    response_middleware_macro(attr, item)
}
#[proc_macro_attribute]
pub fn task_panic(attr: TokenStream, item: TokenStream) -> TokenStream {
    task_panic_macro(attr, item)
}
#[proc_macro_attribute]
pub fn request_error(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_error_macro(attr, item)
}
#[proc_macro_attribute]
pub fn prologue_macros(attr: TokenStream, item: TokenStream) -> TokenStream {
    prologue_macros_macro(attr, item)
}
#[proc_macro_attribute]
pub fn epilogue_macros(attr: TokenStream, item: TokenStream) -> TokenStream {
    epilogue_macros_macro(attr, item)
}
#[proc_macro_attribute]
pub fn try_send(_attr: TokenStream, item: TokenStream) -> TokenStream {
    try_send_macro(item, Position::Epilogue)
}
#[proc_macro_attribute]
pub fn send(_attr: TokenStream, item: TokenStream) -> TokenStream {
    send_macro(item, Position::Epilogue)
}
#[proc_macro_attribute]
pub fn try_send_body(_attr: TokenStream, item: TokenStream) -> TokenStream {
    try_send_body_macro(item, Position::Epilogue)
}
#[proc_macro_attribute]
pub fn send_body(_attr: TokenStream, item: TokenStream) -> TokenStream {
    send_body_macro(item, Position::Epilogue)
}
#[proc_macro_attribute]
pub fn try_send_body_with_data(attr: TokenStream, item: TokenStream) -> TokenStream {
    try_send_body_with_data_macro(attr, item, Position::Epilogue)
}
#[proc_macro_attribute]
pub fn send_body_with_data(attr: TokenStream, item: TokenStream) -> TokenStream {
    send_body_with_data_macro(attr, item, Position::Epilogue)
}
#[proc_macro_attribute]
pub fn try_flush(_attr: TokenStream, item: TokenStream) -> TokenStream {
    try_flush_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn flush(_attr: TokenStream, item: TokenStream) -> TokenStream {
    flush_macro(item, Position::Prologue)
}
```
# Path: hyperlane-macros/src/closed/mod.rs
```rust
mod r#fn;
pub(crate) use r#fn::*;
```
# Path: hyperlane-macros/src/closed/fn.rs
```rust
use crate::*;
pub(crate) fn closed_macro(item: TokenStream, position: Position) -> TokenStream {
    inject(position, item, |context| {
        quote! {
            let _ = #context.closed().await;
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "closed",
        handler: Handler::NoAttrPosition(closed_macro),
    }
}
```
# Path: hyperlane-macros/src/hook/mod.rs
```rust
mod r#fn;
pub(crate) use r#fn::*;
```
# Path: hyperlane-macros/src/hook/fn.rs
```rust
use crate::*;
pub(crate) fn task_panic_macro(attr: TokenStream, item: TokenStream) -> TokenStream {
    let attr_args: OrderAttr = parse_macro_input!(attr as OrderAttr);
    let order: TokenStream2 = expr_to_isize(&attr_args.order);
    let input_struct: ItemStruct = parse_macro_input!(item as ItemStruct);
    let struct_name: &Ident = &input_struct.ident;
    let gen_code: TokenStream2 = quote! {
        #input_struct
        ::hyperlane::inventory::submit! {
            ::hyperlane::HookType::TaskPanic(#order, || ::hyperlane::server_hook_factory::<#struct_name>())
        }
    };
    gen_code.into()
}
inventory::submit! {
    InjectableMacro {
        name: "task_panic",
        handler: Handler::WithAttr(task_panic_macro),
    }
}
pub(crate) fn request_error_macro(attr: TokenStream, item: TokenStream) -> TokenStream {
    let attr_args: OrderAttr = parse_macro_input!(attr as OrderAttr);
    let order: TokenStream2 = expr_to_isize(&attr_args.order);
    let input_struct: ItemStruct = parse_macro_input!(item as ItemStruct);
    let struct_name: &Ident = &input_struct.ident;
    let gen_code: TokenStream2 = quote! {
        #input_struct
        ::hyperlane::inventory::submit! {
            ::hyperlane::HookType::RequestError(#order, || ::hyperlane::server_hook_factory::<#struct_name>())
        }
    };
    gen_code.into()
}
inventory::submit! {
    InjectableMacro {
        name: "request_error",
        handler: Handler::WithAttr(request_error_macro),
    }
}
pub(crate) fn prologue_hooks_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let functions: Punctuated<Ident, Token![,]> =
        parse_macro_input!(attr with Punctuated::parse_terminated);
    inject(position, item, |context| {
        let hook_calls = functions.iter().map(|function_name| {
            quote! {
                let _ = #function_name(#context.clone()).await;
            }
        });
        quote! {
            #(#hook_calls)*
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "prologue_hooks",
        handler: Handler::WithAttrPosition(prologue_hooks_macro),
    }
}
pub(crate) fn epilogue_hooks_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let functions: Punctuated<Ident, Token![,]> =
        parse_macro_input!(attr with Punctuated::parse_terminated);
    inject(position, item, |context| {
        let hook_calls = functions.iter().map(|function_name| {
            quote! {
                let _ = #function_name(#context.clone()).await;
            }
        });
        quote! {
            #(#hook_calls)*
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "epilogue_hooks",
        handler: Handler::WithAttrPosition(epilogue_hooks_macro),
    }
}
```
# Path: hyperlane-macros/src/response/mod.rs
```rust
mod r#enum;
mod r#fn;
mod r#impl;
mod r#struct;
pub(crate) use r#enum::*;
pub(crate) use r#fn::*;
pub(crate) use r#struct::*;
```
# Path: hyperlane-macros/src/response/enum.rs
```rust
pub(crate) enum HeaderOperation {
    Set,
    Add,
}
```
# Path: hyperlane-macros/src/response/struct.rs
```rust
use crate::*;
pub(crate) struct SendData {
    pub(crate) data: Expr,
}
```
# Path: hyperlane-macros/src/response/fn.rs
```rust
use crate::*;
pub(crate) fn response_status_code_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let value: Expr = match parse(attr) {
        Ok(v) => v,
        Err(err) => return err.to_compile_error().into(),
    };
    inject(position, item, |context| {
        quote! {
            #context.set_response_status_code(::hyperlane::ResponseStatusCode::from(#value as usize)).await;
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "response_status_code",
        handler: Handler::WithAttrPosition(response_status_code_macro),
    }
}
pub(crate) fn response_reason_phrase_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let value: Expr = match parse(attr) {
        Ok(v) => v,
        Err(err) => return err.to_compile_error().into(),
    };
    inject(position, item, |context| {
        quote! {
            #context.set_response_reason_phrase(&#value).await;
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "response_reason_phrase",
        handler: Handler::WithAttrPosition(response_reason_phrase_macro),
    }
}
pub(crate) fn response_header_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let header_data: ResponseHeaderData = parse_macro_input!(attr as ResponseHeaderData);
    let key: Expr = header_data.key;
    let value: Expr = header_data.value;
    let operation: HeaderOperation = header_data.operation;
    inject(position, item, |context| match operation {
        HeaderOperation::Add => {
            quote! {
                #context.add_response_header(&#key, &#value).await;
            }
        }
        HeaderOperation::Set => {
            quote! {
                #context.set_response_header(&#key, &#value).await;
            }
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "response_header",
        handler: Handler::WithAttrPosition(response_header_macro),
    }
}
pub(crate) fn response_body_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let body_data: ResponseBodyData = parse_macro_input!(attr as ResponseBodyData);
    let body: Expr = body_data.body;
    inject(position, item, |context| {
        quote! {
            #context.set_response_body(&#body).await;
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "response_body",
        handler: Handler::WithAttrPosition(response_body_macro),
    }
}
pub(crate) fn clear_response_headers_macro(item: TokenStream, position: Position) -> TokenStream {
    inject(position, item, |context| {
        quote! {
            #context.clear_response_headers().await;
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "clear_response_headers",
        handler: Handler::NoAttrPosition(clear_response_headers_macro),
    }
}
pub(crate) fn response_version_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let value: Expr = match parse(attr) {
        Ok(v) => v,
        Err(err) => return err.to_compile_error().into(),
    };
    inject(position, item, |context| {
        quote! {
            #context.set_response_version(#value).await;
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "response_version",
        handler: Handler::WithAttrPosition(response_version_macro),
    }
}
```
# Path: hyperlane-macros/src/response/impl.rs
```rust
use crate::*;
impl Parse for ResponseHeaderData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let key: Expr = input.parse()?;
        let operation: HeaderOperation = if input.peek(Token![=>]) {
            input.parse::<Token![=>]>()?;
            HeaderOperation::Set
        } else if input.peek(Token![,]) {
            input.parse::<Token![,]>()?;
            HeaderOperation::Add
        } else {
            return Err(syn::Error::new(
                input.span(),
                "Expected either ',' for add operation or '=>' for set operation",
            ));
        };
        let value: Expr = input.parse()?;
        Ok(ResponseHeaderData {
            key,
            value,
            operation,
        })
    }
}
impl Parse for ResponseBodyData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let body: Expr = input.parse()?;
        Ok(ResponseBodyData { body })
    }
}
```
# Path: hyperlane-macros/src/inject/mod.rs
```rust
pub(crate) mod r#fn;
pub(crate) use r#fn::*;
```
# Path: hyperlane-macros/src/inject/fn.rs
```rust
use crate::*;
fn apply_macro(macro_meta: &Meta, item_stream: TokenStream, position: Position) -> TokenStream {
    let (macro_name, macro_attr) = match macro_meta {
        Meta::Path(path) => (
            path.get_ident()
                .expect("Macro path should have an identifier")
                .to_string(),
            TokenStream::new(),
        ),
        Meta::List(meta_list) => (
            meta_list
                .path
                .get_ident()
                .expect("Macro path should have an identifier")
                .to_string(),
            meta_list.tokens.clone().into(),
        ),
        _ => panic!("Unsupported macro format in inject macro"),
    };
    for injectable_macro in inventory::iter::<InjectableMacro>() {
        if injectable_macro.name == macro_name {
            return match injectable_macro.handler {
                Handler::WithAttr(handler) => handler(macro_attr, item_stream),
                Handler::NoAttrPosition(handler) => {
                    if !macro_attr.is_empty() {
                        panic!("Macro {macro_name} does not take attributes");
                    }
                    handler(item_stream, position)
                }
                Handler::WithAttrPosition(handler) => handler(macro_attr, item_stream, position),
            };
        }
    }
    panic!("Unsupported macro: {macro_name}");
}
pub(crate) fn prologue_macros_macro(attr: TokenStream, item: TokenStream) -> TokenStream {
    let metas: Punctuated<Meta, Comma> = Punctuated::<Meta, Token![,]>::parse_terminated
        .parse(attr)
        .expect("Failed to parse macro attributes");
    let mut current_stream: TokenStream = item;
    for meta in metas.iter().rev() {
        current_stream = apply_macro(meta, current_stream, Position::Prologue);
    }
    current_stream
}
pub(crate) fn epilogue_macros_macro(attr: TokenStream, item: TokenStream) -> TokenStream {
    let metas: Punctuated<Meta, Comma> = Punctuated::<Meta, Token![,]>::parse_terminated
        .parse(attr)
        .expect("Failed to parse macro attributes");
    let mut current_stream: TokenStream = item;
    for meta in metas.iter() {
        current_stream = apply_macro(meta, current_stream, Position::Epilogue);
    }
    current_stream
}
```
# Path: hyperlane-macros/src/request_middleware/mod.rs
```rust
pub(crate) mod r#fn;
pub(crate) use r#fn::*;
```
# Path: hyperlane-macros/src/request_middleware/fn.rs
```rust
use crate::*;
pub(crate) fn request_middleware_macro(attr: TokenStream, item: TokenStream) -> TokenStream {
    let attr_args: OrderAttr = parse_macro_input!(attr as OrderAttr);
    let order: TokenStream2 = expr_to_isize(&attr_args.order);
    let input_struct: ItemStruct = parse_macro_input!(item as ItemStruct);
    let struct_name: &Ident = &input_struct.ident;
    let gen_code: TokenStream2 = quote! {
        #input_struct
        ::hyperlane::inventory::submit! {
            ::hyperlane::HookType::RequestMiddleware(#order, || ::hyperlane::server_hook_factory::<#struct_name>())
        }
    };
    gen_code.into()
}
inventory::submit! {
    InjectableMacro {
        name: "request_middleware",
        handler: Handler::WithAttr(request_middleware_macro),
    }
}
```
# Path: hyperlane-macros/src/hyperlane/mod.rs
```rust
pub(crate) mod r#fn;
pub(crate) mod r#impl;
pub(crate) mod r#struct;
pub(crate) use r#fn::*;
pub(crate) use r#struct::*;
```
# Path: hyperlane-macros/src/hyperlane/struct.rs
```rust
use crate::*;
pub(crate) struct MultiHyperlaneAttr {
    pub(crate) params: Vec<(Ident, Ident)>,
}
```
# Path: hyperlane-macros/src/hyperlane/fn.rs
```rust
use crate::*;
pub(crate) fn hyperlane_macro(attr: TokenStream, item: TokenStream) -> TokenStream {
    let multi_hyperlane: MultiHyperlaneAttr = parse_macro_input!(attr as MultiHyperlaneAttr);
    let input_fn: ItemFn = parse_macro_input!(item as ItemFn);
    let vis: &Visibility = &input_fn.vis;
    let sig: &Signature = &input_fn.sig;
    let block: &Block = &input_fn.block;
    let ident: &Ident = &sig.ident;
    let attrs: &Vec<Attribute> = &input_fn.attrs;
    let stmts: &Vec<Stmt> = &block.stmts;
    let inputs: &Punctuated<FnArg, token::Comma> = &sig.inputs;
    let output: &ReturnType = &sig.output;
    let mut init_statements: Vec<TokenStream2> = Vec::new();
    for (var_name, type_name) in &multi_hyperlane.params {
        init_statements.push(quote! {
            let #var_name: #type_name = #type_name::new().await;
        });
        if type_name == SERVER_TYPE_KEY {
            init_statements.push(quote! {
                let mut hooks: Vec<::hyperlane::HookType> = inventory::iter().cloned().collect();
                assert_hook_unique_order(hooks.clone());
                hooks.sort_by_key(|hook| hook.try_get_order());
                for hook in hooks {
                    #var_name.handle_hook(hook.clone()).await;
                }
            });
        }
    }
    let gen_code: TokenStream2 = quote! {
        #(#attrs)*
        #vis async fn #ident(#inputs) #output {
            #(#init_statements)*
            #(#stmts)*
        }
    };
    gen_code.into()
}
inventory::submit! {
    InjectableMacro {
        name: "hyperlane",
        handler: Handler::WithAttr(hyperlane_macro),
    }
}
```
# Path: hyperlane-macros/src/hyperlane/impl.rs
```rust
use crate::*;
impl Parse for MultiHyperlaneAttr {
    fn parse(input: ParseStream) -> Result<Self> {
        let mut params: Vec<(Ident, Ident)> = Vec::new();
        loop {
            let var_name: Ident = input.parse()?;
            input.parse::<Token![:]>()?;
            let type_name: Ident = input.parse()?;
            params.push((var_name, type_name));
            if input.is_empty() {
                break;
            }
            input.parse::<Token![,]>()?;
            if input.is_empty() {
                break;
            }
        }
        Ok(MultiHyperlaneAttr { params })
    }
}
```
# Path: hyperlane-macros/src/referer/mod.rs
```rust
mod r#fn;
mod r#impl;
mod r#struct;
pub(crate) use r#fn::*;
pub(crate) use r#struct::*;
```
# Path: hyperlane-macros/src/referer/struct.rs
```rust
use crate::*;
pub(crate) struct MultiRefererData {
    pub(crate) referer_values: Vec<Expr>,
}
```
# Path: hyperlane-macros/src/referer/fn.rs
```rust
use crate::*;
pub(crate) fn referer_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_referer: MultiRefererData = parse_macro_input!(attr as MultiRefererData);
    inject(position, item, |context| {
        let statements = multi_referer.referer_values.iter().map(|referer_value| {
            quote! {
                let referer: Option<::hyperlane::RequestHeadersValueItem> = #context.try_get_request_header_back(REFERER).await;
                if let Some(referer_header) = referer {
                    if referer_header != #referer_value {
                        return;
                    }
                } else {
                    return;
                }
            }
        });
        quote! {
            #(#statements)*
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "referer",
        handler: Handler::WithAttrPosition(referer_macro),
    }
}
pub(crate) fn reject_referer_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_referer: MultiRefererData = parse_macro_input!(attr as MultiRefererData);
    inject(position, item, |context| {
        let statements = multi_referer.referer_values.iter().map(|referer_value| {
            quote! {
                let referer: Option<::hyperlane::RequestHeadersValueItem> = #context.try_get_request_header_back(REFERER).await;
                if let Some(referer_header) = referer {
                    if referer_header == #referer_value {
                        return;
                    }
                }
            }
        });
        quote! {
            #(#statements)*
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "reject_referer",
        handler: Handler::WithAttrPosition(reject_referer_macro),
    }
}
```
# Path: hyperlane-macros/src/referer/impl.rs
```rust
use crate::*;
impl Parse for MultiRefererData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let mut referer_values: Vec<Expr> = Vec::new();
        loop {
            let referer_value: Expr = input.parse()?;
            referer_values.push(referer_value);
            if input.is_empty() {
                break;
            }
            input.parse::<Token![,]>()?;
            if input.is_empty() {
                break;
            }
        }
        Ok(MultiRefererData { referer_values })
    }
}
```
# Path: hyperlane-macros/src/flush/mod.rs
```rust
mod r#fn;
pub(crate) use r#fn::*;
```
# Path: hyperlane-macros/src/flush/fn.rs
```rust
use crate::*;
pub(crate) fn try_flush_macro(item: TokenStream, position: Position) -> TokenStream {
    inject(position, item, |context| {
        quote! {
            let _ = #context.try_flush().await;
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "try_flush",
        handler: Handler::NoAttrPosition(try_flush_macro),
    }
}
inventory::submit! {
    InjectableMacro {
        name: "flush",
        handler: Handler::NoAttrPosition(flush_macro),
    }
}
pub(crate) fn flush_macro(item: TokenStream, position: Position) -> TokenStream {
    inject(position, item, |context| {
        quote! {
            #context.flush().await;
        }
    })
}
```
# Path: hyperlane-macros/src/protocol/mod.rs
```rust
mod r#fn;
pub(crate) use r#fn::*;
```
# Path: hyperlane-macros/src/protocol/fn.rs
```rust
use crate::*;
pub(crate) fn ws_macro(item: TokenStream, position: Position) -> TokenStream {
    inject(position, item, |context| {
        quote! {
            if !#context.get_request().await.is_ws() {
                return;
            }
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "ws",
        handler: Handler::NoAttrPosition(ws_macro),
    }
}
pub(crate) fn http_macro(item: TokenStream, position: Position) -> TokenStream {
    inject(position, item, |context| {
        quote! {
            if !#context.get_request().await.is_http() {
                return;
            }
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "http",
        handler: Handler::NoAttrPosition(http_macro),
    }
}
macro_rules! impl_protocol_check_macro {
    ($name:ident, $check:ident, $str_name:expr) => {
        pub(crate) fn $name(item: TokenStream, position: Position) -> TokenStream {
            inject(position, item, |context| {
                let check_fn = Ident::new(stringify!($check), proc_macro2::Span::call_site());
                quote! {
                    let request: ::hyperlane::Request = #context.get_request().await;
                    if !request.#check_fn() {
                        return;
                    }
                }
            })
        }
        inventory::submit! {
            InjectableMacro {
                name: $str_name,
                handler: Handler::NoAttrPosition($name),
            }
        }
    };
}
impl_protocol_check_macro!(h2c_macro, is_h2c, "h2c");
impl_protocol_check_macro!(http0_9_macro, is_http0_9, "http0_9");
impl_protocol_check_macro!(http1_0_macro, is_http1_0, "http1_0");
impl_protocol_check_macro!(http1_1_macro, is_http1_1, "http1_1");
impl_protocol_check_macro!(
    http1_1_or_higher_macro,
    is_http1_1_or_higher,
    "http1_1_or_higher"
);
impl_protocol_check_macro!(http2_macro, is_http2, "http2");
impl_protocol_check_macro!(http3_macro, is_http3, "http3");
impl_protocol_check_macro!(tls_macro, is_tls, "tls");
```
# Path: hyperlane-macros/src/request/mod.rs
```rust
mod r#fn;
mod r#impl;
mod r#struct;
pub(crate) use r#fn::*;
pub(crate) use r#struct::*;
```
# Path: hyperlane-macros/src/request/struct.rs
```rust
use crate::*;
pub(crate) struct RequestMethods {
    pub(crate) methods: Punctuated<Ident, Token![,]>,
}
pub(crate) struct MultiRequestBodyData {
    pub(crate) variables: Vec<Ident>,
}
pub(crate) struct MultiRequestBodyJsonData {
    pub(crate) params: Vec<(Ident, Type)>,
}
pub(crate) struct MultiAttributeData {
    pub(crate) params: Vec<(Expr, Ident, Type)>,
}
pub(crate) struct MultiAttributesData {
    pub(crate) variables: Vec<Ident>,
}
pub(crate) struct MultiRouteParamData {
    pub(crate) params: Vec<(Expr, Ident)>,
}
pub(crate) struct MultiRouteParamsData {
    pub(crate) variables: Vec<Ident>,
}
pub(crate) struct MultiQueryData {
    pub(crate) params: Vec<(Expr, Ident)>,
}
pub(crate) struct MultiQuerysData {
    pub(crate) variables: Vec<Ident>,
}
pub(crate) struct MultiHeaderData {
    pub(crate) params: Vec<(Expr, Ident)>,
}
pub(crate) struct MultiHeadersData {
    pub(crate) variables: Vec<Ident>,
}
pub(crate) struct MultiCookieData {
    pub(crate) params: Vec<(Expr, Ident)>,
}
pub(crate) struct MultiCookiesData {
    pub(crate) variables: Vec<Ident>,
}
pub(crate) struct MultiRequestVersionData {
    pub(crate) variables: Vec<Ident>,
}
pub(crate) struct MultiRequestPathData {
    pub(crate) variables: Vec<Ident>,
}
pub(crate) struct MultiPanicData {
    pub(crate) variables: Vec<Ident>,
}
pub(crate) struct MultiRequestErrorData {
    pub(crate) variables: Vec<Ident>,
}
```
# Path: hyperlane-macros/src/request/fn.rs
```rust
use crate::*;
pub(crate) fn request_body_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_body: MultiRequestBodyData = parse_macro_input!(attr as MultiRequestBodyData);
    inject(position, item, |context| {
        let statements = multi_body.variables.iter().map(|variable| {
            quote! {
                let #variable: ::hyperlane::RequestBody = #context.get_request_body().await;
            }
        });
        quote! {
            #(#statements)*
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "request_body",
        handler: Handler::WithAttrPosition(request_body_macro),
    }
}
pub(crate) fn request_body_json_result_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_body_json: MultiRequestBodyJsonData =
        parse_macro_input!(attr as MultiRequestBodyJsonData);
    inject(position, item, |context| {
        let statements = multi_body_json.params.iter().map(|(variable, type_name)| {
            quote! {
                let #variable: Result<#type_name, ::hyperlane::serde_json::Error> = #context.try_get_request_body_json::<#type_name>().await;
            }
        });
        quote! {
            #(#statements)*
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "request_body_json_result",
        handler: Handler::WithAttrPosition(request_body_json_result_macro),
    }
}
pub(crate) fn request_body_json_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_body_json: MultiRequestBodyJsonData =
        parse_macro_input!(attr as MultiRequestBodyJsonData);
    inject(position, item, |context| {
        let statements = multi_body_json.params.iter().map(|(variable, type_name)| {
            quote! {
                let #variable: #type_name = #context.get_request_body_json::<#type_name>().await;
            }
        });
        quote! {
            #(#statements)*
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "request_body_json",
        handler: Handler::WithAttrPosition(request_body_json_macro),
    }
}
pub(crate) fn attribute_option_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_attr: MultiAttributeData = parse_macro_input!(attr as MultiAttributeData);
    inject(position, item, |context| {
        let statements = multi_attr
            .params
            .iter()
            .map(|(key_name, variable, type_name)| {
                quote! {
                    let #variable: Option<#type_name> = #context.try_get_attribute(&#key_name).await;
                }
            });
        quote! {
            #(#statements)*
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "attribute_option",
        handler: Handler::WithAttrPosition(attribute_option_macro),
    }
}
pub(crate) fn attribute_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_attr: MultiAttributeData = parse_macro_input!(attr as MultiAttributeData);
    inject(position, item, |context| {
        let statements = multi_attr
            .params
            .iter()
            .map(|(key_name, variable, type_name)| {
                quote! {
                    let #variable: #type_name = #context.get_attribute(&#key_name).await;
                }
            });
        quote! {
            #(#statements)*
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "attribute",
        handler: Handler::WithAttrPosition(attribute_macro),
    }
}
pub(crate) fn attributes_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_attrs: MultiAttributesData = parse_macro_input!(attr as MultiAttributesData);
    inject(position, item, |context| {
        let statements = multi_attrs.variables.iter().map(|variable| {
            quote! {
                let #variable: ::hyperlane::ThreadSafeAttributeStore = #context.get_attributes().await;
            }
        });
        quote! {
            #(#statements)*
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "attributes",
        handler: Handler::WithAttrPosition(attributes_macro),
    }
}
pub(crate) fn task_panic_data_option_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_task_panic_data: MultiPanicData = parse_macro_input!(attr as MultiPanicData);
    inject(position, item, |context| {
        let statements = multi_task_panic_data.variables.iter().map(|variable| {
            quote! {
                let #variable: Option<::hyperlane::PanicData> = #context.try_get_task_panic_data().await;
            }
        });
        quote! {
            #(#statements)*
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "task_panic_data_option",
        handler: Handler::WithAttrPosition(task_panic_data_option_macro),
    }
}
pub(crate) fn task_panic_data_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_task_panic_data: MultiPanicData = parse_macro_input!(attr as MultiPanicData);
    inject(position, item, |context| {
        let statements = multi_task_panic_data.variables.iter().map(|variable| {
            quote! {
                let #variable: ::hyperlane::PanicData = #context.get_task_panic_data().await;
            }
        });
        quote! {
            #(#statements)*
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "task_panic_data",
        handler: Handler::WithAttrPosition(task_panic_data_macro),
    }
}
pub(crate) fn request_error_data_option_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_error_data: MultiRequestErrorData = parse_macro_input!(attr as MultiRequestErrorData);
    inject(position, item, |context| {
        let statements = multi_error_data.variables.iter().map(|variable| {
            quote! {
                let #variable: Option<::hyperlane::RequestError> = #context.try_get_request_error_data().await;
            }
        });
        quote! {
            #(#statements)*
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "request_error_data_option",
        handler: Handler::WithAttrPosition(request_error_data_option_macro),
    }
}
pub(crate) fn request_error_data_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_error_data: MultiRequestErrorData = parse_macro_input!(attr as MultiRequestErrorData);
    inject(position, item, |context| {
        let statements = multi_error_data.variables.iter().map(|variable| {
            quote! {
                let #variable: ::hyperlane::RequestError = #context.get_request_error_data().await;
            }
        });
        quote! {
            #(#statements)*
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "request_error_data",
        handler: Handler::WithAttrPosition(request_error_data_macro),
    }
}
pub(crate) fn route_param_option_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_param: MultiRouteParamData = parse_macro_input!(attr as MultiRouteParamData);
    inject(position, item, |context| {
        let statements = multi_param.params.iter().map(|(key_name, variable)| {
            quote! {
                let #variable: Option<std::string::String> = #context.try_get_route_param(#key_name).await;
            }
        });
        quote! {
            #(#statements)*
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "route_param_option",
        handler: Handler::WithAttrPosition(route_param_option_macro),
    }
}
pub(crate) fn route_param_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_param: MultiRouteParamData = parse_macro_input!(attr as MultiRouteParamData);
    inject(position, item, |context| {
        let statements = multi_param.params.iter().map(|(key_name, variable)| {
            quote! {
                let #variable: std::string::String = #context.get_route_param(#key_name).await;
            }
        });
        quote! {
            #(#statements)*
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "route_param",
        handler: Handler::WithAttrPosition(route_param_macro),
    }
}
pub(crate) fn route_params_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_route_params: MultiRouteParamsData = parse_macro_input!(attr as MultiRouteParamsData);
    inject(position, item, |context| {
        let statements = multi_route_params.variables.iter().map(|variable| {
            quote! {
                let #variable: ::hyperlane::RouteParams = #context.get_route_params().await;
            }
        });
        quote! {
            #(#statements)*
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "route_params",
        handler: Handler::WithAttrPosition(route_params_macro),
    }
}
pub(crate) fn request_query_option_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_query: MultiQueryData = parse_macro_input!(attr as MultiQueryData);
    inject(position, item, |context| {
        let statements = multi_query.params.iter().map(|(key_name, variable)| {
            quote! {
                let #variable: Option<::hyperlane::RequestQuerysValue> = #context.try_get_request_query(#key_name).await;
            }
        });
        quote! {
            #(#statements)*
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "request_query_option",
        handler: Handler::WithAttrPosition(request_query_option_macro),
    }
}
pub(crate) fn request_query_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_query: MultiQueryData = parse_macro_input!(attr as MultiQueryData);
    inject(position, item, |context| {
        let statements = multi_query.params.iter().map(|(key_name, variable)| {
            quote! {
                let #variable: ::hyperlane::RequestQuerysValue = #context.get_request_query(#key_name).await;
            }
        });
        quote! {
            #(#statements)*
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "request_query",
        handler: Handler::WithAttrPosition(request_query_macro),
    }
}
pub(crate) fn request_querys_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_querys: MultiQuerysData = parse_macro_input!(attr as MultiQuerysData);
    inject(position, item, |context| {
        let statements = multi_querys.variables.iter().map(|variable| {
            quote! {
                let #variable: ::hyperlane::RequestQuerys = #context.get_request_querys().await;
            }
        });
        quote! {
            #(#statements)*
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "request_querys",
        handler: Handler::WithAttrPosition(request_querys_macro),
    }
}
pub(crate) fn request_header_option_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_header: MultiHeaderData = parse_macro_input!(attr as MultiHeaderData);
    inject(position, item, |context| {
        let statements = multi_header.params.iter().map(|(key_name, variable)| {
            quote! {
                let #variable: Option<::hyperlane::RequestHeadersValueItem> = #context.try_get_request_header_back(#key_name).await;
            }
        });
        quote! {
            #(#statements)*
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "request_header_option",
        handler: Handler::WithAttrPosition(request_header_option_macro),
    }
}
pub(crate) fn request_header_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_header: MultiHeaderData = parse_macro_input!(attr as MultiHeaderData);
    inject(position, item, |context| {
        let statements = multi_header.params.iter().map(|(key_name, variable)| {
            quote! {
                let #variable: ::hyperlane::RequestHeadersValueItem = #context.get_request_header_back(#key_name).await;
            }
        });
        quote! {
            #(#statements)*
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "request_header",
        handler: Handler::WithAttrPosition(request_header_macro),
    }
}
pub(crate) fn request_headers_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_headers: MultiHeadersData = parse_macro_input!(attr as MultiHeadersData);
    inject(position, item, |context| {
        let statements = multi_headers.variables.iter().map(|variable| {
            quote! {
                let #variable: ::hyperlane::RequestHeaders = #context.get_request_headers().await;
            }
        });
        quote! {
            #(#statements)*
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "request_headers",
        handler: Handler::WithAttrPosition(request_headers_macro),
    }
}
pub(crate) fn request_cookie_option_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_cookie: MultiCookieData = parse_macro_input!(attr as MultiCookieData);
    inject(position, item, |context| {
        let statements = multi_cookie.params.iter().map(|(key_name, variable)| {
            quote! {
                let #variable: Option<::hyperlane::CookieValue> = #context.try_get_request_cookie(#key_name).await;
            }
        });
        quote! {
            #(#statements)*
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "request_cookie_option",
        handler: Handler::WithAttrPosition(request_cookie_option_macro),
    }
}
pub(crate) fn request_cookie_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_cookie: MultiCookieData = parse_macro_input!(attr as MultiCookieData);
    inject(position, item, |context| {
        let statements = multi_cookie.params.iter().map(|(key_name, variable)| {
            quote! {
                let #variable: ::hyperlane::CookieValue = #context.get_request_cookie(#key_name).await;
            }
        });
        quote! {
            #(#statements)*
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "request_cookie",
        handler: Handler::WithAttrPosition(request_cookie_macro),
    }
}
pub(crate) fn request_cookies_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_cookies: MultiCookiesData = parse_macro_input!(attr as MultiCookiesData);
    inject(position, item, |context| {
        let statements = multi_cookies.variables.iter().map(|variable| {
            quote! {
                let #variable: ::hyperlane::Cookies = #context.get_request_cookies().await;
            }
        });
        quote! {
            #(#statements)*
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "request_cookies",
        handler: Handler::WithAttrPosition(request_cookies_macro),
    }
}
pub(crate) fn request_version_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_version: MultiRequestVersionData =
        parse_macro_input!(attr as MultiRequestVersionData);
    inject(position, item, |context| {
        let statements = multi_version.variables.iter().map(|variable| {
            quote! {
                let #variable: ::hyperlane::RequestVersion = #context.get_request_version().await;
            }
        });
        quote! {
            #(#statements)*
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "request_version",
        handler: Handler::WithAttrPosition(request_version_macro),
    }
}
pub(crate) fn request_path_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_path: MultiRequestPathData = parse_macro_input!(attr as MultiRequestPathData);
    inject(position, item, |context| {
        let statements = multi_path.variables.iter().map(|variable| {
            quote! {
                let #variable: ::hyperlane::RequestPath = #context.get_request_path().await;
            }
        });
        quote! {
            #(#statements)*
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "request_path",
        handler: Handler::WithAttrPosition(request_path_macro),
    }
}
```
# Path: hyperlane-macros/src/request/impl.rs
```rust
use crate::*;
impl Parse for RequestMethods {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        Ok(RequestMethods {
            methods: Punctuated::parse_separated_nonempty(input)?,
        })
    }
}
impl Parse for MultiRequestBodyData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let mut variables: Vec<Ident> = Vec::new();
        loop {
            let variable: Ident = input.parse()?;
            variables.push(variable);
            if input.is_empty() {
                break;
            }
            input.parse::<Token![,]>()?;
            if input.is_empty() {
                break;
            }
        }
        Ok(MultiRequestBodyData { variables })
    }
}
impl Parse for MultiRequestBodyJsonData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let mut params: Vec<(Ident, Type)> = Vec::new();
        loop {
            let variable: Ident = input.parse()?;
            input.parse::<Token![:]>()?;
            let type_name: Type = input.parse()?;
            params.push((variable, type_name));
            if input.is_empty() {
                break;
            }
            input.parse::<Token![,]>()?;
            if input.is_empty() {
                break;
            }
        }
        Ok(MultiRequestBodyJsonData { params })
    }
}
impl Parse for MultiAttributeData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let mut params: Vec<(Expr, Ident, Type)> = Vec::new();
        loop {
            let key_name: Expr = input.parse()?;
            input.parse::<Token![=>]>()?;
            let variable: Ident = input.parse()?;
            input.parse::<Token![:]>()?;
            let type_name: Type = input.parse()?;
            params.push((key_name, variable, type_name));
            if input.is_empty() {
                break;
            }
            input.parse::<Token![,]>()?;
            if input.is_empty() {
                break;
            }
        }
        Ok(MultiAttributeData { params })
    }
}
impl Parse for MultiAttributesData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let mut variables: Vec<Ident> = Vec::new();
        loop {
            let variable: Ident = input.parse()?;
            variables.push(variable);
            if input.is_empty() {
                break;
            }
            input.parse::<Token![,]>()?;
            if input.is_empty() {
                break;
            }
        }
        Ok(MultiAttributesData { variables })
    }
}
impl Parse for MultiRouteParamData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let mut params: Vec<(Expr, Ident)> = Vec::new();
        loop {
            let key_name: Expr = input.parse()?;
            input.parse::<Token![=>]>()?;
            let variable: Ident = input.parse()?;
            params.push((key_name, variable));
            if input.is_empty() {
                break;
            }
            input.parse::<Token![,]>()?;
            if input.is_empty() {
                break;
            }
        }
        Ok(MultiRouteParamData { params })
    }
}
impl Parse for MultiRouteParamsData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let mut variables: Vec<Ident> = Vec::new();
        loop {
            let variable: Ident = input.parse()?;
            variables.push(variable);
            if input.is_empty() {
                break;
            }
            input.parse::<Token![,]>()?;
            if input.is_empty() {
                break;
            }
        }
        Ok(MultiRouteParamsData { variables })
    }
}
impl Parse for MultiQueryData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let mut params: Vec<(Expr, Ident)> = Vec::new();
        loop {
            let key_name: Expr = input.parse()?;
            input.parse::<Token![=>]>()?;
            let variable: Ident = input.parse()?;
            params.push((key_name, variable));
            if input.is_empty() {
                break;
            }
            input.parse::<Token![,]>()?;
            if input.is_empty() {
                break;
            }
        }
        Ok(MultiQueryData { params })
    }
}
impl Parse for MultiQuerysData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let mut variables: Vec<Ident> = Vec::new();
        loop {
            let variable: Ident = input.parse()?;
            variables.push(variable);
            if input.is_empty() {
                break;
            }
            input.parse::<Token![,]>()?;
            if input.is_empty() {
                break;
            }
        }
        Ok(MultiQuerysData { variables })
    }
}
impl Parse for MultiHeaderData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let mut params: Vec<(Expr, Ident)> = Vec::new();
        loop {
            let key_name: Expr = input.parse()?;
            input.parse::<Token![=>]>()?;
            let variable: Ident = input.parse()?;
            params.push((key_name, variable));
            if input.is_empty() {
                break;
            }
            input.parse::<Token![,]>()?;
            if input.is_empty() {
                break;
            }
        }
        Ok(MultiHeaderData { params })
    }
}
impl Parse for MultiHeadersData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let mut variables: Vec<Ident> = Vec::new();
        loop {
            let variable: Ident = input.parse()?;
            variables.push(variable);
            if input.is_empty() {
                break;
            }
            input.parse::<Token![,]>()?;
            if input.is_empty() {
                break;
            }
        }
        Ok(MultiHeadersData { variables })
    }
}
impl Parse for MultiCookieData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let mut params: Vec<(Expr, Ident)> = Vec::new();
        loop {
            let key_name: Expr = input.parse()?;
            input.parse::<Token![=>]>()?;
            let variable: Ident = input.parse()?;
            params.push((key_name, variable));
            if input.is_empty() {
                break;
            }
            input.parse::<Token![,]>()?;
            if input.is_empty() {
                break;
            }
        }
        Ok(MultiCookieData { params })
    }
}
impl Parse for MultiCookiesData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let mut variables: Vec<Ident> = Vec::new();
        loop {
            let variable: Ident = input.parse()?;
            variables.push(variable);
            if input.is_empty() {
                break;
            }
            input.parse::<Token![,]>()?;
            if input.is_empty() {
                break;
            }
        }
        Ok(MultiCookiesData { variables })
    }
}
impl Parse for MultiRequestVersionData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let mut variables: Vec<Ident> = Vec::new();
        loop {
            let variable: Ident = input.parse()?;
            variables.push(variable);
            if input.is_empty() {
                break;
            }
            input.parse::<Token![,]>()?;
            if input.is_empty() {
                break;
            }
        }
        Ok(MultiRequestVersionData { variables })
    }
}
impl Parse for MultiRequestPathData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let mut variables: Vec<Ident> = Vec::new();
        loop {
            let variable: Ident = input.parse()?;
            variables.push(variable);
            if input.is_empty() {
                break;
            }
            input.parse::<Token![,]>()?;
            if input.is_empty() {
                break;
            }
        }
        Ok(MultiRequestPathData { variables })
    }
}
impl Parse for MultiPanicData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let mut variables: Vec<Ident> = Vec::new();
        loop {
            let variable: Ident = input.parse()?;
            variables.push(variable);
            if input.is_empty() {
                break;
            }
            input.parse::<Token![,]>()?;
            if input.is_empty() {
                break;
            }
        }
        Ok(MultiPanicData { variables })
    }
}
impl Parse for MultiRequestErrorData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let mut variables: Vec<Ident> = Vec::new();
        loop {
            let variable: Ident = input.parse()?;
            variables.push(variable);
            if input.is_empty() {
                break;
            }
            input.parse::<Token![,]>()?;
            if input.is_empty() {
                break;
            }
        }
        Ok(MultiRequestErrorData { variables })
    }
}
```
# Path: hyperlane-macros/src/aborted/mod.rs
```rust
mod r#fn;
pub(crate) use r#fn::*;
```
# Path: hyperlane-macros/src/aborted/fn.rs
```rust
use crate::*;
pub(crate) fn aborted_macro(item: TokenStream, position: Position) -> TokenStream {
    inject(position, item, |context| {
        quote! {
            let _ = #context.aborted().await;
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "aborted",
        handler: Handler::NoAttrPosition(aborted_macro),
    }
}
```
# Path: hyperlane-macros/src/stream/mod.rs
```rust
mod r#fn;
pub(crate) use r#fn::*;
```
# Path: hyperlane-macros/src/stream/fn.rs
```rust
use crate::*;
use syn::Ident;
pub(crate) fn generate_stream(
    context: &Ident,
    stream_method: &str,
    data: &FromStreamData,
    stmts: &[Stmt],
) -> TokenStream2 {
    let method_ident: Ident = Ident::new(stream_method, proc_macro2::Span::call_site());
    match (data.request_config.clone(), data.variable_name.clone()) {
        (Some(request_config), Some(variable_name)) => {
            quote! {
                while let Ok(#variable_name) = #context.#method_ident(#request_config).await {
                    #(#stmts)*
                }
            }
        }
        (Some(request_config), None) => {
            quote! {
                while #context.#method_ident(#request_config).await.is_ok() {
                    #(#stmts)*
                }
            }
        }
        (None, Some(variable_name)) => {
            quote! {
                while let Ok(#variable_name) = #context.#method_ident(::hyperlane::RequestConfig::default()).await {
                    #(#stmts)*
                }
            }
        }
        (None, None) => {
            quote! {
                while #context.#method_ident(::hyperlane::RequestConfig::default()).await.is_ok() {
                    #(#stmts)*
                }
            }
        }
    }
}
pub(crate) fn http_from_stream_macro(attr: TokenStream, item: TokenStream) -> TokenStream {
    let data: FromStreamData = parse_macro_input!(attr as FromStreamData);
    let input_fn: ItemFn = parse_macro_input!(item as ItemFn);
    let vis: &Visibility = &input_fn.vis;
    let sig: &Signature = &input_fn.sig;
    let block: &Block = &input_fn.block;
    let attrs: &Vec<Attribute> = &input_fn.attrs;
    match parse_context_from_signature(sig) {
        Ok(context) => {
            let stmts: &Vec<Stmt> = &block.stmts;
            let loop_stream: TokenStream2 =
                generate_stream(context, "http_from_stream", &data, stmts);
            quote! {
                #(#attrs)*
                #vis #sig {
                    #loop_stream
                }
            }
            .into()
        }
        Err(err) => err.to_compile_error().into(),
    }
}
inventory::submit! {
    InjectableMacro {
        name: "http_from_stream",
        handler: Handler::WithAttr(http_from_stream_macro),
    }
}
pub(crate) fn ws_from_stream_macro(attr: TokenStream, item: TokenStream) -> TokenStream {
    let data: FromStreamData = parse_macro_input!(attr as FromStreamData);
    let input_fn: ItemFn = parse_macro_input!(item as ItemFn);
    let vis: &Visibility = &input_fn.vis;
    let sig: &Signature = &input_fn.sig;
    let block: &Block = &input_fn.block;
    let attrs: &Vec<Attribute> = &input_fn.attrs;
    match parse_context_from_signature(sig) {
        Ok(context) => {
            let stmts: &Vec<Stmt> = &block.stmts;
            let loop_stream: TokenStream2 =
                generate_stream(context, "ws_from_stream", &data, stmts);
            quote! {
                #(#attrs)*
                #vis #sig {
                    #loop_stream
                }
            }
            .into()
        }
        Err(err) => err.to_compile_error().into(),
    }
}
inventory::submit! {
    InjectableMacro {
        name: "ws_from_stream",
        handler: Handler::WithAttr(ws_from_stream_macro),
    }
}
```
# Path: hyperlane-macros/src/from_stream/mod.rs
```rust
mod r#impl;
mod r#struct;
pub(crate) use r#struct::*;
```
# Path: hyperlane-macros/src/from_stream/struct.rs
```rust
use crate::*;
pub(crate) struct FromStreamData {
    pub(crate) request_config: Option<Expr>,
    pub(crate) variable_name: Option<Expr>,
}
```
# Path: hyperlane-macros/src/from_stream/impl.rs
```rust
use crate::*;
impl Parse for FromStreamData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let mut request_config: Option<Expr> = None;
        let mut variable_name: Option<Expr> = None;
        if input.is_empty() {
            return Ok(FromStreamData {
                request_config,
                variable_name,
            });
        }
        let first_expr: Expr = input.parse()?;
        if input.is_empty() {
            if is_integer_literal(&first_expr) {
                request_config = Some(first_expr);
            } else {
                variable_name = Some(first_expr);
            }
        } else {
            input.parse::<Token![,]>()?;
            if input.is_empty() {
                return Err(syn::Error::new(
                    input.span(),
                    "expected second parameter after comma",
                ));
            }
            let second_expr: Expr = input.parse()?;
            let first_is_int: bool = is_integer_literal(&first_expr);
            let second_is_int: bool = is_integer_literal(&second_expr);
            match (first_is_int, second_is_int) {
                (true, true) => {
                    return Err(syn::Error::new_spanned(
                        &second_expr,
                        "cannot have two request config parameters",
                    ));
                }
                (false, false) => {
                    return Err(syn::Error::new_spanned(
                        &second_expr,
                        "cannot have two variable name parameters",
                    ));
                }
                (true, false) => {
                    request_config = Some(first_expr);
                    variable_name = Some(second_expr);
                }
                (false, true) => {
                    variable_name = Some(first_expr);
                    request_config = Some(second_expr);
                }
            }
        }
        if !input.is_empty() {
            return Err(syn::Error::new_spanned(
                input.parse::<TokenStream2>()?,
                "unexpected additional tokens in attribute",
            ));
        }
        Ok(FromStreamData {
            request_config,
            variable_name,
        })
    }
}
```
# Path: hyperlane-macros/src/host/mod.rs
```rust
pub(crate) mod r#fn;
pub(crate) mod r#impl;
pub(crate) mod r#struct;
pub(crate) use r#fn::*;
pub(crate) use r#struct::*;
```
# Path: hyperlane-macros/src/host/struct.rs
```rust
use crate::*;
pub(crate) struct MultiHostData {
    pub(crate) host_values: Vec<Expr>,
}
```
# Path: hyperlane-macros/src/host/fn.rs
```rust
use crate::*;
pub(crate) fn host_macro(attr: TokenStream, item: TokenStream, position: Position) -> TokenStream {
    let multi_host: MultiHostData = parse_macro_input!(attr as MultiHostData);
    inject(position, item, |context| {
        let statements = multi_host.host_values.iter().map(|host_value| {
            quote! {
                let request_host: ::hyperlane::RequestHost = #context.get_request_host().await;
                if request_host.as_str() != #host_value {
                    return;
                }
            }
        });
        quote! {
            #(#statements)*
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "host",
        handler: Handler::WithAttrPosition(host_macro),
    }
}
pub(crate) fn reject_host_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_host: MultiHostData = parse_macro_input!(attr as MultiHostData);
    inject(position, item, |context| {
        let statements = multi_host.host_values.iter().map(|host_value| {
            quote! {
                let request_host: ::hyperlane::RequestHost = #context.get_request_host().await;
                if request_host.as_str() == #host_value {
                    return;
                }
            }
        });
        quote! {
            #(#statements)*
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "reject_host",
        handler: Handler::WithAttrPosition(reject_host_macro),
    }
}
```
# Path: hyperlane-macros/src/host/impl.rs
```rust
use crate::*;
impl Parse for MultiHostData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let mut host_values: Vec<Expr> = Vec::new();
        loop {
            let host_value: Expr = input.parse()?;
            host_values.push(host_value);
            if input.is_empty() {
                break;
            }
            input.parse::<Token![,]>()?;
            if input.is_empty() {
                break;
            }
        }
        Ok(MultiHostData { host_values })
    }
}
```
# Path: hyperlane-macros/src/common/const.rs
```rust
pub(crate) const SERVER_TYPE_KEY: &str = "Server";
```
# Path: hyperlane-macros/src/common/mod.rs
```rust
mod r#const;
mod r#enum;
mod r#fn;
mod r#impl;
mod r#struct;
mod r#type;
pub(crate) use r#const::*;
pub(crate) use r#enum::*;
pub(crate) use r#fn::*;
pub(crate) use r#struct::*;
pub(crate) use r#type::*;
```
# Path: hyperlane-macros/src/common/enum.rs
```rust
use crate::*;
pub(crate) enum Handler {
    WithAttr(MacroHandlerWithAttr),
    NoAttrPosition(MacroHandlerPosition),
    WithAttrPosition(MacroHandlerWithAttrPosition),
}
pub(crate) enum Position {
    Prologue,
    Epilogue,
}
```
# Path: hyperlane-macros/src/common/struct.rs
```rust
use crate::*;
#[derive(Clone)]
pub(crate) struct OrderAttr {
    pub(crate) order: Option<Expr>,
}
pub(crate) struct InjectableMacro {
    pub(crate) name: &'static str,
    pub(crate) handler: Handler,
}
```
# Path: hyperlane-macros/src/common/fn.rs
```rust
use crate::*;
fn inject_at_start(
    input: TokenStream,
    before_fn: impl FnOnce(&Ident) -> TokenStream2,
) -> TokenStream {
    let input_fn: ItemFn = parse_macro_input!(input as ItemFn);
    let vis: &Visibility = &input_fn.vis;
    let sig: &Signature = &input_fn.sig;
    let block: &Block = &input_fn.block;
    let attrs: &Vec<Attribute> = &input_fn.attrs;
    match parse_context_from_signature(sig) {
        Ok(context) => {
            let before_code: TokenStream2 = before_fn(context);
            let stmts: &Vec<Stmt> = &block.stmts;
            let gen_code: TokenStream2 = quote! {
                #(#attrs)*
                #vis #sig {
                    #before_code
                    #(#stmts)*
                }
            };
            gen_code.into()
        }
        Err(err) => err.to_compile_error().into(),
    }
}
fn inject_at_end(input: TokenStream, after_fn: impl FnOnce(&Ident) -> TokenStream2) -> TokenStream {
    let input_fn: ItemFn = parse_macro_input!(input as ItemFn);
    let vis: &Visibility = &input_fn.vis;
    let sig: &Signature = &input_fn.sig;
    let block: &Block = &input_fn.block;
    let attrs: &Vec<Attribute> = &input_fn.attrs;
    match parse_context_from_signature(sig) {
        Ok(context) => {
            let after_code: TokenStream2 = after_fn(context);
            let stmts: &Vec<Stmt> = &block.stmts;
            let gen_code: TokenStream2 = quote! {
                #(#attrs)*
                #vis #sig {
                    #(#stmts)*
                    #after_code
                }
            };
            gen_code.into()
        }
        Err(err) => err.to_compile_error().into(),
    }
}
pub(crate) fn inject(
    position: Position,
    input: TokenStream,
    hook: impl FnOnce(&Ident) -> TokenStream2,
) -> TokenStream {
    match position {
        Position::Prologue => inject_at_start(input, hook),
        Position::Epilogue => inject_at_end(input, hook),
    }
}
#[allow(dead_code)]
pub(crate) fn parse_context_from_fn(sig: &Signature) -> syn::Result<&Ident> {
    match sig.inputs.first() {
        Some(FnArg::Typed(pat_type)) => match &*pat_type.pat {
            Pat::Ident(pat_ident) => Ok(&pat_ident.ident),
            Pat::Wild(wild) => Err(syn::Error::new_spanned(
                wild,
                "The argument cannot be anonymous `_`, please use a named identifier",
            )),
            _ => Err(syn::Error::new_spanned(
                &pat_type.pat,
                "expected identifier as first argument",
            )),
        },
        _ => Err(syn::Error::new_spanned(
            &sig.inputs,
            "expected at least one argument",
        )),
    }
}
#[allow(dead_code)]
pub(crate) fn parse_self_from_method(sig: &Signature) -> syn::Result<&Ident> {
    match sig.inputs.first() {
        Some(FnArg::Receiver(_)) => match sig.inputs.iter().nth(1) {
            Some(FnArg::Typed(pat_type)) => match &*pat_type.pat {
                Pat::Ident(pat_ident) => Ok(&pat_ident.ident),
                Pat::Wild(wild) => Err(syn::Error::new_spanned(
                    wild,
                    "The context argument cannot be anonymous `_`, please use a named identifier",
                )),
                _ => Err(syn::Error::new_spanned(
                    &pat_type.pat,
                    "expected identifier as second argument (context)",
                )),
            },
            _ => Err(syn::Error::new_spanned(
                &sig.inputs,
                "expected context as second argument",
            )),
        },
        _ => Err(syn::Error::new_spanned(
            &sig.inputs,
            "expected self as first argument for method",
        )),
    }
}
fn is_context_type(ty: &Type) -> bool {
    if let Type::Reference(type_ref) = ty
        && let Type::Path(type_path) = &*type_ref.elem
    {
        let path: &Path = &type_path.path;
        if path.segments.len() >= 2 {
            let segments: Vec<_> = path.segments.iter().collect();
            if segments.len() >= 2 {
                let last_two: &[&PathSegment] = &segments[segments.len() - 2..];
                if last_two[0].ident == "hyperlane" && last_two[1].ident == "Context" {
                    return true;
                }
            }
        }
        if path.segments.len() == 1 && path.segments[0].ident == "Context" {
            return true;
        }
    }
    false
}
pub(crate) fn parse_context_from_signature(sig: &Signature) -> syn::Result<&Ident> {
    for arg in sig.inputs.iter() {
        if let FnArg::Typed(pat_type) = arg
            && is_context_type(&pat_type.ty)
        {
            match &*pat_type.pat {
                Pat::Ident(pat_ident) => return Ok(&pat_ident.ident),
                Pat::Wild(wild) => {
                    return Err(syn::Error::new_spanned(
                        wild,
                        "The context argument cannot be anonymous `_`, please use a named identifier",
                    ));
                }
                _ => {
                    return Err(syn::Error::new_spanned(
                        &pat_type.pat,
                        "expected identifier for context parameter",
                    ));
                }
            }
        }
    }
    Err(syn::Error::new_spanned(
        &sig.inputs,
        "expected at least one parameter of type &::hyperlane::Context",
    ))
}
pub(crate) fn expr_to_isize(opt_expr: &Option<Expr>) -> TokenStream2 {
    match opt_expr {
        Some(expr) => match expr {
            Expr::Lit(ExprLit {
                lit: Lit::Int(lit_int),
                ..
            }) => {
                let value: isize = lit_int.base10_parse::<isize>().unwrap();
                quote! { Some(#value) }
            }
            Expr::Lit(ExprLit {
                lit: Lit::Str(lit_str),
                ..
            }) => {
                let value: isize = lit_str.value().parse().expect("Cannot parse to isize");
                quote! { Some(#value) }
            }
            _ => quote! { None },
        },
        None => quote! { None },
    }
}
pub(crate) fn is_integer_literal(expr: &Expr) -> bool {
    if matches!(
        expr,
        Expr::Lit(ExprLit {
            lit: Lit::Int(_),
            ..
        })
    ) {
        return true;
    }
    if let Expr::Call(ExprCall { func, .. }) = expr {
        if let Expr::Path(ExprPath { path, .. }) = &**func {
            if path.segments.len() == 2 {
                let first = &path.segments[0];
                let second = &path.segments[1];
                if first.ident == "RequestConfig" && second.ident == "default" {
                    return true;
                }
            }
        }
    }
    false
}
```
# Path: hyperlane-macros/src/common/impl.rs
```rust
use crate::*;
impl Parse for OrderAttr {
    fn parse(input: ParseStream) -> Result<Self> {
        if input.is_empty() {
            return Ok(OrderAttr { order: None });
        }
        let expr: Expr = input.parse()?;
        Ok(OrderAttr { order: Some(expr) })
    }
}
```
# Path: hyperlane-macros/src/common/type.rs
```rust
use crate::*;
pub(crate) type MacroHandlerPosition = fn(TokenStream, Position) -> TokenStream;
pub(crate) type MacroHandlerWithAttr = fn(TokenStream, TokenStream) -> TokenStream;
pub(crate) type MacroHandlerWithAttrPosition =
    fn(TokenStream, TokenStream, Position) -> TokenStream;
```
# Path: hyperlane-macros/src/send/mod.rs
```rust
mod r#fn;
mod r#impl;
mod r#struct;
pub(crate) use r#fn::*;
pub(crate) use r#struct::*;
```
# Path: hyperlane-macros/src/send/struct.rs
```rust
use crate::*;
pub(crate) struct ResponseHeaderData {
    pub(crate) key: Expr,
    pub(crate) value: Expr,
    pub(crate) operation: HeaderOperation,
}
pub(crate) struct ResponseBodyData {
    pub(crate) body: Expr,
}
```
# Path: hyperlane-macros/src/send/fn.rs
```rust
use crate::*;
pub(crate) fn try_send_macro(item: TokenStream, position: Position) -> TokenStream {
    inject(position, item, |context| {
        quote! {
            let _ = #context.try_send().await;
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "try_send",
        handler: Handler::NoAttrPosition(try_send_macro),
    }
}
pub(crate) fn send_macro(item: TokenStream, position: Position) -> TokenStream {
    inject(position, item, |context| {
        quote! {
            #context.send().await;
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "send",
        handler: Handler::NoAttrPosition(send_macro),
    }
}
pub(crate) fn try_send_body_macro(item: TokenStream, position: Position) -> TokenStream {
    inject(position, item, |context| {
        quote! {
            let _ = #context.try_send_body().await;
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "try_send_body",
        handler: Handler::NoAttrPosition(try_send_body_macro),
    }
}
pub(crate) fn send_body_macro(item: TokenStream, position: Position) -> TokenStream {
    inject(position, item, |context| {
        quote! {
            #context.send_body().await;
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "send_body",
        handler: Handler::NoAttrPosition(send_body_macro),
    }
}
pub(crate) fn try_send_body_with_data_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let send_data: SendData = parse_macro_input!(attr as SendData);
    let data: Expr = send_data.data;
    inject(position, item, |context| {
        quote! {
            let _ = #context.try_send_body_with_data(#data).await;
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "try_send_body_with_data",
        handler: Handler::WithAttrPosition(try_send_body_with_data_macro),
    }
}
pub(crate) fn send_body_with_data_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let send_data: SendData = parse_macro_input!(attr as SendData);
    let data: Expr = send_data.data;
    inject(position, item, |context| {
        quote! {
            #context.send_body_with_data(#data).await;
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "send_body_with_data",
        handler: Handler::WithAttrPosition(send_body_with_data_macro),
    }
}
```
# Path: hyperlane-macros/src/send/impl.rs
```rust
use crate::*;
impl Parse for SendData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let data: Expr = input.parse()?;
        Ok(SendData { data })
    }
}
```
# Path: hyperlane-macros/src/filter/mod.rs
```rust
mod r#fn;
pub(crate) use r#fn::*;
```
# Path: hyperlane-macros/src/filter/fn.rs
```rust
use crate::*;
pub(crate) fn filter_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let condition: Expr = parse_macro_input!(attr as Expr);
    inject(position, item, |_| {
        quote! {
            if !(#condition) {
                return;
            }
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "filter",
        handler: Handler::WithAttrPosition(filter_macro),
    }
}
```
# Path: hyperlane-macros/src/reject/mod.rs
```rust
mod r#fn;
pub(crate) use r#fn::*;
```
# Path: hyperlane-macros/src/reject/fn.rs
```rust
use crate::*;
pub(crate) fn reject_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let condition: Expr = parse_macro_input!(attr as Expr);
    inject(position, item, |_| {
        quote! {
            if #condition {
                return;
            }
        }
    })
}
inventory::submit! {
    InjectableMacro {
        name: "reject",
        handler: Handler::WithAttrPosition(reject_macro),
    }
}
```
# Path: hyperlane-macros/src/response_middleware/mod.rs
```rust
pub(crate) mod r#fn;
pub(crate) use r#fn::*;
```
# Path: hyperlane-macros/src/response_middleware/fn.rs
```rust
use crate::*;
pub(crate) fn response_middleware_macro(attr: TokenStream, item: TokenStream) -> TokenStream {
    let attr_args: OrderAttr = parse_macro_input!(attr as OrderAttr);
    let order: TokenStream2 = expr_to_isize(&attr_args.order);
    let input_struct: ItemStruct = parse_macro_input!(item as ItemStruct);
    let struct_name: &Ident = &input_struct.ident;
    let gen_code: TokenStream2 = quote! {
        #input_struct
        ::hyperlane::inventory::submit! {
            ::hyperlane::HookType::ResponseMiddleware(#order, || ::hyperlane::server_hook_factory::<#struct_name>())
        }
    };
    gen_code.into()
}
inventory::submit! {
    InjectableMacro {
        name: "response_middleware",
        handler: Handler::WithAttr(response_middleware_macro),
    }
}
```
# Path: hyperlane-macros/src/route/mod.rs
```rust
pub(crate) mod r#fn;
pub(crate) mod r#impl;
pub(crate) mod r#struct;
pub(crate) use r#fn::*;
pub(crate) use r#struct::*;
```
# Path: hyperlane-macros/src/route/struct.rs
```rust
use crate::*;
pub(crate) struct RouteAttr {
    pub(crate) path: Expr,
}
```
# Path: hyperlane-macros/src/route/fn.rs
```rust
use crate::*;
pub(crate) fn route_macro(attr: TokenStream, item: TokenStream) -> TokenStream {
    let route_attr: RouteAttr = parse_macro_input!(attr as RouteAttr);
    let path: &Expr = &route_attr.path;
    let input_struct: ItemStruct = parse_macro_input!(item as ItemStruct);
    let struct_name: &Ident = &input_struct.ident;
    let gen_code: TokenStream2 = quote! {
        #input_struct
        ::hyperlane::inventory::submit! {
            ::hyperlane::HookType::Route(#path, || ::hyperlane::server_hook_factory::<#struct_name>())
        }
    };
    gen_code.into()
}
inventory::submit! {
    InjectableMacro {
        name: "route",
        handler: Handler::WithAttr(route_macro),
    }
}
```
# Path: hyperlane-macros/src/route/impl.rs
```rust
use crate::*;
impl Parse for RouteAttr {
    fn parse(input: ParseStream) -> Result<Self> {
        let first_expr: Expr = input.parse()?;
        Ok(RouteAttr { path: first_expr })
    }
}
```
# Path: hyperlane-macros/src/http/mod.rs
```rust
mod r#fn;
pub(crate) use r#fn::*;
```
# Path: hyperlane-macros/src/http/fn.rs
```rust
use crate::*;
macro_rules! impl_http_method_macro {
    ($name:ident, $method:expr) => {
        pub(crate) fn $name(item: TokenStream, position: Position) -> TokenStream {
            inject(
                position,
                item,
                create_method_check($method, proc_macro2::Span::call_site()),
            )
        }
        inventory::submit! {
            InjectableMacro {
                name: $method,
                handler: Handler::NoAttrPosition($name),
            }
        }
    };
}
impl_http_method_macro!(get_handler, "get");
impl_http_method_macro!(post_handler, "post");
impl_http_method_macro!(put_handler, "put");
impl_http_method_macro!(delete_handler, "delete");
impl_http_method_macro!(patch_handler, "patch");
impl_http_method_macro!(head_handler, "head");
impl_http_method_macro!(options_handler, "options");
impl_http_method_macro!(connect_handler, "connect");
impl_http_method_macro!(trace_handler, "trace");
pub(crate) fn create_method_check(
    method_name: &str,
    span: proc_macro2::Span,
) -> impl FnOnce(&Ident) -> TokenStream2 {
    let check_method: Ident = Ident::new(&format!("is_{method_name}"), span);
    move |context| {
        quote! {
            if !#context.get_request().await.#check_method() {
                return;
            }
        }
    }
}
pub(crate) fn methods_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let item_clone_1: TokenStream = item.clone();
    let methods: RequestMethods = parse_macro_input!(attr as RequestMethods);
    let input_fn: ItemFn = parse_macro_input!(item as ItemFn);
    let sig: &Signature = &input_fn.sig;
    match parse_context_from_signature(sig) {
        Ok(context) => {
            let method_checks = methods.methods.iter().map(|method| {
                let check_fn: Ident = Ident::new(&format!("is_{method}"), method.span());
                quote! {
                    #context.get_request().await.#check_fn()
                }
            });
            inject(position, item_clone_1, |_| {
                quote! {
                    if !(#(#method_checks)||*) {
                        return;
                    }
                }
            })
        }
        Err(err) => err.to_compile_error().into(),
    }
}
inventory::submit! {
    InjectableMacro {
        name: "methods",
        handler: Handler::WithAttrPosition(methods_macro),
    }
}
```
