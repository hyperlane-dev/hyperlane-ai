# Path: hyperlane\README.md


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

## Use

```rust
use hyperlane::*;

struct UpgradeMiddleware;
struct SendBodyMiddleware {
    socket_addr: String,
}
struct ResponseMiddleware;
struct ServerPanicHook {
    response_body: String,
    content_type: String,
}
struct RootRoute {
    response_body: String,
    cookie1: String,
    cookie2: String,
}
struct SseRoute;
struct WebsocketRoute;
struct DynamicRoute {
    params: RouteParams,
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
                .await
                .unwrap();
        }
    }
}

impl ServerHook for ResponseMiddleware {
    async fn new(_ctx: &Context) -> Self {
        Self
    }

    async fn handle(self, ctx: &Context) {
        if ctx.get_request().await.is_ws() {
            return;
        }
        let _ = ctx.send().await;
    }
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

impl WebsocketRoute {
    async fn send_body_hook(&self, ctx: &Context) {
        let body: ResponseBody = ctx.get_response_body().await;
        if ctx.get_request().await.is_ws() {
            let frame_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(&body);
            ctx.send_body_list_with_data(&frame_list).await.unwrap();
        } else {
            ctx.send_body().await.unwrap();
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
                Err(err) => {
                    ctx.set_response_body(&err.to_string()).await;
                    self.send_body_hook(ctx).await;
                    break;
                }
            }
        }
    }
}

impl ServerHook for SseRoute {
    async fn new(_ctx: &Context) -> Self {
        Self
    }

    async fn handle(self, ctx: &Context) {
        let _ = ctx
            .set_response_header(CONTENT_TYPE, TEXT_EVENT_STREAM)
            .await
            .send()
            .await;
        for i in 0..10 {
            let _ = ctx
                .set_response_body(&format!("data:{}{}", i, HTTP_DOUBLE_BR))
                .await
                .send_body()
                .await;
        }
        let _ = ctx.closed().await;
    }
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

impl ServerHook for ServerPanicHook {
    async fn new(ctx: &Context) -> Self {
        let error: Panic = ctx.try_get_panic().await.unwrap_or_default();
        let response_body: String = error.to_string();
        let content_type: String =
            ContentType::format_content_type_with_charset(TEXT_PLAIN, UTF8);
        Self {
            response_body,
            content_type,
        }
    }

    async fn handle(self, ctx: &Context) {
        let _ = ctx
            .set_response_version(HttpVersion::Http1_1)
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

async fn main() {
    let config: ServerConfig = ServerConfig::new().await;
    config.host("0.0.0.0").await;
    config.port(60000).await;
    config.request_config(RequestConfig::default()).await;
    config.disable_linger().await;
    config.disable_nodelay().await;
    let server: Server = Server::from(config).await;
    server.request_middleware::<SendBodyMiddleware>().await;
    server.request_middleware::<UpgradeMiddleware>().await;
    server.response_middleware::<ResponseMiddleware>().await;
    server.panic_hook::<ServerPanicHook>().await;
    server.route::<RootRoute>("/").await;
    server.route::<WebsocketRoute>("/websocket").await;
    server.route::<SseRoute>("/sse").await;
    server.route::<DynamicRoute>("/dynamic/{routing}").await;
    server.route::<DynamicRoute>("/regex/{file:^.*$}").await;
    let server_control_hook: ServerControlHook = server.run().await.unwrap_or_default();
    server_control_hook.wait().await;
}
```

## Contact


# Path: hyperlane\src\lib.rs

```rust
//! hyperlane
//!
//! A lightweight, high-performance, and cross-platform
//! Rust HTTP server library built on Tokio. It simplifies
//! modern web service development by providing built-in
//! support for middleware, WebSocket, Server-Sent Events (SSE),
//! and raw TCP communication. With a unified and ergonomic API
//! across Windows, Linux, and MacOS, it enables developers to
//! build robust, scalable, and event-driven network
//! applications with minimal overhead and maximum flexibility.

mod attribute;
mod config;
mod context;
mod error;
mod hook;
mod lifecycle;
mod panic;
mod route;
mod server;
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

pub(crate) use lifecycle::*;

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
    time::Duration,
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
pub(crate) use std::time::Instant;

```

# Path: hyperlane\src\attribute\enum.rs

```rust
use crate::*;

/// Represents the key for an attribute.
///
/// Attributes can be either external, defined by a user-provided string,
/// or internal, representing framework-specific functionality.
#[derive(CustomDebug, Clone, PartialEq, Eq, Hash, DisplayDebug)]
pub(crate) enum Attribute {
    /// An external attribute identified by a string.
    External(String),
    /// An internal attribute with a predefined key.
    Internal(InternalAttribute),
}

/// Defines keys for internal attributes used by the framework.
///
/// These keys correspond to specific, built-in functionalities.
#[derive(CustomDebug, Clone, PartialEq, Eq, Hash, DisplayDebug)]
pub(crate) enum InternalAttribute {
    /// The attribute key for panic handling.
    Panic,
    /// The attribute key for hook functions with a custom identifier.
    Hook(String),
}

```

# Path: hyperlane\src\attribute\impl.rs

```rust
use crate::*;

/// Implementation of `From` trait for `Attribute`.
impl From<&str> for Attribute {
    /// Converts a string slice into an `Attribute`.
    ///
    /// # Arguments
    ///
    /// - `&str` - The string slice to convert.
    ///
    /// # Returns
    ///
    /// - `Attribute` - The converted attribute key.
    #[inline(always)]
    fn from(key: &str) -> Self {
        Attribute::External(key.to_string())
    }
}

/// Implementation of `From` trait for `Attribute`.
impl From<String> for Attribute {
    /// Converts a `String` into an `Attribute`.
    ///
    /// # Arguments
    ///
    /// - `String` - The string to convert.
    ///
    /// # Returns
    ///
    /// - `Attribute` - The converted attribute key.
    #[inline(always)]
    fn from(key: String) -> Self {
        Attribute::External(key)
    }
}

/// Implementation of `From` trait for `Attribute`.
impl From<InternalAttribute> for Attribute {
    /// Converts an `InternalAttribute` into an `Attribute`.
    ///
    /// # Arguments
    ///
    /// - `InternalAttribute` - The internal attribute key to convert.
    ///
    /// # Returns
    ///
    /// - `Attribute` - The converted attribute key.
    #[inline(always)]
    fn from(key: InternalAttribute) -> Self {
        Attribute::Internal(key)
    }
}

```

# Path: hyperlane\src\attribute\mod.rs

```rust
pub(crate) mod r#enum;
pub(crate) mod r#impl;
pub(crate) mod r#type;

pub use r#type::*;

pub(crate) use r#enum::*;

```

# Path: hyperlane\src\attribute\type.rs

```rust
use crate::*;

/// A type alias for a thread-safe attribute storage.
///
/// This type is used for storing attributes that can be safely shared across threads.
pub type ThreadSafeAttributeStore = HashMap<String, ArcAnySendSync>;

```

# Path: hyperlane\src\config\impl.rs

```rust
use crate::*;

/// Implements the `Default` trait for `ServerConfigInner`.
///
/// This provides a default configuration for the server with predefined values.
impl Default for ServerConfigInner {
    /// Creates a default `ServerConfigInner`.
    ///
    /// # Returns
    ///
    /// - `Self` - A `ServerConfigInner` instance with default settings.
    #[inline(always)]
    fn default() -> Self {
        Self {
            host: DEFAULT_HOST.to_owned(),
            port: DEFAULT_WEB_PORT,
            request_config: RequestConfig::default(),
            nodelay: DEFAULT_NODELAY,
            linger: DEFAULT_LINGER,
            ttl: DEFAULT_TTI,
        }
    }
}

/// Implements the `Default` trait for `ServerConfig`.
///
/// This wraps the default `ServerConfigInner` in an `Arc<RwLock>`.
impl Default for ServerConfig {
    /// Creates a default `ServerConfig`.
    ///
    /// # Returns
    ///
    /// - `Self` - A `ServerConfig` instance with default settings.
    #[inline(always)]
    fn default() -> Self {
        Self(arc_rwlock(ServerConfigInner::default()))
    }
}

/// Implements the `PartialEq` trait for `ServerConfig`.
///
/// This allows for comparing two `ServerConfig` instances for equality.
impl PartialEq for ServerConfig {
    /// Checks if two `ServerConfig` instances are equal.
    ///
    /// It first checks for pointer equality for performance. If the pointers are not equal,
    /// it compares the inner `ServerConfigInner` values.
    ///
    /// # Arguments
    ///
    /// - `&Self`- The other `ServerConfig` to compare against.
    ///
    /// # Returns
    ///
    /// - `bool` - Indicating whether the configurations are equal.
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

/// Implements the `Eq` trait for `ServerConfig`.
///
/// This indicates that `ServerConfig` has a total equality relation.
impl Eq for ServerConfig {}

/// Implementation block for `ServerConfig`.
impl ServerConfig {
    /// Creates a new `ServerConfig` with default values.
    ///
    /// # Returns
    ///
    /// - `Self` - A new `ServerConfig` instance.
    #[inline(always)]
    pub async fn new() -> Self {
        Self::default()
    }

    /// Acquires a read lock on the server configuration.
    ///
    /// # Returns
    ///
    /// - `ConfigReadGuard` - A `ConfigReadGuard` for the inner configuration.
    async fn read(&self) -> ConfigReadGuard<'_> {
        self.get_0().read().await
    }

    /// Acquires a write lock on the server configuration.
    ///
    /// # Returns
    ///
    /// - `ConfigWriteGuard` - A `ConfigWriteGuard` for the inner configuration.
    async fn write(&self) -> ConfigWriteGuard<'_> {
        self.get_0().write().await
    }

    /// Retrieves a clone of the inner server configuration.
    ///
    /// This function provides a snapshot of the current configuration by acquiring a read lock
    /// and cloning the inner `ServerConfigInner`.
    ///
    /// # Returns
    ///
    /// - `ServerConfigInner` - A `ServerConfigInner` instance containing the current server configuration.
    pub(crate) async fn get_inner(&self) -> ServerConfigInner {
        self.read().await.clone()
    }

    /// Sets the host address for the server.
    ///
    /// # Arguments
    ///
    /// - `H`- The host address to set.
    ///
    /// # Returns
    ///
    /// - `&Self` - A reference to `Self` for method chaining.
    pub async fn host<H: ToString>(&self, host: H) -> &Self {
        self.write().await.set_host(host.to_string());
        self
    }

    /// Sets the port for the server.
    ///
    /// # Arguments
    ///
    /// - `u16`- The port number to set.
    ///
    /// # Returns
    ///
    /// - `&Self` - A reference to `Self` for method chaining.
    pub async fn port(&self, port: u16) -> &Self {
        self.write().await.set_port(port);
        self
    }

    /// Sets the HTTP request config.
    ///
    /// # Arguments
    ///
    /// - `RequestConfig`- The HTTP request config to set.
    ///
    /// # Returns
    ///
    /// - `&Self` - A reference to `Self` for method chaining.
    pub async fn request_config(&self, request_config: RequestConfig) -> &Self {
        self.write().await.set_request_config(request_config);
        self
    }

    /// Sets the `TCP_NODELAY` option.
    ///
    /// # Arguments
    ///
    /// - `bool`- The `bool` value for `TCP_NODELAY`.
    ///
    /// # Returns
    ///
    /// - `&Self` - A reference to `Self` for method chaining.
    pub async fn nodelay(&self, nodelay: bool) -> &Self {
        self.write().await.set_nodelay(Some(nodelay));
        self
    }

    /// Enables the `TCP_NODELAY` option.
    ///
    /// # Returns
    ///
    /// - `&Self` - A reference to `Self` for method chaining.
    pub async fn enable_nodelay(&self) -> &Self {
        self.nodelay(true).await
    }

    /// Disables the `TCP_NODELAY` option.
    ///
    /// # Returns
    ///
    /// - `&Self` - A reference to `Self` for method chaining.
    pub async fn disable_nodelay(&self) -> &Self {
        self.nodelay(false).await
    }

    /// Sets the `SO_LINGER` option.
    ///
    /// # Arguments
    ///
    /// - `Option<Duration>`- The `Duration` value for `SO_LINGER`.
    ///
    /// # Returns
    ///
    /// - `&Self` - A reference to `Self` for method chaining.
    pub async fn linger(&self, linger_opt: Option<Duration>) -> &Self {
        self.write().await.set_linger(linger_opt);
        self
    }

    /// Enables the `SO_LINGER` option.
    ///
    /// # Arguments
    ///
    /// - `Duration`- The `Duration` value for `SO_LINGER`.
    ///
    /// # Returns
    ///
    /// - `&Self` - A reference to `Self` for method chaining.
    pub async fn enable_linger(&self, linger: Duration) -> &Self {
        self.linger(Some(linger)).await;
        self
    }

    /// Disables the `SO_LINGER` option.
    ///
    /// # Returns
    ///
    /// - `&Self` - A reference to `Self` for method chaining.
    pub async fn disable_linger(&self) -> &Self {
        self.linger(None).await;
        self
    }

    /// Sets the `IP_TTL` option.
    ///
    /// # Arguments
    ///
    /// - `u32`- The `u32` value for `IP_TTL`.
    ///
    /// # Returns
    ///
    /// - `&Self` - A reference to `Self` for method chaining.
    pub async fn ttl(&self, ttl: u32) -> &Self {
        self.write().await.set_ttl(Some(ttl));
        self
    }

    /// Creates a `ServerConfig` from a JSON string.
    ///
    /// # Arguments
    ///
    /// - `&str`- The JSON string to parse.
    ///
    /// # Returns
    ///
    /// - `Result<ServerConfig, serde_json::Error>` - A `Result<ServerConfig, serde_json::Error>` which is a `Result` containing either the `ServerConfig` or a `serde_json::Error`.
    ///   Creates a `ServerConfig` from a JSON string.
    ///
    /// # Arguments
    ///
    /// - `config_str` - The JSON string to parse.
    ///
    /// # Returns
    ///
    /// - `Result<ServerConfig, serde_json::Error>` - A `Result<ServerConfig, serde_json::Error>` which is a `Result` containing either the `ServerConfig` or a `serde_json::Error`.
    pub fn from_json_str(config_str: &str) -> Result<ServerConfig, serde_json::Error> {
        serde_json::from_str(config_str).map(|config: ServerConfigInner| Self(arc_rwlock(config)))
    }
}

```

# Path: hyperlane\src\config\mod.rs

```rust
pub(crate) mod r#impl;
pub(crate) mod r#struct;
pub(crate) mod r#type;

pub use r#struct::*;

pub(super) use r#type::*;

```

# Path: hyperlane\src\config\struct.rs

```rust
use crate::*;

/// Represents the inner, mutable server configuration.
///
/// This structure holds all the settings for the HTTP and WebSocket server,
/// including network parameters and buffer sizes. It is not intended to be used directly
/// by end-users, but rather through the `ServerConfig` wrapper.
#[derive(Clone, Data, CustomDebug, DisplayDebug, PartialEq, Eq, Deserialize, Serialize)]
pub(crate) struct ServerConfigInner {
    /// The host address the server will bind to.
    #[get(pub(crate))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    pub(super) host: String,
    /// The port number the server will listen on.
    #[get(pub(crate))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    pub(super) port: u16,
    /// The configuration for HTTP request.
    #[get(pub(crate))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    pub(super) request_config: RequestConfig,
    /// The `TCP_NODELAY` option for sockets.
    #[get(pub(crate))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    pub(super) nodelay: Option<bool>,
    /// The `SO_LINGER` option for sockets.
    #[get(pub(crate))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    pub(super) linger: Option<Duration>,
    /// The `IP_TTL` option for sockets.
    #[get(pub(crate))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    pub(super) ttl: Option<u32>,
}

/// Represents the thread-safe, shareable server configuration.
///
/// This structure wraps `ServerConfigInner` in an `Arc<RwLock<ServerConfigInner>>`
/// to allow for safe concurrent access and modification of the server settings.
#[derive(Clone, Getter, CustomDebug, DisplayDebug)]
pub struct ServerConfig(#[get(pub(super))] pub(super) SharedServerConfig);

```

# Path: hyperlane\src\config\type.rs

```rust
use crate::*;

/// A type alias for configuration read guard.
///
/// This provides read-only access to the `ServerConfigInner` wrapped in a `RwLock`.
pub(crate) type ConfigReadGuard<'a> = RwLockReadGuard<'a, ServerConfigInner>;

/// A type alias for configuration write guard.
///
/// This provides mutable access to the `ServerConfigInner` wrapped in a `RwLock`.
pub(crate) type ConfigWriteGuard<'a> = RwLockWriteGuard<'a, ServerConfigInner>;

```

# Path: hyperlane\src\context\impl.rs

```rust
use crate::*;

/// Implementation of `From` trait for `Context`.
impl From<ContextInner> for Context {
    /// Converts a `ContextInner` into a `Context`.
    ///
    /// # Arguments
    ///
    /// - `ContextInner` - The wrapped context data.
    ///
    /// # Returns
    ///
    /// - `Context` - The newly created context instance.
    #[inline(always)]
    fn from(ctx: ContextInner) -> Self {
        Self(arc_rwlock(ctx))
    }
}

/// Implementation of methods for `Context` structure.
impl Context {
    /// Creates a new `Context` with the provided network stream and HTTP request.
    ///
    /// # Arguments
    ///
    /// - `&ArcRwLockStream` - The network stream.
    /// - `&Request` - The HTTP request.
    ///
    /// # Returns
    ///
    /// - `Context` - The newly created context.
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

    /// Acquires a read lock on the inner context data.
    ///
    /// # Returns
    ///
    /// - `ContextReadGuard` - The read guard for the inner context.
    async fn read(&self) -> ContextReadGuard<'_> {
        self.get_0().read().await
    }

    /// Acquires a write lock on the inner context data.
    ///
    /// # Returns
    ///
    /// - `ContextWriteGuard` - The write guard for the inner context.
    async fn write(&self) -> ContextWriteGuard<'_> {
        self.get_0().write().await
    }

    /// Checks if the context has been marked as aborted.
    ///
    /// # Returns
    ///
    /// - `bool` - True if the context is aborted, otherwise false.
    pub async fn get_aborted(&self) -> bool {
        *self.read().await.get_aborted()
    }

    /// Sets the aborted flag for the context.
    ///
    /// # Arguments
    ///
    /// - `bool` - The aborted state to set.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to self for method chaining.
    pub async fn set_aborted(&self, aborted: bool) -> &Self {
        self.write().await.set_aborted(aborted);
        self
    }

    /// Marks the context as aborted.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to the modified context.
    pub async fn aborted(&self) -> &Self {
        self.set_aborted(true).await;
        self
    }

    /// Cancels the aborted state of the context.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to the modified context.
    pub async fn cancel_aborted(&self) -> &Self {
        self.set_aborted(false).await;
        self
    }

    /// Checks if the connection is marked as closed.
    ///
    /// # Returns
    ///
    /// - `bool` - True if the connection is closed, otherwise false.
    pub async fn get_closed(&self) -> bool {
        *self.read().await.get_closed()
    }

    /// Sets the closed flag for the connection.
    ///
    /// # Arguments
    ///
    /// - `bool` - The new value for the closed flag.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to the modified context.
    pub async fn set_closed(&self, closed: bool) -> &Self {
        self.write().await.set_closed(closed);
        self
    }

    /// Marks the connection as closed.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to the modified context.
    pub async fn closed(&self) -> &Self {
        self.set_closed(true).await;
        self
    }

    /// Cancels the closed state of the connection.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to the modified context.
    pub async fn cancel_closed(&self) -> &Self {
        self.set_closed(false).await;
        self
    }

    /// Checks if the connection has been terminated (aborted or closed).
    ///
    /// # Returns
    ///
    /// - `bool` - True if the connection is both aborted and closed, otherwise false.
    pub async fn is_terminated(&self) -> bool {
        self.get_aborted().await || self.get_closed().await
    }

    /// Retrieves the underlying network stream, if available.
    ///
    /// # Returns
    ///
    /// - `Option<ArcRwLockStream>` - The thread-safe, shareable network stream if it exists.
    pub async fn try_get_stream(&self) -> Option<ArcRwLockStream> {
        self.read().await.get_stream().clone()
    }

    /// Retrieves the underlying network stream.
    ///
    /// # Returns
    ///
    /// - `ArcRwLockStream` - The thread-safe, shareable network stream.
    ///
    /// # Panics
    ///
    /// - If the network stream is not found.
    pub async fn get_stream(&self) -> ArcRwLockStream {
        self.try_get_stream().await.unwrap()
    }

    /// Retrieves the remote socket address of the connection.
    ///
    /// # Returns
    ///
    /// - `Option<SocketAddr>` - The socket address of the remote peer if available.
    pub async fn try_get_socket_addr(&self) -> Option<SocketAddr> {
        self.try_get_stream()
            .await
            .as_ref()?
            .read()
            .await
            .peer_addr()
            .ok()
    }

    /// Retrieves the remote socket address.
    ///
    /// # Returns
    ///
    /// - `SocketAddr` - The socket address of the remote peer.
    ///
    /// # Panics
    ///
    /// - If the socket address is not found.
    pub async fn get_socket_addr(&self) -> SocketAddr {
        self.try_get_socket_addr().await.unwrap()
    }

    /// Retrieves the remote socket address as a string.
    ///
    /// # Returns
    ///
    /// - `Option<String>` - The string representation of the socket address if available.
    pub async fn try_get_socket_addr_string(&self) -> Option<String> {
        self.try_get_socket_addr()
            .await
            .map(|data| data.to_string())
    }

    /// Retrieves the remote socket address as a string.
    ///
    /// # Returns
    ///
    /// - `String` - The string representation of the socket address.
    ///
    /// # Panics
    ///
    /// - If the socket address is not found.
    pub async fn get_socket_addr_string(&self) -> String {
        self.get_socket_addr().await.to_string()
    }

    /// Retrieves the IP address part of the remote socket address.
    ///
    /// # Returns
    ///
    /// - `Option<SocketHost>` - The IP address of the remote peer.
    pub async fn try_get_socket_host(&self) -> Option<SocketHost> {
        self.try_get_socket_addr()
            .await
            .map(|socket_addr: SocketAddr| socket_addr.ip())
    }

    /// Retrieves the IP address part of the remote socket address.
    ///
    /// # Returns
    ///
    /// - `SocketHost` - The IP address of the remote peer.
    ///
    /// # Panics
    ///
    /// - If the socket address is not found.
    pub async fn get_socket_host(&self) -> SocketHost {
        self.try_get_socket_host().await.unwrap()
    }

    /// Retrieves the port number part of the remote socket address.
    ///
    /// # Returns
    ///
    /// - `Option<SocketPort>` - The port number of the remote peer if available.
    pub async fn try_get_socket_port(&self) -> Option<SocketPort> {
        self.try_get_socket_addr()
            .await
            .map(|socket_addr: SocketAddr| socket_addr.port())
    }

    /// Retrieves the port number part of the remote socket address.
    ///
    /// # Returns
    ///
    /// - `SocketPort` - The port number of the remote peer.
    ///
    /// # Panics
    ///
    /// - If the socket address is not found.
    pub async fn get_socket_port(&self) -> SocketPort {
        self.try_get_socket_port().await.unwrap()
    }

    /// Retrieves the current HTTP request.
    ///
    /// # Returns
    ///
    /// - `Request` - A clone of the current request.
    pub async fn get_request(&self) -> Request {
        self.read().await.get_request().clone()
    }

    /// Sets the current HTTP request for the context.
    ///
    /// # Arguments
    ///
    /// - `&Request` - The request to set in the context.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to the modified context.
    pub(crate) async fn set_request(&self, request_data: &Request) -> &Self {
        self.write().await.set_request(request_data.clone());
        self
    }

    /// Executes an asynchronous closure with the current request.
    ///
    /// This method provides temporary access to the request data without needing to clone it.
    ///
    /// # Arguments
    ///
    /// - `F` - A closure that takes the `Request` and returns a future.
    ///
    /// # Returns
    ///
    /// - `R` - The result of the provided closure's future.
    pub async fn with_request<F, Fut, R>(&self, func: F) -> R
    where
        F: Fn(Request) -> Fut,
        Fut: FutureSendStatic<R>,
    {
        func(self.read().await.get_request().clone()).await
    }

    /// Retrieves the string representation of the current request.
    ///
    /// # Returns
    ///
    /// - `String` - The full request as a string.
    pub async fn get_request_string(&self) -> String {
        self.read().await.get_request().get_string()
    }

    /// Retrieves the HTTP version of the request.
    ///
    /// # Returns
    ///
    /// - `RequestVersion` - The HTTP version of the request.
    pub async fn get_request_version(&self) -> RequestVersion {
        self.read().await.get_request().get_version().clone()
    }

    /// Retrieves the HTTP method of the request.
    ///
    /// # Returns
    ///
    /// - `RequestMethod` - The HTTP method of the request.
    pub async fn get_request_method(&self) -> RequestMethod {
        self.read().await.get_request().get_method().clone()
    }

    /// Retrieves the host from the request headers.
    ///
    /// # Returns
    ///
    /// - `RequestHost` - The host part of the request's URI.
    pub async fn get_request_host(&self) -> RequestHost {
        self.read().await.get_request().get_host().clone()
    }

    /// Retrieves the path of the request.
    ///
    /// # Returns
    ///
    /// - `RequestPath` - The path part of the request's URI.
    pub async fn get_request_path(&self) -> RequestPath {
        self.read().await.get_request().get_path().clone()
    }

    /// Retrieves the query parameters of the request.
    ///
    /// # Returns
    ///
    /// - `RequestQuerys` - A map containing the query parameters.
    pub async fn get_request_querys(&self) -> RequestQuerys {
        self.read().await.get_request().get_querys().clone()
    }

    /// Attempts to retrieve a specific query parameter by its key.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The query parameter key.
    ///
    /// # Returns
    ///
    /// - `Option<RequestQuerysValue>` - The query parameter value if exists.
    pub async fn try_get_request_query<K>(&self, key: K) -> Option<RequestQuerysValue>
    where
        K: AsRef<str>,
    {
        self.read().await.get_request().try_get_query(key)
    }

    /// Retrieves a specific query parameter by its key, panicking if not found.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The query parameter key.
    ///
    /// # Returns
    ///
    /// - `RequestQuerysValue` - The query parameter value if exists.
    ///
    /// # Panics
    ///
    /// - If the query parameter is not found.
    pub async fn get_request_query<K>(&self, key: K) -> RequestQuerysValue
    where
        K: AsRef<str>,
    {
        self.read().await.get_request().get_query(key)
    }

    /// Retrieves the body of the request.
    ///
    /// # Returns
    ///
    /// - `RequestBody` - A clone of the request's body.
    pub async fn get_request_body(&self) -> RequestBody {
        self.read().await.get_request().get_body().clone()
    }

    /// Retrieves the request body as a string.
    ///
    /// # Returns
    ///
    /// - `String` - The request body converted to a string.
    pub async fn get_request_body_string(&self) -> String {
        self.read().await.get_request().get_body_string()
    }

    /// Deserializes the request body from JSON into a specified type.
    ///
    /// # Returns
    ///
    /// - `Result<J, serde_json::Error>` - The deserialized type `J` or a JSON error.
    pub async fn try_get_request_body_json<J>(&self) -> Result<J, serde_json::Error>
    where
        J: DeserializeOwned,
    {
        self.read().await.get_request().try_get_body_json()
    }

    /// Deserializes the request body from JSON into a specified type, panicking if not found.
    ///
    /// # Returns
    ///
    /// - `J` - The deserialized type `J`.
    ///
    /// # Panics
    ///
    /// - If deserialization fails.
    pub async fn get_request_body_json<J>(&self) -> J
    where
        J: DeserializeOwned,
    {
        self.read().await.get_request().get_body_json()
    }

    /// Retrieves all request headers.
    ///
    /// # Returns
    ///
    /// - `RequestHeaders` - A clone of the request's header map.
    pub async fn get_request_headers(&self) -> RequestHeaders {
        self.read().await.get_request().get_headers().clone()
    }

    /// Retrieves the total number of request headers.
    ///
    /// # Returns
    ///
    /// - `usize` - The total number of headers in the request.
    pub async fn get_request_headers_length(&self) -> usize {
        self.read().await.get_request().get_headers_length()
    }

    /// Attempts to retrieve a specific request header by its key.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The header key.
    ///
    /// # Returns
    ///
    /// - `Option<RequestHeadersValue>` - The header values if exists.
    pub async fn try_get_request_header<K>(&self, key: K) -> Option<RequestHeadersValue>
    where
        K: AsRef<str>,
    {
        self.read().await.get_request().try_get_header(key)
    }

    /// Retrieves a specific request header by its key, panicking if not found.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The key of the header to retrieve.
    ///
    /// # Returns
    ///
    /// - `RequestHeadersValue` - The header values if exists.
    ///
    /// # Panics
    ///
    /// - If the header is not found.
    pub async fn get_request_header<K>(&self, key: K) -> RequestHeadersValue
    where
        K: AsRef<str>,
    {
        self.read().await.get_request().get_header(key)
    }

    /// Attempts to retrieve the first value of a specific request header.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The key of the header.
    ///
    /// # Returns
    ///
    /// - `Option<RequestHeadersValueItem>` - The first value of the header if it exists.
    pub async fn try_get_request_header_front<K>(&self, key: K) -> Option<RequestHeadersValueItem>
    where
        K: AsRef<str>,
    {
        self.read().await.get_request().try_get_header_front(key)
    }

    /// Retrieves the first value of a specific request header, panicking if not found.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The key of the header.
    ///
    /// # Returns
    ///
    /// - `RequestHeadersValueItem` - The first value of the header if it exists.
    ///
    /// # Panics
    ///
    /// - If the header is not found.
    pub async fn get_request_header_front<K>(&self, key: K) -> RequestHeadersValueItem
    where
        K: AsRef<str>,
    {
        self.read().await.get_request().get_header_front(key)
    }

    /// Attempts to retrieve the last value of a specific request header.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The key of the header.
    ///
    /// # Returns
    ///
    /// - `Option<RequestHeadersValueItem>` - The last value of the header if it exists.
    pub async fn try_get_request_header_back<K>(&self, key: K) -> Option<RequestHeadersValueItem>
    where
        K: AsRef<str>,
    {
        self.read().await.get_request().try_get_header_back(key)
    }

    /// Retrieves the last value of a specific request header, panicking if not found.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The key of the header.
    ///
    /// # Returns
    ///
    /// - `RequestHeadersValueItem` - The last value of the header if it exists.
    ///
    /// # Panics
    ///
    /// - If the header is not found.
    pub async fn get_request_header_back<K>(&self, key: K) -> RequestHeadersValueItem
    where
        K: AsRef<str>,
    {
        self.read().await.get_request().get_header_back(key)
    }

    /// Attempts to retrieve the number of values for a specific request header.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The key of the header.
    ///
    /// # Returns
    ///
    /// - `Option<usize>` - The number of values for the specified header if it exists.
    pub async fn try_get_request_header_len<K>(&self, key: K) -> Option<usize>
    where
        K: AsRef<str>,
    {
        self.read().await.get_request().try_get_header_length(key)
    }

    /// Retrieves the number of values for a specific request header.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The key of the header.
    ///
    /// # Returns
    ///
    /// - `usize` - The number of values for the specified header.
    ///
    /// # Panics
    ///
    /// - If the header is not found.
    pub async fn get_request_header_len<K>(&self, key: K) -> usize
    where
        K: AsRef<str>,
    {
        self.read().await.get_request().get_header_length(key)
    }

    /// Retrieves the total number of values across all request headers.
    ///
    /// # Returns
    ///
    /// - `usize` - The total count of all values in all headers.
    pub async fn get_request_headers_values_length(&self) -> usize {
        self.read().await.get_request().get_headers_values_length()
    }

    /// Checks if a specific request header exists.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The key of the header to check.
    ///
    /// # Returns
    ///
    /// - `bool` - True if the header exists, otherwise false.
    pub async fn get_request_has_header<K>(&self, key: K) -> bool
    where
        K: AsRef<str>,
    {
        self.read().await.get_request().has_header(key)
    }

    /// Checks if a request header has a specific value.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The header key.
    /// - `AsRef<str>` - The value to check.
    ///
    /// # Returns
    ///
    /// - `bool` - True if header contains the value.
    pub async fn get_request_has_header_value<K, V>(&self, key: K, value: V) -> bool
    where
        K: AsRef<str>,
        V: AsRef<str>,
    {
        self.read().await.get_request().has_header_value(key, value)
    }

    /// Parses and retrieves all cookies from the request headers.
    ///
    /// # Returns
    ///
    /// - `Cookies` - A map of cookies parsed from the request's Cookie header.
    pub async fn get_request_cookies(&self) -> Cookies {
        self.try_get_request_header_back(COOKIE)
            .await
            .map(|data| Cookie::parse(&data))
            .unwrap_or_default()
    }

    /// Attempts to retrieve a specific cookie by its name from the request.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The cookie name.
    ///
    /// # Returns
    ///
    /// - `Option<CookieValue>` - The cookie value if exists.
    pub async fn try_get_request_cookie<K>(&self, key: K) -> Option<CookieValue>
    where
        K: AsRef<str>,
    {
        self.get_request_cookies().await.get(key.as_ref()).cloned()
    }

    /// Retrieves a specific cookie by its name from the request, panicking if not found.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The cookie name.
    ///
    /// # Returns
    ///
    /// - `CookieValue` - The cookie value if exists.
    ///
    /// # Panics
    ///
    /// - If the cookie is not found.
    pub async fn get_request_cookie<K>(&self, key: K) -> CookieValue
    where
        K: AsRef<str>,
    {
        self.try_get_request_cookie(key).await.unwrap()
    }

    /// Retrieves the upgrade type of the request.
    ///
    /// # Returns
    ///
    /// - `UpgradeType` - The upgrade type of the request.
    pub async fn get_request_upgrade_type(&self) -> UpgradeType {
        self.read().await.get_request().get_upgrade_type()
    }

    /// Checks if the request is a WebSocket upgrade request.
    ///
    /// # Returns
    ///
    /// - `bool` - True if this is a WebSocket upgrade request.
    pub async fn get_request_is_ws(&self) -> bool {
        self.read().await.get_request().is_ws()
    }

    /// Checks if the request is an HTTP/2 cleartext (h2c) upgrade.
    ///
    /// # Returns
    ///
    /// - `bool` - True if this is an h2c upgrade request.
    pub async fn get_request_is_h2c(&self) -> bool {
        self.read().await.get_request().is_h2c()
    }

    /// Checks if the request is a TLS upgrade.
    ///
    /// # Returns
    ///
    /// - `bool` - True if this is a TLS upgrade request.
    pub async fn get_request_is_tls(&self) -> bool {
        self.read().await.get_request().is_tls()
    }

    /// Checks if the request has an unknown upgrade type.
    ///
    /// # Returns
    ///
    /// - `bool` - True if the upgrade type is unknown.
    pub async fn get_request_is_unknown_upgrade(&self) -> bool {
        self.read().await.get_request().is_unknown_upgrade()
    }

    /// Checks if the request HTTP version is HTTP/1.1 or higher.
    ///
    /// # Returns
    ///
    /// - `bool` - True if the version is HTTP/1.1 or higher.
    pub async fn get_request_is_http1_1_or_higher(&self) -> bool {
        self.read().await.get_request().is_http1_1_or_higher()
    }

    /// Checks if the request HTTP version is HTTP/0.9.
    ///
    /// # Returns
    ///
    /// - `bool` - True if the version is HTTP/0.9.
    pub async fn get_request_is_http0_9(&self) -> bool {
        self.read().await.get_request().is_http0_9()
    }

    /// Checks if the request HTTP version is HTTP/1.0.
    ///
    /// # Returns
    ///
    /// - `bool` - True if the version is HTTP/1.0.
    pub async fn get_request_is_http1_0(&self) -> bool {
        self.read().await.get_request().is_http1_0()
    }

    /// Checks if the request HTTP version is HTTP/1.1.
    ///
    /// # Returns
    ///
    /// - `bool` - True if the version is HTTP/1.1.
    pub async fn get_request_is_http1_1(&self) -> bool {
        self.read().await.get_request().is_http1_1()
    }

    /// Checks if the request HTTP version is HTTP/2.
    ///
    /// # Returns
    ///
    /// - `bool` - True if the version is HTTP/2.
    pub async fn get_request_is_http2(&self) -> bool {
        self.read().await.get_request().is_http2()
    }

    /// Checks if the request HTTP version is HTTP/3.
    ///
    /// # Returns
    ///
    /// - `bool` - True if the version is HTTP/3.
    pub async fn get_request_is_http3(&self) -> bool {
        self.read().await.get_request().is_http3()
    }

    /// Checks if the request has an unknown HTTP version.
    ///
    /// # Returns
    ///
    /// - `bool` - True if the version is unknown.
    pub async fn get_request_is_unknown_version(&self) -> bool {
        self.read().await.get_request().is_unknown_version()
    }

    /// Checks if the request uses HTTP protocol.
    ///
    /// # Returns
    ///
    /// - `bool` - True if the version belongs to HTTP family.
    pub async fn get_request_is_http(&self) -> bool {
        self.read().await.get_request().is_http()
    }

    /// Checks if the request method is GET.
    ///
    /// # Returns
    ///
    /// - `bool` - True if the method is GET.
    pub async fn get_request_is_get(&self) -> bool {
        self.read().await.get_request().is_get()
    }

    /// Checks if the request method is POST.
    ///
    /// # Returns
    ///
    /// - `bool` - True if the method is POST.
    pub async fn get_request_is_post(&self) -> bool {
        self.read().await.get_request().is_post()
    }

    /// Checks if the request method is PUT.
    ///
    /// # Returns
    ///
    /// - `bool` - True if the method is PUT.
    pub async fn get_request_is_put(&self) -> bool {
        self.read().await.get_request().is_put()
    }

    /// Checks if the request method is DELETE.
    ///
    /// # Returns
    ///
    /// - `bool` - True if the method is DELETE.
    pub async fn get_request_is_delete(&self) -> bool {
        self.read().await.get_request().is_delete()
    }

    /// Checks if the request method is PATCH.
    ///
    /// # Returns
    ///
    /// - `bool` - True if the method is PATCH.
    pub async fn get_request_is_patch(&self) -> bool {
        self.read().await.get_request().is_patch()
    }

    /// Checks if the request method is HEAD.
    ///
    /// # Returns
    ///
    /// - `bool` - True if the method is HEAD.
    pub async fn get_request_is_head(&self) -> bool {
        self.read().await.get_request().is_head()
    }

    /// Checks if the request method is OPTIONS.
    ///
    /// # Returns
    ///
    /// - `bool` - True if the method is OPTIONS.
    pub async fn get_request_is_options(&self) -> bool {
        self.read().await.get_request().is_options()
    }

    /// Checks if the request method is CONNECT.
    ///
    /// # Returns
    ///
    /// - `bool` - True if the method is CONNECT.
    pub async fn get_request_is_connect(&self) -> bool {
        self.read().await.get_request().is_connect()
    }

    /// Checks if the request method is TRACE.
    ///
    /// # Returns
    ///
    /// - `bool` - True if the method is TRACE.
    pub async fn get_request_is_trace(&self) -> bool {
        self.read().await.get_request().is_trace()
    }

    /// Checks if the request method is unknown.
    ///
    /// # Returns
    ///
    /// - `bool` - True if the method is unknown.
    pub async fn get_request_is_unknown_method(&self) -> bool {
        self.read().await.get_request().is_unknown_method()
    }

    /// Checks if the connection should be kept alive based on request headers.
    ///
    /// # Returns
    ///
    /// - `bool` - True if the Connection header suggests keeping the connection alive, otherwise false.
    pub async fn get_request_is_enable_keep_alive(&self) -> bool {
        self.read().await.get_request().is_enable_keep_alive()
    }

    /// Checks if keep-alive should be disabled for the request.
    ///
    /// # Returns
    ///
    /// - `bool` - True if keep-alive should be disabled.
    pub async fn get_request_is_disable_keep_alive(&self) -> bool {
        self.read().await.get_request().is_disable_keep_alive()
    }

    /// Retrieves the current HTTP response.
    ///
    /// # Returns
    ///
    /// - `Response` - A clone of the current response.
    pub async fn get_response(&self) -> Response {
        self.read().await.get_response().clone()
    }

    /// Sets the HTTP response for the context.
    ///
    /// # Arguments
    ///
    /// - `Borrow<Response>` - The response to set in the context.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to the modified context.
    pub async fn set_response<T>(&self, response: T) -> &Self
    where
        T: Borrow<Response>,
    {
        self.write().await.set_response(response.borrow().clone());
        self
    }

    /// Executes an asynchronous closure with the current response.
    ///
    /// # Arguments
    ///
    /// - `F` - A closure that takes the `Response` and returns a future.
    ///
    /// # Returns
    ///
    /// - `R` - The result of the provided closure's future.
    pub async fn with_response<F, Fut, R>(&self, func: F) -> R
    where
        F: Fn(Response) -> Fut,
        Fut: FutureSendStatic<R>,
    {
        func(self.read().await.get_response().clone()).await
    }

    /// Retrieves the string representation of the current response.
    ///
    /// # Returns
    ///
    /// - `String` - The full response as a string.
    pub async fn get_response_string(&self) -> String {
        self.read().await.get_response().get_string()
    }

    /// Retrieves the HTTP version of the response.
    ///
    /// # Returns
    ///
    /// - `ResponseVersion` - The HTTP version of the response.
    pub async fn get_response_version(&self) -> ResponseVersion {
        self.read().await.get_response().get_version().clone()
    }

    /// Sets the HTTP version for the response.
    ///
    /// # Arguments
    ///
    /// - `ResponseVersion` - The HTTP version to set for the response.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to the modified context.
    pub async fn set_response_version(&self, version: ResponseVersion) -> &Self {
        self.write().await.get_mut_response().set_version(version);
        self
    }

    /// Retrieves all response headers.
    ///
    /// # Returns
    ///
    /// - `ResponseHeaders` - A clone of the response's header map.
    pub async fn get_response_headers(&self) -> ResponseHeaders {
        self.read().await.get_response().get_headers().clone()
    }

    /// Attempts to retrieve a specific response header by its key.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The key of the header to retrieve.
    ///
    /// # Returns
    ///
    /// - `Option<ResponseHeadersValue>` - The header values if the header exists.
    pub async fn try_get_response_header<K>(&self, key: K) -> Option<ResponseHeadersValue>
    where
        K: AsRef<str>,
    {
        self.read().await.get_response().try_get_header(key)
    }

    /// Retrieves a specific response header by its key, panicking if not found.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The key of the header to retrieve.
    ///
    /// # Returns
    ///
    /// - `ResponseHeadersValue` - The header values if the header exists.
    ///
    /// # Panics
    ///
    /// - If the header is not found.
    pub async fn get_response_header<K>(&self, key: K) -> ResponseHeadersValue
    where
        K: AsRef<str>,
    {
        self.read().await.get_response().get_header(key)
    }

    /// Sets a response header with a new value, removing any existing values.
    ///
    /// # Arguments
    ///
    /// - `K` - The key of the header to set.
    /// - `V` - The new value for the header.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to the modified context.
    pub async fn set_response_header<K, V>(&self, key: K, value: V) -> &Self
    where
        K: AsRef<str>,
        V: AsRef<str>,
    {
        self.write().await.get_mut_response().set_header(key, value);
        self
    }

    /// Attempts to retrieve the first value of a specific response header.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The key of the header.
    ///
    /// # Returns
    ///
    /// - `Option<ResponseHeadersValueItem>` - The first value of the header if it exists.
    pub async fn try_get_response_header_front<K>(&self, key: K) -> Option<ResponseHeadersValueItem>
    where
        K: AsRef<str>,
    {
        self.read().await.get_response().try_get_header_front(key)
    }

    /// Retrieves the first value of a specific response header, panicking if not found.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The key of the header.
    ///
    /// # Returns
    ///
    /// - `ResponseHeadersValueItem` - The first value of the header if it exists.
    ///
    /// # Panics
    ///
    /// - If the header is not found.
    pub async fn get_response_header_front<K>(&self, key: K) -> ResponseHeadersValueItem
    where
        K: AsRef<str>,
    {
        self.read().await.get_response().get_header_front(key)
    }

    /// Attempts to retrieve the last value of a specific response header.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The key of the header.
    ///
    /// # Returns
    ///
    /// - `Option<ResponseHeadersValueItem>` - The last value of the header if it exists.
    pub async fn try_get_response_header_back<K>(&self, key: K) -> Option<ResponseHeadersValueItem>
    where
        K: AsRef<str>,
    {
        self.read().await.get_response().try_get_header_back(key)
    }

    /// Retrieves the last value of a specific response header, panicking if not found.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The key of the header.
    ///
    /// # Returns
    ///
    /// - `ResponseHeadersValueItem` - The last value of the header if it exists.
    ///
    /// # Panics
    ///
    /// - If the header is not found.
    pub async fn get_response_header_back<K>(&self, key: K) -> ResponseHeadersValueItem
    where
        K: AsRef<str>,
    {
        self.read().await.get_response().get_header_back(key)
    }

    /// Checks if a specific response header exists.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The key of the header to check.
    ///
    /// # Returns
    ///
    /// - `bool` - True if the header exists, otherwise false.
    pub async fn get_response_has_header<K>(&self, key: K) -> bool
    where
        K: AsRef<str>,
    {
        self.read().await.get_response().has_header(key)
    }

    /// Checks if a response header has a specific value.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The key of the header.
    /// - `AsRef<str>` - The value to check for.
    ///
    /// # Returns
    ///
    /// - `bool` - True if the header contains the specified value, otherwise false.
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

    /// Retrieves the total number of response headers.
    ///
    /// # Returns
    ///
    /// - `usize` - The total number of headers in the response.
    pub async fn get_response_headers_length(&self) -> usize {
        self.read().await.get_response().get_headers_length()
    }

    /// Attempts to retrieve the number of values for a specific response header.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The key of the header.
    ///
    /// # Returns
    ///
    /// - `Option<usize>` - The number of values for the specified header if it exists.
    pub async fn try_get_response_header_length<K>(&self, key: K) -> Option<usize>
    where
        K: AsRef<str>,
    {
        self.read().await.get_response().try_get_header_length(key)
    }

    /// Retrieves the number of values for a specific response header.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The key of the header.
    ///
    /// # Returns
    ///
    /// - `usize` - The number of values for the specified header.
    ///
    /// # Panics
    ///
    /// - If the header is not found.
    pub async fn get_response_header_length<K>(&self, key: K) -> usize
    where
        K: AsRef<str>,
    {
        self.read().await.get_response().get_header_length(key)
    }

    /// Retrieves the total number of values across all response headers.
    ///
    /// # Returns
    ///
    /// - `usize` - The total count of all values in all headers.
    pub async fn get_response_headers_values_length(&self) -> usize {
        self.read().await.get_response().get_headers_values_length()
    }

    /// Adds a response header, adding it if it doesn't exist or appending to it if it does.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The header key.
    /// - `AsRef<str>` - The header value.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to self for method chaining.
    pub async fn add_response_header<K, V>(&self, key: K, value: V) -> &Self
    where
        K: AsRef<str>,
        V: AsRef<str>,
    {
        self.write().await.get_mut_response().add_header(key, value);
        self
    }

    /// Removes a response header and all its values.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The key of the header to remove.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to the modified context.
    pub async fn remove_response_header<K>(&self, key: K) -> &Self
    where
        K: AsRef<str>,
    {
        self.write().await.get_mut_response().remove_header(key);
        self
    }

    /// Removes a specific value from a response header.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The header key.
    /// - `AsRef<str>` - The value to remove.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to self for method chaining.
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

    /// Clears all headers from the response.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to the modified context.
    pub async fn clear_response_headers(&self) -> &Self {
        self.write().await.get_mut_response().clear_headers();
        self
    }

    /// Parses and retrieves all cookies from the response headers.
    ///
    /// # Returns
    ///
    /// - `Cookies` - A map of cookies parsed from the response's Cookie header.
    pub async fn get_response_cookies(&self) -> Cookies {
        self.try_get_response_header_back(COOKIE)
            .await
            .map(|data| Cookie::parse(&data))
            .unwrap_or_default()
    }

    /// Attempts to retrieve a specific cookie by its name from the response.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The name of the cookie to retrieve.
    ///
    /// # Returns
    ///
    /// - `Option<CookieValue>` - The cookie's value if it exists.
    pub async fn try_get_response_cookie<K>(&self, key: K) -> Option<CookieValue>
    where
        K: AsRef<str>,
    {
        self.get_response_cookies().await.get(key.as_ref()).cloned()
    }

    /// Retrieves a specific cookie by its name from the response, panicking if not found.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The name of the cookie to retrieve.
    ///
    /// # Returns
    ///
    /// - `CookieValue` - The cookie's value if it exists.
    ///
    /// # Panics
    ///
    /// - If the cookie is not found.
    pub async fn get_response_cookie<K>(&self, key: K) -> CookieValue
    where
        K: AsRef<str>,
    {
        self.try_get_response_cookie(key).await.unwrap()
    }

    /// Retrieves the body of the response.
    ///
    /// # Returns
    ///
    /// - `ResponseBody` - The response body.
    pub async fn get_response_body(&self) -> ResponseBody {
        self.read().await.get_response().get_body().clone()
    }

    /// Sets the body of the response.
    ///
    /// # Arguments
    ///
    /// - `B` - The body data to set for the response.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to the modified context.
    pub async fn set_response_body<B>(&self, body: B) -> &Self
    where
        B: AsRef<[u8]>,
    {
        self.write().await.get_mut_response().set_body(body);
        self
    }

    /// Retrieves the response body as a string.
    ///
    /// # Returns
    ///
    /// - `String` - The response body converted to a string.
    pub async fn get_response_body_string(&self) -> String {
        self.read().await.get_response().get_body_string()
    }

    /// Deserializes the response body from JSON into a specified type.
    ///
    /// # Returns
    ///
    /// - `Result<J, serde_json::Error>` - The deserialized type `J` or a JSON error.
    pub async fn try_get_response_body_json<J>(&self) -> Result<J, serde_json::Error>
    where
        J: DeserializeOwned,
    {
        self.read().await.get_response().try_get_body_json()
    }

    /// Deserializes the response body from JSON into a specified type, panicking if not found.
    ///
    /// # Returns
    ///
    /// - `J` - The deserialized type `J`.
    ///
    /// # Panics
    ///
    /// - If deserialization fails.
    pub async fn get_response_body_json<J>(&self) -> J
    where
        J: DeserializeOwned,
    {
        self.read().await.get_response().get_body_json()
    }

    /// Retrieves the reason phrase of the response status code.
    ///
    /// # Returns
    ///
    /// - `ResponseReasonPhrase` - The reason phrase associated with the response status code.
    pub async fn get_response_reason_phrase(&self) -> ResponseReasonPhrase {
        self.read().await.get_response().get_reason_phrase().clone()
    }

    /// Sets the reason phrase for the response status code.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The reason phrase to set.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to the modified context.
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

    /// Retrieves the status code of the response.
    ///
    /// # Returns
    ///
    /// - `ResponseStatusCode` - The status code of the response.
    pub async fn get_response_status_code(&self) -> ResponseStatusCode {
        *self.read().await.get_response().get_status_code()
    }

    /// Sets the status code for the response.
    ///
    /// # Arguments
    ///
    /// - `ResponseStatusCode` - The status code to set for the response.
    ///
    /// # Returns
    ///
    /// - `&Self` - A reference to the modified context.
    pub async fn set_response_status_code(&self, status_code: ResponseStatusCode) -> &Self {
        self.write()
            .await
            .get_mut_response()
            .set_status_code(status_code);
        self
    }

    /// Retrieves the parameters extracted from the route path.
    ///
    /// # Returns
    ///
    /// - `RouteParams` - A map containing the route parameters.
    pub async fn get_route_params(&self) -> RouteParams {
        self.read().await.get_route_params().clone()
    }

    /// Sets the route parameters for the context.
    ///
    /// # Arguments
    ///
    /// - `RouteParams` - The route parameters to set.
    ///
    /// # Returns
    ///
    /// - `&Self` - A reference to the modified `Context`.
    pub(crate) async fn set_route_params(&self, params: RouteParams) -> &Self {
        self.write().await.set_route_params(params);
        self
    }

    /// Attempts to retrieve a specific route parameter by its name.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The name of the route parameter to retrieve.
    ///
    /// # Returns
    ///
    /// - `Option<String>` - The value of the route parameter if it exists.
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

    /// Retrieves a specific route parameter by its name, panicking if not found.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The name of the route parameter to retrieve.
    ///
    /// # Returns
    ///
    /// - `String` - The value of the route parameter if it exists.
    ///
    /// # Panics
    ///
    /// - If the route parameter is not found.
    pub async fn get_route_param<T>(&self, name: T) -> String
    where
        T: AsRef<str>,
    {
        self.try_get_route_param(name).await.unwrap()
    }

    /// Retrieves all attributes stored in the context.
    ///
    /// # Returns
    ///
    /// - `ThreadSafeAttributeStore` - A map containing all attributes.
    pub async fn get_attributes(&self) -> ThreadSafeAttributeStore {
        self.read().await.get_attributes().clone()
    }

    /// Attempts to retrieve a specific attribute by its key, casting it to the specified type.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The key of the attribute to retrieve.
    ///
    /// # Returns
    ///
    /// - `Option<V>` - The attribute value if it exists and can be cast to the specified type.
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

    /// Retrieves a specific attribute by its key, casting it to the specified type, panicking if not found.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The key of the attribute to retrieve.
    ///
    /// # Returns
    ///
    /// - `V` - The attribute value if it exists and can be cast to the specified type.
    ///
    /// # Panics
    ///
    /// - If the attribute is not found.
    pub async fn get_attribute<K, V>(&self, key: K) -> V
    where
        K: AsRef<str>,
        V: AnySendSyncClone,
    {
        self.try_get_attribute(key).await.unwrap()
    }

    /// Sets an attribute in the context.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The key of the attribute to set.
    /// - `AnySendSyncClone` - The value of the attribute.
    ///
    /// # Returns
    ///
    /// - `&Self` - A reference to the modified context.
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

    /// Removes an attribute from the context.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The key of the attribute to remove.
    ///
    /// # Returns
    ///
    /// - `&Self` - A reference to the modified context.
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

    /// Clears all attributes from the context.
    ///
    /// # Returns
    ///
    /// - `&Self` - A reference to the modified context.
    pub async fn clear_attribute(&self) -> &Self {
        self.write().await.get_mut_attributes().clear();
        self
    }

    /// Retrieves an internal framework attribute.
    ///
    /// # Arguments
    ///
    /// - `InternalAttribute` - The internal attribute key to retrieve.
    ///
    /// # Returns
    ///
    /// - `Option<V>` - The attribute value if it exists and can be cast to the specified type.
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

    /// Retrieves an internal framework attribute.
    ///
    /// # Arguments
    ///
    /// - `InternalAttribute` - The internal attribute key to retrieve.
    ///
    /// # Returns
    ///
    /// - `V` - The attribute value if it exists and can be cast to the specified type.
    ///
    /// # Panics
    ///
    /// - If the attribute is not found.
    async fn get_internal_attribute<V>(&self, key: InternalAttribute) -> V
    where
        V: AnySendSyncClone,
    {
        self.try_get_internal_attribute(key).await.unwrap()
    }

    /// Sets an internal framework attribute.
    ///
    /// # Arguments
    ///
    /// - `InternalAttribute` - The internal attribute key to set.
    /// - `AnySendSyncClone` - The value of the attribute.
    ///
    /// # Returns
    ///
    /// - `&Self` - A reference to the modified context.
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

    /// Retrieves panic information if a panic has occurred during handling.
    ///
    /// # Returns
    ///
    /// - `Option<Panic>` - The panic information if a panic was caught.
    pub async fn try_get_panic(&self) -> Option<Panic> {
        self.try_get_internal_attribute(InternalAttribute::Panic)
            .await
    }

    /// Retrieves panic information if a panic has occurred during handling.
    ///
    /// # Returns
    ///
    /// - `Panic` - The panic information if a panic was caught.
    ///
    /// # Panics
    ///
    /// - If the panic information is not found.
    pub async fn get_panic(&self) -> Panic {
        self.get_internal_attribute(InternalAttribute::Panic).await
    }

    /// Sets the panic information for the context.
    ///
    /// # Arguments
    ///
    /// - `Panic` - The panic information to store.
    ///
    /// # Returns
    ///
    /// - `&Self` - A reference to the modified context.
    pub(crate) async fn set_panic(&self, panic: Panic) -> &Self {
        self.set_internal_attribute(InternalAttribute::Panic, panic)
            .await
    }

    /// Sets a hook function for the context with a custom key.
    ///
    /// # Arguments
    ///
    /// - `ToString` - The key to identify this hook.
    /// - `FnContextSendSyncStatic<Fut, ()>, Fut: FutureSendStatic<()>` - The hook function to store.
    ///
    /// # Returns
    ///
    /// - `&Self` - A reference to the modified context.
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

    /// Attempts to retrieve a hook function if it has been set.
    ///
    /// # Arguments
    ///
    /// - `K: ToString` - The key to identify the hook.
    ///
    /// # Returns
    ///
    /// - `Option<HookHandler<()>>` - The hook function if it has been set.
    pub async fn try_get_hook<K>(&self, key: K) -> Option<HookHandler<()>>
    where
        K: ToString,
    {
        self.try_get_internal_attribute(InternalAttribute::Hook(key.to_string()))
            .await
    }

    /// Retrieves a hook function if it has been set, panicking if not found.
    ///
    /// # Arguments
    ///
    /// - `K: ToString` - The key to identify the hook.
    ///
    /// # Returns
    ///
    /// - `HookHandler<()>` - The hook function if it has been set.
    ///
    /// # Panics
    ///
    /// - If the hook function is not found.
    pub async fn get_hook<K>(&self, key: K) -> HookHandler<()>
    where
        K: ToString,
    {
        self.get_internal_attribute(InternalAttribute::Hook(key.to_string()))
            .await
    }

    /// Updates the lifecycle status based on the current context state.
    ///
    /// # Arguments
    ///
    /// - `&mut RequestLifecycle` - The request lifecycle to update.
    pub(crate) async fn update_lifecycle_status(&self, lifecycle: &mut RequestLifecycle) {
        let keep_alive: bool = !self.get_closed().await && lifecycle.is_keep_alive();
        let aborted: bool = self.get_aborted().await;
        lifecycle.update_status(aborted, keep_alive);
    }

    /// Sends the response headers and body to the client.
    ///
    /// # Returns
    ///
    /// - `Result<(), ResponseError>` - The result of the send operation.
    pub async fn send(&self) -> Result<(), ResponseError> {
        if self.is_terminated().await {
            return Err(ResponseError::Terminated);
        }
        let response_data: ResponseData = self.write().await.get_mut_response().build();
        if let Some(stream) = self.try_get_stream().await {
            return stream.send(response_data).await;
        }
        Err(ResponseError::NotFoundStream)
    }

    /// Sends only the response body to the client.
    ///
    /// This method is useful for streaming data or for responses where headers have already been sent.
    ///
    /// # Returns
    ///
    /// - `Result<(), ResponseError>` - The result of the send operation.
    pub async fn send_body(&self) -> Result<(), ResponseError> {
        let response_body: ResponseBody = self.get_response_body().await;
        self.send_body_with_data(response_body).await
    }

    /// Sends only the response body to the client with additional data.
    ///
    /// This method is useful for streaming data or for responses where headers have already been sent.
    ///
    /// # Arguments
    ///
    /// - `AsRef<[u8]>` - The additional data to send as the body.
    ///
    /// # Returns
    ///
    /// - `Result<(), ResponseError>` - The result of the send operation.
    pub async fn send_body_with_data<D>(&self, data: D) -> Result<(), ResponseError>
    where
        D: AsRef<[u8]>,
    {
        if self.is_terminated().await {
            return Err(ResponseError::Terminated);
        }
        if let Some(stream) = self.try_get_stream().await {
            return stream.send_body(data).await;
        }
        Err(ResponseError::NotFoundStream)
    }

    /// Sends a list of response bodies to the client with additional data.
    ///
    /// This is useful for streaming multiple data chunks or for responses where headers have already been sent.
    ///
    /// # Arguments
    ///
    /// - `I: IntoIterator<Item = D>, D: AsRef<[u8]>` - The additional data to send as a list of bodies.
    ///
    /// # Returns
    ///
    /// - `Result<(), ResponseError>` - The result of the send operation.
    pub async fn send_body_list_with_data<I, D>(&self, data_iter: I) -> Result<(), ResponseError>
    where
        I: IntoIterator<Item = D>,
        D: AsRef<[u8]>,
    {
        if self.is_terminated().await {
            return Err(ResponseError::Terminated);
        }
        if let Some(stream) = self.try_get_stream().await {
            return stream.send_body_list(data_iter).await;
        }
        Err(ResponseError::NotFoundStream)
    }

    /// Flushes the underlying network stream, ensuring all buffered data is sent.
    ///
    /// # Returns
    ///
    /// - `Result<(), ResponseError>` - The result of the flush operation.
    pub async fn flush(&self) -> Result<(), ResponseError> {
        if let Some(stream) = self.try_get_stream().await {
            stream.flush().await;
            return Ok(());
        }
        Err(ResponseError::NotFoundStream)
    }

    /// Reads an HTTP request from the underlying stream.
    ///
    /// # Arguments
    ///
    /// - `RequestConfig` - The request config.
    ///
    /// # Returns
    ///
    /// - `Result<Request, RequestError>` - The parsed request or error.
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

    /// Reads a WebSocket frame from the underlying stream.
    ///
    /// # Arguments
    ///
    /// - `RequestConfig` - The request config.
    ///
    /// # Returns
    ///
    /// - `Result<Request, RequestError>` - The parsed frame or error.
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
}

```

# Path: hyperlane\src\context\mod.rs

```rust
pub(crate) mod r#impl;
pub(crate) mod r#struct;
pub(crate) mod r#type;

pub use r#struct::*;

pub(crate) use r#type::*;

```

# Path: hyperlane\src\context\struct.rs

```rust
use crate::*;

/// Represents the internal state of the application context.
///
/// This structure holds all the data associated with a single request-response cycle,
/// including the stream, request, response, and any custom attributes.
#[derive(Clone, Data, Default, CustomDebug, DisplayDebug)]
pub(crate) struct ContextInner {
    /// A flag indicating whether the request handling has been aborted.
    #[get(pub(super))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    aborted: bool,
    /// A flag indicating whether the connection has been closed.
    #[get(pub(super))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    closed: bool,
    /// The underlying network stream for the connection.
    #[get(pub(super))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    stream: Option<ArcRwLockStream>,
    /// The incoming HTTP request.
    #[get(pub(super))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    request: Request,
    /// The outgoing HTTP response.
    #[get(pub(super))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    response: Response,
    /// Parameters extracted from the route path.
    #[get(pub(super))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    route_params: RouteParams,
    /// A collection of custom attributes for sharing data within the request lifecycle.
    #[get(pub(super))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    attributes: ThreadSafeAttributeStore,
}

/// The main application context, providing thread-safe access to request and response data.
///
/// This is a wrapper around `ContextInner` that uses an `Arc<RwLock<>>` to allow
/// for shared, mutable access across asynchronous tasks.
#[derive(Clone, Default, Getter, CustomDebug, DisplayDebug)]
pub struct Context(#[get(pub(super))] pub(super) ArcRwLock<ContextInner>);

```

# Path: hyperlane\src\context\type.rs

```rust
use crate::*;

/// A type alias for a write guard on the context data.
///
/// This provides exclusive, mutable access to the `ContextInner` data.
pub(crate) type ContextWriteGuard<'a> = RwLockWriteGuard<'a, ContextInner>;

/// A type alias for a read guard on the context data.
///
/// This provides shared, immutable access to the `ContextInner` data.
pub(crate) type ContextReadGuard<'a> = RwLockReadGuard<'a, ContextInner>;

```

# Path: hyperlane\src\error\enum.rs

```rust
use crate::*;

/// Represents errors that can occur at the server level.
#[derive(CustomDebug, DisplayDebug, PartialEq, Eq, Clone)]
pub enum ServerError {
    /// An error occurred while trying to bind to a TCP socket.
    TcpBind(String),
    /// An unknown or unexpected error occurred.
    Unknown(String),
    /// An error occurred while reading an HTTP request.
    HttpRead(String),
    /// The received HTTP request was invalid or malformed.
    InvalidHttpRequest(Request),
    /// Other error.
    Other(String),
}

/// Represents errors related to route definitions and matching.
#[derive(CustomDebug, DisplayDebug, PartialEq, Eq, Clone)]
pub enum RouteError {
    /// The route pattern cannot be empty.
    EmptyPattern,
    /// A route with the same pattern has already been defined.
    DuplicatePattern(String),
    /// The provided route pattern is not a valid regular expression.
    InvalidRegexPattern(String),
}

```

# Path: hyperlane\src\error\mod.rs

```rust
pub(crate) mod r#enum;

pub use r#enum::*;

```

# Path: hyperlane\src\hook\enum.rs

```rust
use crate::*;

/// Represents different handler types for hooks.
#[derive(Clone)]
pub enum HookHandlerSpec {
    /// Arc handler (used for request/response middleware and route)
    Handler(ServerHookHandler),
    /// Factory function that creates a handler when called
    Factory(ServerHookHandlerFactory),
}

/// Represents different kinds of hooks in the server lifecycle.
///
/// Each variant corresponds to a specific hook that can be registered
/// and triggered at different stages of request handling or server events.
/// Hooks with an `Option<isize>` allow specifying a priority order; `None` indicates
/// the default order (0 or unspecified).
#[derive(Clone, Debug, PartialEq, Eq, Copy, Hash, DisplayDebug)]
pub enum HookType {
    /// Triggered when a panic occurs in the server.
    ///
    /// - `Option<isize>`- Optional priority of the panic hook. `None` means default.
    PanicHook(Option<isize>),
    /// Executed before a request reaches its designated route handler.
    ///
    /// - `Option<isize>`- Optional priority of the request middleware.
    RequestMiddleware(Option<isize>),
    /// Represents a route handler for a specific path.
    ///
    /// - `&'static str`- The route path handled by this hook.
    Route(&'static str),
    /// Executed after a route handler but before the response is sent.
    ///
    /// - `Option<isize>`- Optional priority of the response middleware.
    ResponseMiddleware(Option<isize>),
}

```

# Path: hyperlane\src\hook\fn.rs

```rust
use crate::*;

/// Creates a new `ServerHookHandler` from a trait object.
///
/// # Arguments
///
/// - `ServerHook` - The trait object implementing `ServerHook`.
///
/// # Returns
///
/// - `ServerHookHandler` - A new `ServerHookHandler` instance.
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

/// Verify that each `Hook` in the list with the same type and non-zero priority is unique.
///
/// This function iterates over all provided `Hook` items and ensures that no two
/// `Hook` items of the same type define the same non-zero `order`. If a duplicate
/// is found, the function will panic at runtime.
///
/// # Arguments
///
/// - `Vec<HookMacro>`- A vector of `HookMacro` instances to be checked.
///
/// # Panics
///
/// - Panics if two or more `Hook` items of the same type define the same non-zero `order`.
#[inline(always)]
pub fn assert_hook_unique_order(list: Vec<HookMacro>) {
    let mut seen: HashSet<(HookType, isize)> = HashSet::new();
    list.iter()
        .filter_map(|hook| {
            hook.hook_type
                .try_get()
                .map(|order| (hook.hook_type, order))
        })
        .for_each(|(key, order)| {
            if !seen.insert((key, order)) {
                panic!("Duplicate hook detected: {} with order {}", key, order);
            }
        });
}

```

# Path: hyperlane\src\hook\impl.rs

```rust
use crate::*;

/// A blanket implementation for any function that takes a `Context` and returns a value.
///
/// This implementation makes it easy to use any compatible function as a `FnContextSendSync`,
/// promoting a flexible and functional programming style.
impl<F, R> FnContextSendSync<R> for F where F: Fn(Context) -> R + Send + Sync {}

/// A blanket implementation for functions that return a pinned, boxed, sendable future.
///
/// This trait is a common pattern for asynchronous handlers in Rust, enabling type
/// erasure and dynamic dispatch for futures. It is essential for storing different
/// async functions in a collection.
impl<F, T> FnContextPinBoxSendSync<T> for F where F: FnContextSendSync<SendableAsyncTask<T>> {}

/// A blanket implementation for static, sendable, synchronous functions that return a future.
///
/// This trait is used for handlers that are known at compile time, ensuring they
/// are safe to be sent across threads and have a static lifetime. This is crucial
/// for handlers that are part of the application's long-lived state.
impl<F, Fut, T> FnContextSendSyncStatic<Fut, T> for F
where
    F: FnContextSendSync<Fut> + 'static,
    Fut: Future<Output = T> + Send,
{
}

/// A blanket implementation for any future that is sendable and has a static lifetime.
///
/// This is a convenient trait for working with futures in an asynchronous context,
/// ensuring that they can be safely managed by the async runtime across different
/// threads.
impl<T, R> FutureSendStatic<R> for T where T: Future<Output = R> + Send + 'static {}

/// Blanket implementation of `FutureSend` for any type that satisfies the bounds.
impl<T, O> FutureSend<O> for T where T: Future<Output = O> + Send {}

/// Blanket implementation of `FnPinBoxFutureSend` for any type that satisfies the bounds.
impl<T, O> FnPinBoxFutureSend<O> for T where T: Fn() -> SendableAsyncTask<O> + Send + Sync {}

/// Provides a default implementation for `ServerControlHook`.
impl Default for ServerControlHook {
    /// Creates a new `ServerControlHook` instance with default no-op hooks.
    ///
    /// The default `wait_hook` and `shutdown_hook` do nothing, allowing the server
    /// to run without specific shutdown or wait logic unless configured otherwise.
    ///
    /// # Returns
    ///
    /// - `Self` - A new `ServerControlHook` instance with default hooks.
    #[inline(always)]
    fn default() -> Self {
        Self {
            wait_hook: Arc::new(|| Box::pin(async {})),
            shutdown_hook: Arc::new(|| Box::pin(async {})),
        }
    }
}

/// Manages server lifecycle hooks, including waiting and shutdown procedures.
///
/// This struct holds closures that are executed during specific server lifecycle events.
impl ServerControlHook {
    /// Waits for the server's shutdown signal or completion.
    ///
    /// This method asynchronously waits until the server's `wait_hook` is triggered,
    /// typically indicating that the server has finished its operations or is ready to shut down.
    pub async fn wait(&self) {
        self.get_wait_hook()().await;
    }

    /// Initiates the server shutdown process.
    ///
    /// This method asynchronously calls the `shutdown_hook`, which is responsible for
    /// performing any necessary cleanup or graceful shutdown procedures.
    pub async fn shutdown(&self) {
        self.get_shutdown_hook()().await;
    }
}

impl PartialEq for HookHandlerSpec {
    #[inline(always)]
    fn eq(&self, other: &Self) -> bool {
        match (self, other) {
            (HookHandlerSpec::Handler(handler_a), HookHandlerSpec::Handler(handler_b)) => {
                Arc::ptr_eq(handler_a, handler_b)
            }
            (HookHandlerSpec::Factory(factory_a), HookHandlerSpec::Factory(factory_b)) => {
                std::ptr::eq(factory_a as *const _, factory_b as *const _)
            }
            _ => false,
        }
    }
}

impl Eq for HookHandlerSpec {}

/// Implementation block for `HookType`.
///
/// This block defines utility methods associated with the `HookType` enum.
/// These methods provide additional functionality for working with hooks,
/// such as extracting the execution order (priority) used in duplicate checks.
impl HookType {
    /// Returns the optional execution priority (`order`) of a hook.
    ///
    /// Hooks that carry an `order` indicate their execution priority.  
    /// Hooks without an `order` are considered unordered and are ignored in duplicate checks.
    ///
    /// # Returns
    ///
    /// - `Option<isize>` - `Some(order)` if the hook defines a priority, otherwise `None`.
    #[inline(always)]
    pub fn try_get(&self) -> Option<isize> {
        match *self {
            HookType::RequestMiddleware(order)
            | HookType::ResponseMiddleware(order)
            | HookType::PanicHook(order) => order,
            _ => None,
        }
    }
}

```

# Path: hyperlane\src\hook\mod.rs

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

# Path: hyperlane\src\hook\struct.rs

```rust
use crate::*;

/// Represents the hooks for managing the server's lifecycle, specifically for waiting and shutting down.
///
/// This struct is returned by the `run` method and provides two key hooks:
/// - `wait_hook`- A future that resolves when the server has stopped accepting new connections.
/// - `shutdown_hook`- A function that can be called to gracefully shut down the server.
#[derive(Clone, CustomDebug, DisplayDebug, Getter, Setter)]
pub struct ServerControlHook {
    /// A hook that returns a future, which completes when the server's main task finishes.
    /// This is typically used to wait for the server to stop accepting connections before
    /// the application exits.
    #[debug(skip)]
    #[get(pub)]
    #[set(pub(crate))]
    pub(super) wait_hook: SharedAsyncTaskFactory<()>,
    /// A hook that, when called, initiates a graceful shutdown of the server.
    /// This will stop the server from accepting new connections and allow existing ones
    /// to complete.
    #[debug(skip)]
    #[get(pub)]
    #[set(pub(crate))]
    pub(super) shutdown_hook: SharedAsyncTaskFactory<()>,
}

/// Represents a route definition created by a macro.
///
/// This struct encapsulates the necessary information to register a new hook.
#[derive(Getter, Setter, Clone, CustomDebug, PartialEq, Eq)]
pub struct HookMacro {
    /// Represents the asynchronous handler that is executed when
    /// the associated hook is triggered.
    #[debug(skip)]
    pub handler: HookHandlerSpec,
    /// Represents the type of the hook that determines when the handler
    /// should be executed.
    pub hook_type: HookType,
}

impl HookMacro {
    /// Creates a new HookMacro for a panic hook with a generic type.
    ///
    /// # Type Parameters
    ///
    /// - `P: ServerHook` - The panic hook type.
    ///
    /// # Arguments
    ///
    /// - `order` - Optional execution priority.
    ///
    /// # Returns
    ///
    /// - `Self` - The created HookMacro instance.
    pub fn panic_hook<P: ServerHook>(order: Option<isize>) -> Self {
        Self {
            handler: HookHandlerSpec::Factory(server_hook_factory::<P>),
            hook_type: HookType::PanicHook(order),
        }
    }

    /// Creates a new HookMacro for request middleware with a generic type.
    ///
    /// # Type Parameters
    ///
    /// - `M: ServerHook` - The middleware type.
    ///
    /// # Arguments
    ///
    /// - `order` - Optional execution priority.
    ///
    /// # Returns
    ///
    /// - `Self` - The created HookMacro instance.
    pub fn request_middleware<M: ServerHook>(order: Option<isize>) -> Self {
        Self {
            handler: HookHandlerSpec::Factory(server_hook_factory::<M>),
            hook_type: HookType::RequestMiddleware(order),
        }
    }

    /// Creates a new HookMacro for response middleware with a generic type.
    ///
    /// # Type Parameters
    ///
    /// - `M: ServerHook` - The middleware type.
    ///
    /// # Arguments
    ///
    /// - `order` - Optional execution priority.
    ///
    /// # Returns
    ///
    /// - `Self` - The created HookMacro instance.
    pub fn response_middleware<M: ServerHook>(order: Option<isize>) -> Self {
        Self {
            handler: HookHandlerSpec::Factory(server_hook_factory::<M>),
            hook_type: HookType::ResponseMiddleware(order),
        }
    }

    /// Creates a new HookMacro for a route with a generic type.
    ///
    /// # Type Parameters
    ///
    /// - `R: ServerHook` - The route handler type.
    ///
    /// # Arguments
    ///
    /// - `path` - The route path.
    ///
    /// # Returns
    ///
    /// - `Self` - The created HookMacro instance.
    pub fn route<R: ServerHook>(path: &'static str) -> Self {
        Self {
            handler: HookHandlerSpec::Factory(server_hook_factory::<R>),
            hook_type: HookType::Route(path),
        }
    }
}

```

# Path: hyperlane\src\hook\trait.rs

```rust
use crate::*;

/// A generic trait for functions that take a `Context` and return a value.
///
/// This trait encapsulates the common behavior of being a sendable, synchronous
/// function that accepts a `Context`. It is used as a base for other, more
/// specific function traits.
pub trait FnContextSendSync<R>: Fn(Context) -> R + Send + Sync {}

/// A trait for functions that return a pinned, boxed, sendable future.
///
/// This trait is essential for creating type-erased async function pointers,
/// which is a common pattern for storing and dynamically dispatching different
/// asynchronous handlers in a collection.
pub trait FnContextPinBoxSendSync<T>: FnContextSendSync<SendableAsyncTask<T>> {}

/// A trait for static, sendable, synchronous functions that return a future.
///
/// This trait ensures that a handler function is safe to be sent across threads
/// and has a static lifetime, making it suitable for use in long-lived components
/// of the application, such as the main router.
pub trait FnContextSendSyncStatic<Fut, T>: FnContextSendSync<Fut> + 'static
where
    Fut: Future<Output = T> + Send,
{
}

/// A trait for futures that are sendable and have a static lifetime.
///
/// This marker trait simplifies generic bounds for asynchronous operations, ensuring
```

# Path: hyperlane\src\hook\type.rs

```rust
use crate::*;

/// A type alias for a shared hook handler.
///
/// This type is used for storing handlers in a shared context, allowing multiple
/// parts of the application to safely access and execute the same handler.
pub type HookHandler<T> = Arc<dyn FnContextPinBoxSendSync<T>>;

/// A type alias for a hook handler chain.
///
/// This type is used to represent a chain of middleware or hooks that can be
/// executed sequentially.
pub type HookHandlerChain<T> = Vec<HookHandler<T>>;

/// A type alias for an asynchronous task.
///
/// This is a common return type for asynchronous handlers, providing a type-erased
/// future that can be easily managed by the async runtime.
pub type AsyncTask = Pin<Box<dyn Future<Output = ()> + Send + 'static>>;

/// A type alias for a sendable asynchronous task with a generic output.
///
/// This is often used to represent an asynchronous task that can be sent across threads.
pub type SendableAsyncTask<T> = Pin<Box<dyn Future<Output = T> + Send>>;

/// A type alias for a shared asynchronous task factory.
///
/// This is useful for creating and sharing asynchronous task factories.
pub type SharedAsyncTaskFactory<T> = Arc<dyn FnPinBoxFutureSend<T>>;

/// A type alias for a hook handler factory function.
///
/// This function pointer type is used to create ServerHookHandler instances
/// based on generic types. It allows delayed instantiation of hooks.
pub type ServerHookHandlerFactory = fn() -> ServerHookHandler;

/// Type alias for a shared server hook handler.
///
/// This type allows storing handlers (route and middleware) of different concrete types
/// in the same collection. The handler takes a `&Context` and returns
/// a pinned, boxed future that resolves to `()`.
pub type ServerHookHandler = Arc<dyn Fn(&Context) -> SendableAsyncTask<()> + Send + Sync>;

/// Type alias for a list of server hooks.
///
/// Used to store middleware handlers in the request/response processing pipeline.
pub type ServerHookList = Vec<ServerHookHandler>;

/// Type alias for a map of server hook handlers.
///
/// Used for fast lookup of exact-match route.
pub type ServerHookMap = HashMapXxHash3_64<String, ServerHookHandler>;

/// Type alias for a collection of pattern-based server hook route grouped by segment count.
///
/// The outer HashMap uses segment count as key for fast filtering.
/// The inner Vec stores patterns with the same segment count, maintaining insertion order.
pub type ServerHookPatternRoute = HashMapXxHash3_64<usize, Vec<(RoutePattern, ServerHookHandler)>>;

```

# Path: hyperlane\src\lifecycle\enum.rs

```rust
/// Represents the control flow state of a request's lifecycle.
///
/// This enum is used internally to manage whether the request processing pipeline
/// should proceed to the next stage or be terminated prematurely. It also tracks
/// whether the underlying connection should be kept alive for subsequent requests.
#[derive(Debug, Clone, PartialEq, Eq)]
pub(crate) enum RequestLifecycle {
    /// Indicates that the request processing should be aborted.
    /// The boolean value specifies whether the connection should be kept alive (`true`) or closed (`false`).
    Aborted(bool),
    /// Indicates that the request processing should continue to the next stage.
    /// The boolean value specifies whether the connection should be kept alive (`true`) or closed (`false`).
    Continuing(bool),
}

```

# Path: hyperlane\src\lifecycle\impl.rs

```rust
use super::*;

/// Implementation of methods for the `RequestLifecycle` enum.
impl RequestLifecycle {
    /// Creates a new RequestLifecycle instance with Continuing state.
    ///
    /// # Arguments
    ///
    /// - `bool` - Whether the connection should be kept alive.
    ///
    /// # Returns
    ///
    /// - `RequestLifecycle` - A new RequestLifecycle::Continuing instance.
    #[inline(always)]
    pub(crate) fn new(keep_alive: bool) -> Self {
        Self::Continuing(keep_alive)
    }

    /// Updates the lifecycle status based on abort and keep-alive flags.
    ///
    /// # Arguments
    ///
    /// - `&mut self` - A mutable reference to the `RequestLifecycle` instance.
    /// - `bool` - Whether the request processing has been aborted.
    /// - `bool` - Whether the connection should be kept alive.
    #[inline(always)]
    pub(crate) fn update_status(&mut self, aborted: bool, keep_alive: bool) {
        *self = if aborted {
            RequestLifecycle::Aborted(keep_alive)
        } else {
            RequestLifecycle::Continuing(keep_alive)
        };
    }

    /// Checks if the lifecycle state is Aborted.
    ///
    /// # Returns
    ///
    /// - `bool` - true if in Aborted state, false otherwise.
    #[inline(always)]
    pub(crate) fn is_aborted(&self) -> bool {
        matches!(self, RequestLifecycle::Aborted(_))
    }

    /// Checks if the connection should be kept alive.
    ///
    /// # Returns
    ///
    /// - `bool` - true if keep-alive flag is set, false otherwise.
    #[inline(always)]
    pub(crate) fn is_keep_alive(&self) -> bool {
        matches!(
            self,
            RequestLifecycle::Continuing(true) | RequestLifecycle::Aborted(true)
        )
    }

    /// Returns the keep-alive status of the connection.
    ///
    /// # Returns
    ///
    /// - `bool` - The keep-alive flag value.
    #[inline(always)]
    pub(crate) fn keep_alive(&self) -> bool {
        match self {
            RequestLifecycle::Continuing(res) | RequestLifecycle::Aborted(res) => *res,
        }
    }
}

```

# Path: hyperlane\src\lifecycle\mod.rs

```rust
pub(crate) mod r#enum;
pub(crate) mod r#impl;

pub(crate) use r#enum::*;

```

# Path: hyperlane\src\panic\impl.rs

```rust
use crate::*;

/// Implementation of methods for the `Panic` struct.
impl Panic {
    /// Creates a new `Panic` instance from its constituent parts.
    ///
    /// # Arguments
    ///
    /// - `Option<String>` - The panic message.
    /// - `Option<String>` - The source code location of the panic.
    /// - `Option<String>` - The panic payload.
    ///
    /// # Returns
    ///
    /// - `Panic` - A new panic instance.
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

    /// Attempts to extract a string from a dynamic `&dyn Any` panic payload.
    ///
    /// This function handles payloads that are either `&str` or `String`.
    ///
    /// # Arguments
    ///
    /// - `&dyn Any` - The payload from a `PanicInfo` object.
    ///
    /// # Returns
    ///
    /// - `Option<String>` - The extracted message, or None if the payload is not a string type.
    #[inline(always)]
    fn try_extract_panic_message(panic_payload: &dyn Any) -> Option<String> {
        if let Some(s) = panic_payload.downcast_ref::<&str>() {
            Some(s.to_string())
        } else {
            panic_payload.downcast_ref::<String>().cloned()
        }
    }

    /// Creates a `Panic` instance from a `tokio::task::JoinError`.
    ///
    /// This is used to handle panics that occur within spawned asynchronous tasks,
    /// extracting the panic message from the `JoinError`.
    ///
    /// # Arguments
    ///
    /// - `JoinError` - The error from a panicked task.
    ///
    /// # Returns
    ///
    /// - `Panic` - A new panic instance with message from error.
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
        let panic: Panic = Panic::new(message, None, None);
        panic
    }
}

```

# Path: hyperlane\src\panic\mod.rs

```rust
pub(crate) mod r#impl;
pub(crate) mod r#struct;

pub use r#struct::*;

```

# Path: hyperlane\src\panic\struct.rs

```rust
use crate::*;

/// Represents detailed information about a panic that has occurred within the server.
///
/// This struct captures essential details about a panic, such as the message,
/// source code location, and payload. It is used by the server's panic handling
/// mechanism and passed to the configured panic hook for custom processing.
#[derive(CustomDebug, Default, PartialEq, Eq, Clone, Getter, DisplayDebug, Setter)]
pub struct Panic {
    /// The message associated with the panic.
    /// This is `None` if the panic payload is not a string.
    #[get(pub)]
    #[set(pub(crate))]
    pub(super) message: Option<String>,
    /// The source code location where the panic occurred.
    #[get(pub)]
    #[set(pub(crate))]
    pub(super) location: Option<String>,
    /// The payload of the panic, often a string literal.
    /// The handler attempts to downcast it to a `&str` or `String`.
    #[get(pub)]
    #[set(pub(crate))]
    pub(super) payload: Option<String>,
}

```

# Path: hyperlane\src\route\enum.rs

```rust
use crate::*;

/// Represents the different types of segments that can make up a route path.
///
/// A route path is parsed into a sequence of these segments. For example, the path
/// `/users/:id/posts` would be broken down into `Static("users")`, `Dynamic("id")`,
/// and `Static("posts")`.
#[derive(Clone, CustomDebug, DisplayDebug)]
pub enum RouteSegment {
    /// A static, literal segment of a path.
    /// This must be an exact match. For example, in `/users/active`, "users" and "active"
    /// are both static segments.
    Static(String),
    /// A dynamic segment that captures a value from the path.
    /// It is denoted by a colon prefix. The captured value
    /// is stored as a parameter in the request context.
    Dynamic(String),
    /// A segment that is matched against a regular expression.
    /// This allows for more complex and flexible routing logic. The first element is the parameter
    /// name, and the second is the compiled `Regex` object.
    Regex(String, Regex),
}

```

# Path: hyperlane\src\route\impl.rs

```rust
use crate::*;

// Associate a plugin registry with the specified type.
collect!(HookMacro);

/// Provides a default implementation for RouteMatcher.
impl Default for RouteMatcher {
    /// Creates a new, empty RouteMatcher.
    ///
    /// # Returns
    ///
    /// - `RouteMatcher` - A new RouteMatcher with empty storage for static, dynamic, and regex route.
    #[inline(always)]
    fn default() -> Self {
        Self {
            static_route: hash_map_xx_hash3_64(),
            dynamic_route: hash_map_xx_hash3_64(),
            regex_route: hash_map_xx_hash3_64(),
        }
    }
}

/// Implements the `PartialEq` trait for `RoutePattern`.
///
/// This allows for comparing two `RoutePattern` instances for equality.
impl PartialEq for RoutePattern {
    /// Checks if two `RoutePattern` instances are equal.
    ///
    /// # Arguments
    ///
    /// - `&Self` - The other `RoutePattern` instance to compare against.
    ///
    /// # Returns
    ///
    /// - `bool`- `true` if the instances are equal, `false` otherwise.
    #[inline(always)]
    fn eq(&self, other: &Self) -> bool {
        self.get_0() == other.get_0()
    }
}

/// Implements the `Eq` trait for `RoutePattern`.
///
/// This indicates that `RoutePattern` has a total equality relation.
impl Eq for RoutePattern {}

/// Implements the `Hash` trait for `RoutePattern`.
///
/// This allows `RoutePattern` to be used as a key in hash-based collections.
impl Hash for RoutePattern {
    /// Hashes the `RoutePattern` instance.
    ///
    /// # Arguments
    ///
    /// - `&mut Hasher` - The hasher to use.
    #[inline(always)]
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.get_0().hash(state);
    }
}

/// Implements the `PartialOrd` trait for `RoutePattern`.
///
/// This allows for partial ordering of `RoutePattern` instances.
impl PartialOrd for RoutePattern {
    /// Partially compares two `RoutePattern` instances.
    ///
    /// # Arguments
    ///
    /// - `&Self`- The other `RoutePattern` instance to compare against.
    ///
    /// # Returns
    ///
    /// - `Option<Ordering>`- The ordering of the two instances.
    #[inline(always)]
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

/// Implements the `Ord` trait for `RoutePattern`.
///
/// This allows for total ordering of `RoutePattern` instances.
impl Ord for RoutePattern {
    /// Compares two `RoutePattern` instances.
    ///
    /// # Arguments
    ///
    /// - `&Self`- The other `RoutePattern` instance to compare against.
    ///
    /// # Returns
    ///
    /// - `Ordering`- The ordering of the two instances.
    #[inline(always)]
    fn cmp(&self, other: &Self) -> Ordering {
        self.get_0().cmp(other.get_0())
    }
}

/// Implements the `PartialEq` trait for `RouteMatcher`.
///
/// This allows for comparing two `RouteMatcher` instances for equality.
impl PartialEq for RouteMatcher {
    /// Checks if two `RouteMatcher` instances are equal.
    ///
    /// # Arguments
    ///
    /// - `&Self`- The other `RouteMatcher` instance to compare against.
    ///
    /// # Returns
    ///
    /// - `bool`- `true` if the instances are equal, `false` otherwise.
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

/// Implements the `Eq` trait for `RouteMatcher`.
///
/// This indicates that `RouteMatcher` has a total equality relation.
impl Eq for RouteMatcher {}

/// Implements the `Eq` trait for `RouteSegment`.
///
/// This indicates that `RouteSegment` has a total equality relation.
impl Eq for RouteSegment {}

/// Implements the `PartialOrd` trait for `RouteSegment`.
///
/// This allows for partial ordering of `RouteSegment` instances.
impl PartialOrd for RouteSegment {
    /// Partially compares two `RouteSegment` instances.
    ///
    /// # Arguments
    ///
    /// - `&Self`- The other `RouteSegment` instance to compare against.
    ///
    /// # Returns
    ///
    /// - `Option<Ordering>`- The ordering of the two instances.
    #[inline(always)]
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

/// Implements the `Ord` trait for `RouteSegment`.
///
/// This allows for total ordering of `RouteSegment` instances.
impl Ord for RouteSegment {
    /// Compares two `RouteSegment` instances.
    ///
    /// # Arguments
    ///
    /// - `&Self`- The other `RouteSegment` instance to compare against.
    ///
    /// # Returns
    ///
    /// - `Ordering`- The ordering of the two instances.
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

/// Implements the `PartialEq` trait for `RouteSegment`.
///
/// This allows for comparing two `RouteSegment` instances for equality.
impl PartialEq for RouteSegment {
    /// Checks if two `RouteSegment` instances are equal.
    ///
    /// # Arguments
    ///
    /// - `&Self`- The other `RouteSegment` instance to compare against.
    ///
    /// # Returns
    ///
    /// - `bool`- `true` if the instances are equal, `false` otherwise.
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

/// Implements the `Hash` trait for `RouteSegment`.
///
/// This allows `RouteSegment` to be used in hash-based collections.
impl Hash for RouteSegment {
    /// Hashes the `RouteSegment` instance.
    ///
    /// # Arguments
    ///
    /// - `&mut HHasher` - The hasher to use.
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

/// Manages route patterns, including parsing and matching.
///
/// This struct is responsible for defining and validating route structures,
/// supporting static, dynamic, and regex-based path matching.
impl RoutePattern {
    /// Creates a new RoutePattern by parsing a route string.
    ///
    /// # Arguments
    ///
    /// - `&str` - The raw route string to parse.
    ///
    /// # Returns
    ///
    /// - `Result<RoutePattern, RouteError>` - The parsed RoutePattern on success, or RouteError on failure.
    pub(crate) fn new(route: &str) -> Result<RoutePattern, RouteError> {
        Ok(Self(Self::parse_route(route)?))
    }

    /// Parses a raw route string into RouteSegments.
    ///
    /// This is the core logic for interpreting the route syntax.
    ///
    /// # Arguments
    ///
    /// - `&str` - The raw route string.
    ///
    /// # Returns
    ///
    /// - `Result<RouteSegmentList, RouteError>` - Vector of RouteSegments on success, or RouteError on failure.
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
                        Err(err) => {
                            return Err(RouteError::InvalidRegexPattern(format!(
                                "Invalid regex pattern '{}{}{}",
                                pattern, COLON, err
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

    /// Matches this route pattern against a request path.
    ///
    /// If the pattern matches, extracts any dynamic or regex parameters.
    ///
    /// # Arguments
    ///
    /// - `&str` - The request path to match against.
    ///
    /// # Returns
    ///
    /// - `Option<RouteParams>` - Some with parameters if matched, None otherwise.
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
                        break;
                    }
                }
            }
        }
        Some(params)
    }

    /// Checks if the route pattern is static.
    ///
    /// # Returns
    ///
    /// - `bool` - true if the pattern is static, false otherwise.
    #[inline(always)]
    pub(crate) fn is_static(&self) -> bool {
        self.get_0()
            .iter()
            .all(|seg| matches!(seg, RouteSegment::Static(_)))
    }

    /// Checks if the route pattern is dynamic.
    ///
    /// # Returns
    ///
    /// - `bool` - true if the pattern is dynamic, false otherwise.
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

    /// Gets the number of segments in this route pattern.
    ///
    /// # Returns
    ///
    /// - `usize` - The number of segments.
    #[inline(always)]
    pub(crate) fn segment_count(&self) -> usize {
        self.get_0().len()
    }

    /// Checks if the last segment is a regex pattern.
    ///
    /// # Returns
    ///
    /// - `bool` - true if the last segment is a regex, false otherwise.
    #[inline(always)]
    pub(crate) fn has_tail_regex(&self) -> bool {
        matches!(self.get_0().last(), Some(RouteSegment::Regex(_, _)))
    }
}

/// Manages a collection of route, enabling efficient lookup and dispatch.
///
/// This struct stores route categorized by type (static, dynamic, regex)
/// to quickly find the appropriate handler for incoming requests.
impl RouteMatcher {
    /// Creates a new, empty RouteMatcher.
    ///
    /// # Returns
    ///
    /// - `RouteMatcher` - A new RouteMatcher instance with empty route stores.
    #[inline(always)]
    pub(crate) fn new() -> Self {
        Self::default()
    }

    /// Counts the number of segments in a path.
    ///
    /// # Arguments
    ///
    /// - `&str` - The path to count segments in.
    ///
    /// # Returns
    ///
    /// - `usize` - The number of segments.
    #[inline(always)]
    fn count_path_segments(path: &str) -> usize {
        let path: &str = path.trim_start_matches(DEFAULT_HTTP_PATH);
        if path.is_empty() {
            return 0;
        }
        path.matches(DEFAULT_HTTP_PATH).count() + 1
    }

    /// Adds a new route and its handler to the matcher.
    ///
    /// Adds a route handler to the matcher.
    ///
    /// This method categorizes the route as static, dynamic, or regex based on its pattern
    /// and stores it in the appropriate collection.
    ///
    /// # Arguments
    ///
    /// - `&str` - The route pattern string.
    /// - `ServerHookHandler` - The boxed route handler.
    ///
    /// # Returns
    ///
    /// - `Result<(), RouteError>` - Ok on success, or RouteError if pattern is duplicate.
    pub(crate) fn add(
        &mut self,
        pattern: &str,
        handler: ServerHookHandler,
    ) -> Result<(), RouteError> {
        let route_pattern: RoutePattern = RoutePattern::new(pattern)?;
        if route_pattern.is_static() {
            if self.get_static_route().contains_key(pattern) {
                return Err(RouteError::DuplicatePattern(pattern.to_owned()));
            }
            self.get_mut_static_route()
                .insert(pattern.to_string(), handler);
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
            Err(pos) => routes_for_count.insert(pos, (route_pattern, handler)),
        }
        Ok(())
    }

    /// Resolves and executes a route handler.
    ///
    /// This method searches for a matching route and executes it if found.
    /// Finds a matching route handler for the given path.
    ///
    /// # Arguments
    ///
    /// - `&Context` - The request context.
    /// - `&str` - The request path to resolve.
    ///
    /// # Returns
    ///
    /// - `Option<ServerHookHandler>` - The matched route handler if found, None otherwise.
    pub(crate) async fn try_resolve_route(
        &self,
        ctx: &Context,
        path: &str,
    ) -> Option<ServerHookHandler> {
        if let Some(handler) = self.get_static_route().get(path) {
            ctx.set_route_params(RouteParams::default()).await;
            return Some(handler.clone());
        }
        let path_segment_count: usize = Self::count_path_segments(path);
        if let Some(routes) = self.get_dynamic_route().get(&path_segment_count) {
            for (pattern, handler) in routes {
                if let Some(params) = pattern.try_match_path(path) {
                    ctx.set_route_params(params).await;
                    return Some(handler.clone());
                }
            }
        }
        if let Some(routes) = self.get_regex_route().get(&path_segment_count) {
            for (pattern, handler) in routes {
                if let Some(params) = pattern.try_match_path(path) {
                    ctx.set_route_params(params).await;
                    return Some(handler.clone());
                }
            }
        }
        for (&segment_count, routes) in self.get_regex_route() {
            if segment_count == path_segment_count {
                continue;
            }
            for (pattern, handler) in routes {
                if pattern.has_tail_regex()
                    && path_segment_count >= segment_count
                    && let Some(params) = pattern.try_match_path(path)
                {
                    ctx.set_route_params(params).await;
                    return Some(handler.clone());
                }
            }
        }
        None
    }
}

```

# Path: hyperlane\src\route\mod.rs

```rust
pub(crate) mod r#enum;
pub(crate) mod r#impl;
pub(crate) mod r#struct;
pub(crate) mod r#type;

pub use r#struct::*;
pub use r#type::*;

pub use r#enum::*;

```

# Path: hyperlane\src\route\struct.rs

```rust
use crate::*;

/// Represents a parsed and structured route pattern.
///
/// This struct wraps a vector of `RouteSegment`s, which are the individual components
/// of a URL path. It is used internally by the `RouteMatcher` to perform efficient
/// route matching against incoming requests.
#[derive(Debug, Clone, Getter, DisplayDebug)]
pub struct RoutePattern(
    /// The collection of segments that make up the route pattern.
    #[get]
    pub(super) RouteSegmentList,
);

/// The core routing engine responsible for matching request paths to their corresponding handlers.
///
/// The matcher categorizes route into three types for optimized performance:
/// 1.  `static_route`- For exact path matches, offering the fastest lookups.
/// 2.  `dynamic_route`- For paths with variable segments.
/// 3.  `regex_route`- For complex matching based on regular expressions.
///
/// When a request comes in, the matcher checks these categories in order to find the appropriate handler.
#[derive(Clone, CustomDebug, Getter, GetterMut, DisplayDebug, Setter)]
pub struct RouteMatcher {
    /// A hash map for storing and quickly retrieving handlers for static route.
    /// These are route without any variable path segments.
    #[get]
    #[set(skip)]
    #[get_mut(pub(super))]
    #[debug(skip)]
    pub(super) static_route: ServerHookMap,
    /// A layered map of dynamic routes grouped by segment count.
    /// Routes are organized by path segment count for efficient filtering during matching.
    #[get]
    #[set(skip)]
    #[get_mut(pub(super))]
    #[debug(skip)]
    pub(super) dynamic_route: ServerHookPatternRoute,
    /// A layered map of regex routes grouped by segment count.
    /// Routes with tail regex patterns can match paths with more segments.
    #[get]
    #[set(skip)]
    #[get_mut(pub(super))]
    #[debug(skip)]
    pub(super) regex_route: ServerHookPatternRoute,
}

```

# Path: hyperlane\src\route\type.rs

```rust
use crate::*;

/// A type alias for a hash map that stores captured route parameters.
///
/// The key is the parameter name and the value is the captured string.
pub type RouteParams = HashMapXxHash3_64<String, String>;

/// A type alias for a list of route segments.
///
/// This is used to represent a parsed route.
pub type RouteSegmentList = Vec<RouteSegment>;

/// A type alias for a list of path components.
///
/// This is often used for path components.
pub(crate) type PathComponentList<'a> = Vec<&'a str>;

```

# Path: hyperlane\src\server\impl.rs

```rust
use crate::*;

/// Provides a default implementation for ServerInner.
impl Default for ServerInner {
    /// Creates a new ServerInner instance with default values.
    ///
    /// # Returns
    ///
    /// - `Self` - A new instance with default configuration.
    #[inline(always)]
    fn default() -> Self {
        Self {
            config: ServerConfigInner::default(),
            panic_hook: vec![],
            route_matcher: RouteMatcher::new(),
            request_middleware: vec![],
            response_middleware: vec![],
        }
    }
}

/// Implements the `PartialEq` trait for `ServerInner`.
///
/// This allows for comparing two `ServerInner` instances for equality.
impl PartialEq for ServerInner {
    /// Checks if two `ServerInner` instances are equal.
    ///
    /// # Arguments
    ///
    /// - `&Self`- The other `ServerInner` instance to compare against.
    ///
    /// # Returns
    ///
    /// - `bool`- `true` if the instances are equal, `false` otherwise.
    fn eq(&self, other: &Self) -> bool {
        self.config == other.config
            && self.route_matcher == other.route_matcher
            && self.panic_hook.len() == other.panic_hook.len()
            && self.request_middleware.len() == other.request_middleware.len()
            && self.response_middleware.len() == other.response_middleware.len()
            && self
                .panic_hook
                .iter()
                .zip(other.panic_hook.iter())
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

/// Implements the `Eq` trait for `ServerInner`.
///
/// This indicates that `ServerInner` has a total equality relation.
impl Eq for ServerInner {}

/// Implements the `PartialEq` trait for `Server`.
///
/// This allows for comparing two `Server` instances for equality.
impl PartialEq for Server {
    /// Checks if two `Server` instances are equal.
    ///
    /// # Arguments
    ///
    /// - `&Self`- The other `Server` instance to compare against.
    ///
    /// # Returns
    ///
    /// - `bool`- `true` if the instances are equal, `false` otherwise.
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

/// Implements the `Eq` trait for `Server`.
///
/// This indicates that `Server` has a total equality relation.
impl Eq for Server {}

/// Manages the state for handling a single connection, including the stream and context.
///
/// This struct provides a convenient way to pass around the necessary components
/// for processing a request or WebSocket frame.
impl HandlerState {
    /// Creates a new HandlerState instance.
    ///
    /// # Arguments
    ///
    /// - `&'a ArcRwLockStream` - The network stream.
    /// - `&'a Context` - The request context.
    /// - `RequestConfig` - The request config.
    ///
    /// # Returns
    ///
    /// - `Self` - The newly created handler state.
    #[inline(always)]
    pub(super) fn new(
        stream: ArcRwLockStream,
        ctx: Context,
        request_config: RequestConfig,
    ) -> Self {
        Self {
            stream,
            ctx,
            request_config,
        }
    }
}

/// Represents the server, providing methods to configure and run it.
///
/// This struct wraps the `ServerInner` configuration and routing logic,
/// offering a high-level API for setting up the HTTP and WebSocket server.
impl Server {
    /// Creates a new Server instance with default settings.
    ///
    /// # Returns
    ///
    /// - `Self` - A new Server instance.
    pub async fn new() -> Self {
        let server: ServerInner = ServerInner::default();
        Self(arc_rwlock(server))
    }

    /// Creates a new Server instance from a configuration.
    ///
    /// # Arguments
    ///
    /// - `ServerConfig` - The server configuration.
    ///
    /// # Returns
    ///
    /// - `Self` - A new Server instance.
    pub async fn from(config: ServerConfig) -> Self {
        let server: Self = Self::new().await;
        server.config(config).await;
        server
    }

    /// Acquires a read lock on the inner server data.
    ///
    /// # Returns
    ///
    /// - `ServerStateReadGuard` - The read guard for ServerInner.
    pub(super) async fn read(&self) -> ServerStateReadGuard<'_> {
        self.get_0().read().await
    }

    /// Acquires a write lock on the inner server data.
    ///
    /// # Returns
    ///
    /// - `ServerStateWriteGuard` - The write guard for ServerInner.
    async fn write(&self) -> ServerStateWriteGuard<'_> {
        self.get_0().write().await
    }

    /// Gets the route matcher.
    ///
    /// # Returns
    /// - `RouteMatcher` - The route matcher.
    pub async fn get_route_matcher(&self) -> RouteMatcher {
        self.read().await.get_route_matcher().clone()
    }

    /// Handle a given hook macro asynchronously.
    ///
    /// This function dispatches the provided `HookMacro` to the appropriate
    /// internal handler based on its `HookType`. Supported hook types include
    /// panic hooks, request/response middleware, and route.
    ///
    /// # Arguments
    ///
    /// - `HookMacro`- The `HookMacro` instance containing the `HookType` and its handler.
    pub async fn handle_hook(&self, hook: HookMacro) {
        match (hook.hook_type, hook.handler) {
            (HookType::PanicHook(_), HookHandlerSpec::Handler(handler)) => {
                self.write().await.get_mut_panic_hook().push(handler);
            }
            (HookType::PanicHook(_), HookHandlerSpec::Factory(factory)) => {
                self.write().await.get_mut_panic_hook().push(factory());
            }
            (HookType::RequestMiddleware(_), HookHandlerSpec::Handler(handler)) => {
                self.write()
                    .await
                    .get_mut_request_middleware()
                    .push(handler);
            }
            (HookType::RequestMiddleware(_), HookHandlerSpec::Factory(factory)) => {
                self.write()
                    .await
                    .get_mut_request_middleware()
                    .push(factory());
            }
            (HookType::Route(path), HookHandlerSpec::Handler(handler)) => {
                self.write()
                    .await
                    .get_mut_route_matcher()
                    .add(path, handler)
                    .unwrap();
            }
            (HookType::Route(path), HookHandlerSpec::Factory(factory)) => {
                self.write()
                    .await
                    .get_mut_route_matcher()
                    .add(path, factory())
                    .unwrap();
            }
            (HookType::ResponseMiddleware(_), HookHandlerSpec::Handler(handler)) => {
                self.write()
                    .await
                    .get_mut_response_middleware()
                    .push(handler);
            }
            (HookType::ResponseMiddleware(_), HookHandlerSpec::Factory(factory)) => {
                self.write()
                    .await
                    .get_mut_response_middleware()
                    .push(factory());
            }
        };
    }

    /// Sets the server configuration from a string.
    ///
    /// # Arguments
    ///
    /// - `C: ToString` - The configuration.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to self for method chaining.
    pub async fn config_str<C: ToString>(&self, config_str: C) -> &Self {
        let config: ServerConfig = ServerConfig::from_json_str(&config_str.to_string()).unwrap();
        self.write().await.set_config(config.get_inner().await);
        self
    }

    /// Sets the server configuration.
    ///
    /// # Arguments
    ///
    /// - `ServerConfig` - The server configuration.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to self for method chaining.
    pub async fn config(&self, config: ServerConfig) -> &Self {
        self.write().await.set_config(config.get_inner().await);
        self
    }

    /// Registers a panic hook handler to the processing pipeline.
    ///
    /// This method allows registering panic hooks that implement the `ServerHook` trait,
    /// which will be executed when a panic occurs during request processing.
    ///
    /// # Type Parameters
    ///
    /// - `ServerHook` - The panic hook type that implements `ServerHook`.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to self for method chaining.
    pub async fn panic_hook<S>(&self) -> &Self
    where
        S: ServerHook,
    {
        self.write()
            .await
            .get_mut_panic_hook()
            .push(server_hook_factory::<S>());
        self
    }

    /// Registers a route handler for a specific path.
    ///
    /// This method allows registering route handlers that implement the `ServerHook` trait,
    /// providing type safety and better code organization.
    ///
    /// # Type Parameters
    ///
    /// - `ServerHook` - The route handler type that implements `ServerHook`.
    ///
    /// # Arguments
    ///
    /// - `path` - The route path pattern.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to self for method chaining.
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

    /// Registers request middleware to the processing pipeline.
    ///
    /// This method allows registering middleware that implements the `ServerHook` trait,
    /// which will be executed before route handlers for every incoming request.
    ///
    /// # Type Parameters
    ///
    /// - `ServerHook` - The middleware type that implements `ServerHook`.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to self for method chaining.
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

    /// Registers response middleware to the processing pipeline.
    ///
    /// This method allows registering middleware that implements the `ServerHook` trait,
    /// which will be executed after route handlers for every outgoing response.
    ///
    /// # Type Parameters
    ///
    /// - `ServerHook` - The middleware type that implements `ServerHook`.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to self for method chaining.
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

    /// Formats the host and port into a bindable address string.
    ///
    /// # Arguments
    ///
    /// - `H: ToString` - The host address.
    /// - `u16` - The port number.
    ///
    /// # Returns
    ///
    /// - `String` - The formatted address string.
    #[inline(always)]
    pub fn format_host_port<H: ToString>(host: H, port: u16) -> String {
        format!("{}{COLON}{port}", host.to_string())
    }

    /// Flushes the standard output stream.
    ///
    /// # Returns
    ///
    /// - `io::Result<()>` - The result of the flush operation.
    #[inline(always)]
    pub fn try_flush_stdout() -> io::Result<()> {
        stdout().flush()
    }

    /// Flushes the standard error stream.
    ///
    /// # Panics
    ///
    /// This function will panic if the flush operation fails.
    #[inline(always)]
    pub fn flush_stdout() {
        stdout().flush().unwrap();
    }

    /// Flushes the standard error stream.
    ///
    /// # Returns
    ///
    /// - `io::Result<()>` - The result of the flush operation.
    #[inline(always)]
    pub fn try_flush_stderr() -> io::Result<()> {
        stderr().flush()
    }

    /// Flushes the standard error stream.
    ///
    /// # Panics
    ///
    /// This function will panic if the flush operation fails.
    #[inline(always)]
    pub fn flush_stderr() {
        stderr().flush().unwrap();
    }

    /// Flushes both the standard output and error streams.
    ///
    /// # Returns
    ///
    /// - `io::Result<()>` - The result of the flush operation.
    #[inline(always)]
    pub fn try_flush_stdout_and_stderr() -> io::Result<()> {
        Self::try_flush_stdout()?;
        Self::try_flush_stderr()
    }

    /// Flushes both the standard output and error streams.
    ///
    /// # Panics
    ///
    /// This function will panic if either flush operation fails.
    #[inline(always)]
    pub fn flush_stdout_and_stderr() {
        Self::flush_stdout();
        Self::flush_stderr();
    }

    /// Handles a panic that has been captured and associated with a specific request `Context`.
    ///
    /// This function is invoked when a panic occurs within a task that has access to the request
    /// context, such as a route handler or middleware. It ensures that the panic information is
    /// recorded in the `Context` and then passed to the server's configured panic hook for
    /// processing.
    ///
    /// By associating the panic with the context, the handler can access request-specific details
    /// to provide more meaningful error logging and responses.
    ///
    /// # Arguments
    ///
    /// - `&Context` - The context of the request during which the panic occurred.
    /// - `&Panic` - The captured panic information.
    async fn handle_panic_with_context(&self, ctx: &Context, panic: &Panic) {
        let panic_clone: Panic = panic.clone();
        ctx.cancel_aborted().await.set_panic(panic_clone).await;
        for hook in self.read().await.get_panic_hook().iter() {
            if let Err(join_error) = spawn(hook(ctx)).await
                && join_error.is_panic()
            {
                eprintln!("Panic occurred in panic hook: {:?}", join_error);
                let _ = Self::try_flush_stdout_and_stderr();
            }
            if ctx.get_aborted().await {
                return;
            }
        }
    }

    /// Handles a panic that occurred within a spawned Tokio task.
    ///
    /// It extracts the panic information from the `JoinError` and processes it.
    ///
    /// # Arguments
    ///
    /// - `&Context` - The context associated with the task.
    /// - `JoinError` - The `JoinError` returned from the panicked task.
    async fn handle_task_panic(&self, ctx: &Context, join_error: JoinError) {
        let panic: Panic = Panic::from_join_error(join_error);
        ctx.set_response_status_code(HttpStatus::InternalServerError.code())
            .await;
        self.handle_panic_with_context(ctx, &panic).await;
    }

    /// Executes a middleware handler and manages the request lifecycle.
    ///
    /// This function executes middleware with spawn to catch panics properly.
    /// While this adds some overhead, it's necessary to ensure panic hooks
    /// can send error responses to clients.
    ///
    /// # Arguments
    ///
    /// - `&Context` - The request context.
    /// - `&mut RequestLifecycle` - A mutable reference to the current request lifecycle state.
    /// - `&ServerHookHandler` - The middleware handler to execute.
    async fn handle_middleware_with_lifecycle(
        &self,
        ctx: &Context,
        lifecycle: &mut RequestLifecycle,
        handler: &ServerHookHandler,
    ) {
        ctx.update_lifecycle_status(lifecycle).await;
        if let Err(join_error) = spawn(handler(ctx)).await
            && join_error.is_panic()
        {
            self.handle_task_panic(ctx, join_error).await;
        }
    }

    /// Executes a route handler and manages the request lifecycle.
    ///
    /// This function executes the route handler with spawn to catch panics properly.
    /// While this adds some overhead, it's necessary to ensure panic hooks
    /// can send error responses to clients.
    ///
    /// # Arguments
    ///
    /// - `&Context` - The request context.
    /// - `&mut RequestLifecycle` - A mutable reference to the current request lifecycle state.
    /// - `&ServerHookHandler` - The route handler to execute.
    async fn handle_route_matcher_with_lifecycle(
        &self,
        ctx: &Context,
        lifecycle: &mut RequestLifecycle,
        handler: &ServerHookHandler,
    ) {
        ctx.update_lifecycle_status(lifecycle).await;
        if let Err(join_error) = spawn(handler(ctx)).await
            && join_error.is_panic()
        {
            self.handle_task_panic(ctx, join_error).await;
        }
    }

    /// Creates and binds a `TcpListener` based on the server's configuration.
    ///
    /// # Returns
    ///
    /// - `Result<TcpListener, ServerError>` - A `Result` containing the bound `TcpListener` on success,
    ///   or a `ServerError` on failure.
    async fn create_tcp_listener(&self) -> Result<TcpListener, ServerError> {
        let config: ServerConfigInner = self.read().await.get_config().clone();
        let host: String = config.get_host().clone();
        let port: u16 = *config.get_port();
        let addr: String = Self::format_host_port(host, port);
        TcpListener::bind(&addr)
            .await
            .map_err(|err| ServerError::TcpBind(err.to_string()))
    }

    /// Enters a loop to accept incoming TCP connections and spawn handlers for them.
    ///
    /// # Arguments
    ///
    /// - `&TcpListener` - A reference to the `TcpListener` to accept connections from.
    ///
    /// # Returns
    ///
    /// - `Result<(), ServerError>` - A `Result` which is typically `Ok(())` unless an unrecoverable
    ///   error occurs.
    async fn accept_connections(&self, tcp_listener: &TcpListener) -> Result<(), ServerError> {
        while let Ok((stream, _socket_addr)) = tcp_listener.accept().await {
            self.configure_stream(&stream).await;
            let stream: ArcRwLockStream = ArcRwLockStream::from_stream(stream);
            self.spawn_connection_handler(stream).await;
        }
        Ok(())
    }

    /// Configures socket options for a newly accepted `TcpStream`.
    ///
    /// This applies settings like `SO_LINGER`, `TCP_NODELAY`, and `IP_TTL` from the server's configuration.
    ///
    /// # Arguments
    ///
    /// - `&TcpStream` - A reference to the `TcpStream` to configure.
    async fn configure_stream(&self, stream: &TcpStream) {
        let server_inner: ServerStateReadGuard = self.read().await;
        let config: &ServerConfigInner = server_inner.get_config();
        stream.set_linger(*config.get_linger()).unwrap();
        if let Some(nodelay) = config.get_nodelay() {
            let _ = stream.set_nodelay(*nodelay);
        }
        if let Some(ttl) = config.get_ttl() {
            let _ = stream.set_ttl(*ttl);
        }
    }

    /// Spawns a new asynchronous task to handle a single client connection.
    ///
    /// # Arguments
    ///
    /// - `ArcRwLockStream` - The thread-safe stream representing the client connection.
    async fn spawn_connection_handler(&self, stream: ArcRwLockStream) {
        let server: Server = self.clone();
        let request_config: RequestConfig = *self.read().await.get_config().get_request_config();
        spawn(async move {
            server.handle_connection(stream, request_config).await;
        });
    }

    /// Handles a single client connection, determining whether it's an HTTP or WebSocket request.
    ///
    /// It reads the initial request from the stream and dispatches it to the appropriate handler.
    ///
    /// # Arguments
    ///
    /// - `ArcRwLockStream` - The stream for the client connection.
    /// - `request_config` - The request config to use for reading the initial HTTP request.
    async fn handle_connection(&self, stream: ArcRwLockStream, request_config: RequestConfig) {
        match Request::http_from_stream(&stream, &request_config).await {
            Ok(request) => {
                let ctx: Context = Context::new(&stream, &request);
                let handler: HandlerState = HandlerState::new(stream, ctx, request_config);
                self.handle_http_requests(&handler, &request).await;
            }
            Err(err) => {
                let ctx: Context = Context::new(&stream, &Request::default());
                self.handle_http_requests_error(&ctx, &err).await;
            }
        }
    }

    /// The core request handling pipeline.
    ///
    /// This function orchestrates the execution of request middleware, the route handler,
    /// and response middleware. It supports both function-based and trait-based handlers.
    ///
    /// # Arguments
    ///
    /// - `&HandlerState` - The `HandlerState` for the current connection.
    /// - `&Request` - The incoming request to be processed.
    ///
    /// # Returns
    ///
    /// - `bool` - A boolean indicating whether the connection should be kept alive.
    async fn request_hook(&self, state: &HandlerState, request: &Request) -> bool {
        let route: &str = request.get_path();
        let ctx: &Context = state.get_ctx();
        ctx.set_request(request).await;
        let mut lifecycle: RequestLifecycle = RequestLifecycle::new(request.is_enable_keep_alive());
        if self.handle_request_middleware(ctx, &mut lifecycle).await {
            return lifecycle.keep_alive();
        }
        if self.handle_route_matcher(ctx, route, &mut lifecycle).await {
            return lifecycle.keep_alive();
        }
        if self.handle_response_middleware(ctx, &mut lifecycle).await {
            return lifecycle.keep_alive();
        }
        if let Some(panic) = ctx.try_get_panic().await {
            ctx.set_response_status_code(HttpStatus::InternalServerError.code())
                .await;
            self.handle_panic_with_context(ctx, &panic).await;
        }
        lifecycle.keep_alive()
    }

    /// Handles subsequent HTTP requests on a persistent (keep-alive) connection.
    ///
    /// # Arguments
    ///
    /// - `&HandlerState` - The `HandlerState` for the current connection.
    /// - `&Request` - The initial request that established the keep-alive connection.
    async fn handle_http_requests(&self, state: &HandlerState, request: &Request) {
        if !self.request_hook(state, request).await {
            return;
        }
        let stream: &ArcRwLockStream = state.get_stream();
        let request_config: RequestConfig = *state.get_request_config();
        loop {
            match Request::http_from_stream(stream, &request_config).await {
                Ok(new_request) => {
                    if !self.request_hook(state, &new_request).await {
                        return;
                    }
                }
                Err(err) => {
                    Self::flush_stdout_and_stderr();
                    self.handle_http_requests_error(state.get_ctx(), &err).await;
                    break;
                }
            }
        }
    }

    /// Handles errors that occur while processing HTTP requests.
    ///
    /// # Arguments
    ///
    /// - `&Context` - The request context.
    /// - `&RequestError` - The error that occurred.
    pub async fn handle_http_requests_error(&self, ctx: &Context, err: &RequestError) {
        let mut panic: Panic = Panic::default();
        panic.set_message(Some(err.to_string()));
        ctx.set_response_status_code(err.get_http_status_code())
            .await;
        self.handle_panic_with_context(ctx, &panic).await;
    }

    /// Executes trait-based request middleware in sequence.
    ///
    /// # Arguments
    ///
    /// - `&Context` - The request context.
    /// - `&mut RequestLifecycle` - A mutable reference to the request lifecycle state.
    ///
    /// # Returns
    ///
    /// - `bool` - `true` if the lifecycle was aborted, `false` otherwise.
    pub(super) async fn handle_request_middleware(
        &self,
        ctx: &Context,
        lifecycle: &mut RequestLifecycle,
    ) -> bool {
        for handler in self.read().await.get_request_middleware().iter() {
            self.handle_middleware_with_lifecycle(ctx, lifecycle, handler)
                .await;
            if lifecycle.is_aborted() {
                return true;
            }
        }
        false
    }

    /// Executes a trait-based route handler if one matches.
    ///
    /// # Arguments
    ///
    /// - `&Context` - The request context.
    /// - `&str` - The request path to match.
    /// - `&mut RequestLifecycle` - A mutable reference to the request lifecycle state.
    ///
    /// # Returns
    ///
    /// - `bool` - `true` if the lifecycle was aborted, `false` otherwise.
    pub(super) async fn handle_route_matcher(
        &self,
        ctx: &Context,
        path: &str,
        lifecycle: &mut RequestLifecycle,
    ) -> bool {
        if let Some(handler) = self
            .read()
            .await
            .get_route_matcher()
            .try_resolve_route(ctx, path)
            .await
        {
            self.handle_route_matcher_with_lifecycle(ctx, lifecycle, &handler)
                .await;
            if lifecycle.is_aborted() {
                return true;
            }
        }
        false
    }

    /// Executes trait-based response middleware in sequence.
    ///
    /// # Arguments
    ///
    /// - `&Context` - The request context.
    /// - `&mut RequestLifecycle` - A mutable reference to the request lifecycle state.
    ///
    /// # Returns
    ///
    /// - `bool` - `true` if the lifecycle was aborted, `false` otherwise.
    pub(super) async fn handle_response_middleware(
        &self,
        ctx: &Context,
        lifecycle: &mut RequestLifecycle,
    ) -> bool {
        for handler in self.read().await.get_response_middleware().iter() {
            self.handle_middleware_with_lifecycle(ctx, lifecycle, handler)
                .await;
            if lifecycle.is_aborted() {
                return true;
            }
        }
        false
    }

    /// Starts the server, binds to the configured address, and begins listening for connections.
    ///
    /// This is the main entry point to launch the server. It will initialize the panic hook,
    /// create a TCP listener, and then enter the connection acceptance loop in a background task.
    ///
    /// # Returns
    ///
    /// Returns a `Result` containing a shutdown function on success.
    /// Calling this function will shut down the server by aborting its main task.
    /// Returns an error if the server fails to start.
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

# Path: hyperlane\src\server\mod.rs

```rust
pub(crate) mod r#impl;
pub(crate) mod r#struct;
pub(crate) mod r#type;

pub use r#struct::*;

pub(crate) use r#type::*;

```

# Path: hyperlane\src\server\struct.rs

```rust
use crate::*;

/// Represents the state associated with a single connection handler.
///
/// This struct encapsulates the necessary context for processing a connection,
/// including a reference to the network stream and the request context. It is created
/// for each connection and passed to the relevant handlers.
#[derive(Clone, CustomDebug, DisplayDebug, Getter)]
pub(crate) struct HandlerState {
    /// A reference to the underlying network stream for the connection.
    pub(super) stream: ArcRwLockStream,
    /// A reference to the context of the current request.
    pub(super) ctx: Context,
    /// The request config for the current connection.
    pub(super) request_config: RequestConfig,
}

/// Represents the internal, mutable state of the web server.
///
/// This struct consolidates all the core components required for the server to operate,
/// including configuration, routing, middleware, and various hooks for extending functionality.
/// It is not intended to be used directly by end-users, but rather wrapped within the `Server` struct
/// for thread-safe access.
#[derive(Data, Clone, CustomDebug, DisplayDebug)]
pub(crate) struct ServerInner {
    /// Stores the server's configuration settings, such as address, port, and timeouts.
    #[get(pub(super))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    pub(super) config: ServerConfigInner,
    /// The routing component responsible for matching incoming requests to their registered handlers.
    #[get(pub(super))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    pub(super) route_matcher: RouteMatcher,
    /// A collection of panic hook handlers that are invoked when a panic occurs during request processing.
    /// This allows for graceful error recovery and customized error responses.
    #[debug(skip)]
    #[get(pub(super))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    pub(super) panic_hook: ServerHookList,
    /// A collection of request middleware handlers.
    #[debug(skip)]
    #[get(pub(super))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    pub(super) request_middleware: ServerHookList,
    /// A collection of response middleware handlers.
    #[debug(skip)]
    #[get(pub(super))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    pub(super) response_middleware: ServerHookList,
}

/// The primary server structure that provides a thread-safe interface to the server's state.
///
/// This struct acts as a public-facing wrapper around an `Arc<RwLock<ServerInner>>`.
/// It allows multiple parts of the application to safely share and modify the server's
/// configuration and state across different threads and asynchronous tasks.
#[derive(Clone, Getter, CustomDebug, DisplayDebug, Default)]
pub struct Server(#[get(pub(super))] pub(super) SharedServerState);

```

# Path: hyperlane\src\server\type.rs

```rust
use crate::*;

/// A type alias for shared server state.
///
/// This is the core mechanism for sharing server state across threads.
pub(crate) type SharedServerState = ArcRwLock<ServerInner>;

/// A type alias for shared server configuration.
///
/// This is the core mechanism for sharing server config state across threads.
pub(crate) type SharedServerConfig = ArcRwLock<ServerConfigInner>;

/// A type alias for server state read guard.
///
/// This provides read-only access to the server's internal state.
pub(crate) type ServerStateReadGuard<'a> = RwLockReadGuard<'a, ServerInner>;

/// A type alias for server state write guard.
///
/// This provides mutable access to the server's internal state.
pub(crate) type ServerStateWriteGuard<'a> = RwLockWriteGuard<'a, ServerInner>;

```

# Path: hyperlane\src\tests\attribute.rs

```rust
use crate::*;

#[tokio::test]
async fn get_panic_from_context() {
    let ctx: Context = Context::default();
    let set_panic: Panic = Panic::new(
        Some("test".to_string()),
        Some("test".to_string()),
        Some("test".to_string()),
    );
    ctx.set_panic(set_panic.clone()).await;
    let get_panic: Panic = ctx.try_get_panic().await.unwrap();
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
    let panic_struct: Panic = Panic::from_join_error(join_error);
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

# Path: hyperlane\src\tests\config.rs

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
                "ws_read_timeout_ms": 6000
            },
            "nodelay": true,
            "linger": { "secs": 64, "nanos": 0 },
            "ttl": 64
        }
    "#;
    let config: ServerConfig = ServerConfig::from_json_str(config_str).unwrap();
    let new_config: ServerConfig = ServerConfig::new().await;
    new_config.host("0.0.0.0").await;
    new_config.port(80).await;
    new_config.request_config(RequestConfig::default()).await;
    new_config.enable_nodelay().await;
    new_config.linger(Some(Duration::from_secs(64))).await;
    new_config.ttl(64).await;
    assert_eq!(config, new_config);
}

```

# Path: hyperlane\src\tests\context.rs

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

# Path: hyperlane\src\tests\error.rs

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

# Path: hyperlane\src\tests\lifecycle.rs

```rust
use crate::*;

#[tokio::test]
async fn lifecycle_new() {
    let lifecycle: RequestLifecycle = RequestLifecycle::new(true);
    assert_eq!(lifecycle, RequestLifecycle::Continuing(true));
    assert!(lifecycle.is_keep_alive());
    assert!(!lifecycle.is_aborted());
}

#[tokio::test]
async fn lifecycle_update_status() {
    let mut lifecycle: RequestLifecycle = RequestLifecycle::new(true);
    lifecycle.update_status(true, true);
    assert_eq!(lifecycle, RequestLifecycle::Aborted(true));
    assert!(lifecycle.is_aborted());
    assert!(lifecycle.is_keep_alive());
    lifecycle.update_status(true, false);
    assert_eq!(lifecycle, RequestLifecycle::Aborted(false));
    assert!(lifecycle.is_aborted());
    assert!(!lifecycle.is_keep_alive());
    lifecycle.update_status(false, true);
    assert_eq!(lifecycle, RequestLifecycle::Continuing(true));
    assert!(!lifecycle.is_aborted());
    assert!(lifecycle.is_keep_alive());
    lifecycle.update_status(false, false);
    assert_eq!(lifecycle, RequestLifecycle::Continuing(false));
    assert!(!lifecycle.is_aborted());
    assert!(!lifecycle.is_keep_alive());
}

#[tokio::test]
async fn lifecycle_is_aborted() {
    let abort_true: RequestLifecycle = RequestLifecycle::Aborted(true);
    assert!(abort_true.is_aborted());
    let abort_false: RequestLifecycle = RequestLifecycle::Aborted(false);
    assert!(abort_false.is_aborted());
    let continue_true: RequestLifecycle = RequestLifecycle::Continuing(true);
    assert!(!continue_true.is_aborted());
    let continue_false: RequestLifecycle = RequestLifecycle::Continuing(false);
    assert!(!continue_false.is_aborted());
}

#[tokio::test]
async fn lifecycle_is_keep_alive() {
    let abort_true: RequestLifecycle = RequestLifecycle::Aborted(true);
    assert!(abort_true.is_keep_alive());
    let abort_false: RequestLifecycle = RequestLifecycle::Aborted(false);
    assert!(!abort_false.is_keep_alive());
    let continue_true: RequestLifecycle = RequestLifecycle::Continuing(true);
    assert!(continue_true.is_keep_alive());
    let continue_false: RequestLifecycle = RequestLifecycle::Continuing(false);
    assert!(!continue_false.is_keep_alive());
}

#[tokio::test]
async fn lifecycle_keep_alive() {
    let abort_true: RequestLifecycle = RequestLifecycle::Aborted(true);
    assert!(abort_true.keep_alive());
    let abort_false: RequestLifecycle = RequestLifecycle::Aborted(false);
    assert!(!abort_false.keep_alive());
    let continue_true: RequestLifecycle = RequestLifecycle::Continuing(true);
    assert!(continue_true.keep_alive());
    let continue_false: RequestLifecycle = RequestLifecycle::Continuing(false);
    assert!(!continue_false.keep_alive());
}

```

# Path: hyperlane\src\tests\mod.rs

```rust
mod attribute;
mod config;
mod context;
mod error;
mod lifecycle;
mod panic;
mod route;
mod send;
mod server;

```

# Path: hyperlane\src\tests\panic.rs

```rust
use crate::*;

#[test]
fn panic_new() {
    let panic: Panic = Panic::new(
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
        let is_panic: bool = Panic::from_join_error(join_error)
            .get_message()
            .clone()
            .unwrap_or_default()
            .contains("test panic");
        assert!(is_panic);
    }
}

```

# Path: hyperlane\src\tests\route.rs

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

# Path: hyperlane\src\tests\send.rs

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

# Path: hyperlane\src\tests\server.rs

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

#[tokio::test]
async fn test_server() {
    struct UpgradeMiddleware;
    struct SendBodyMiddleware {
        socket_addr: String,
    }
    struct ResponseMiddleware;
    struct ServerPanicHook {
        response_body: String,
        content_type: String,
    }
    struct RootRoute {
        response_body: String,
        cookie1: String,
        cookie2: String,
    }
    struct SseRoute;
    struct WebsocketRoute;
    struct DynamicRoute {
        params: RouteParams,
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
                    .await
                    .unwrap();
            }
        }
    }

    impl ServerHook for ResponseMiddleware {
        async fn new(_ctx: &Context) -> Self {
            Self
        }

        async fn handle(self, ctx: &Context) {
            if ctx.get_request().await.is_ws() {
                return;
            }
            let _ = ctx.send().await;
        }
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

    impl WebsocketRoute {
        async fn send_body_hook(&self, ctx: &Context) {
            let body: ResponseBody = ctx.get_response_body().await;
            if ctx.get_request().await.is_ws() {
                let frame_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(&body);
                ctx.send_body_list_with_data(&frame_list).await.unwrap();
            } else {
                ctx.send_body().await.unwrap();
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
                    Err(err) => {
                        ctx.set_response_body(&err.to_string()).await;
                        self.send_body_hook(ctx).await;
                        break;
                    }
                }
            }
        }
    }

    impl ServerHook for SseRoute {
        async fn new(_ctx: &Context) -> Self {
            Self
        }

        async fn handle(self, ctx: &Context) {
            let _ = ctx
                .set_response_header(CONTENT_TYPE, TEXT_EVENT_STREAM)
                .await
                .send()
                .await;
            for i in 0..10 {
                let _ = ctx
                    .set_response_body(&format!("data:{}{}", i, HTTP_DOUBLE_BR))
                    .await
                    .send_body()
                    .await;
            }
            let _ = ctx.closed().await;
        }
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

    impl ServerHook for ServerPanicHook {
        async fn new(ctx: &Context) -> Self {
            let error: Panic = ctx.try_get_panic().await.unwrap_or_default();
            let response_body: String = error.to_string();
            let content_type: String =
                ContentType::format_content_type_with_charset(TEXT_PLAIN, UTF8);
            Self {
                response_body,
                content_type,
            }
        }

        async fn handle(self, ctx: &Context) {
            let _ = ctx
                .set_response_version(HttpVersion::Http1_1)
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

    async fn main() {
        let config: ServerConfig = ServerConfig::new().await;
        config.host("0.0.0.0").await;
        config.port(60000).await;
        config.request_config(RequestConfig::default()).await;
        config.disable_linger().await;
        config.disable_nodelay().await;
        let server: Server = Server::from(config).await;
        server.request_middleware::<SendBodyMiddleware>().await;
        server.request_middleware::<UpgradeMiddleware>().await;
        server.response_middleware::<ResponseMiddleware>().await;
        server.panic_hook::<ServerPanicHook>().await;
        server.route::<RootRoute>("/").await;
        server.route::<WebsocketRoute>("/websocket").await;
        server.route::<SseRoute>("/sse").await;
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

    main().await;
}

```

# Path: hyperlane-broadcast\README.md


## hyperlane-broadcast

[Official Documentation](https://docs.ltpp.vip/hyperlane-broadcast/)

[Api Docs](https://docs.rs/hyperlane-broadcast/latest/hyperlane_broadcast/)

> hyperlane-broadcast is a lightweight and ergonomic wrapper over Tokio’s broadcast channel designed for easy-to-use publish-subscribe messaging in async Rust applications. It simplifies the native Tokio broadcast API by providing a straightforward interface for broadcasting messages to multiple subscribers with minimal boilerplate.

## Installation

To use this crate, you can run cmd:

```shell
cargo add hyperlane-broadcast
```

## Use

```rust
use hyperlane_broadcast::*;

let broadcast: Broadcast<usize> = Broadcast::new(10);
let mut rec1: BroadcastReceiver<usize> = broadcast.subscribe();
let mut rec2: BroadcastReceiver<usize> = broadcast.subscribe();
broadcast.send(20).unwrap();
assert_eq!(rec1.recv().await, Ok(20));
assert_eq!(rec2.recv().await, Ok(20));

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
```

## Contact


# Path: hyperlane-broadcast\src\cfg.rs

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

# Path: hyperlane-broadcast\src\lib.rs

```rust
//! hyperlane-broadcast
//!
//! hyperlane-broadcast is a lightweight
//! and ergonomic wrapper over Tokio’s broadcast channel designed
//! for easy-to-use publish-subscribe messaging in async Rust applications.
//! It simplifies the native Tokio broadcast API by providing a straightforward
//! interface for broadcasting messages to multiple subscribers with minimal boilerplate.

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

# Path: hyperlane-broadcast\src\broadcast\const.rs

```rust
/// Defines the default capacity for a broadcast sender.
///
/// This constant specifies the initial buffer size for messages awaiting delivery
/// to receivers in a broadcast channel.
pub const DEFAULT_BROADCAST_SENDER_CAPACITY: usize = 1024;

```

# Path: hyperlane-broadcast\src\broadcast\impl.rs

```rust
use crate::*;

/// Implements the `BroadcastTrait` for any type that also implements `Clone` and `Debug`.
/// This blanket implementation allows any clonable and debuggable type to be used in the broadcast system.
impl<T: Clone + Debug> BroadcastTrait for T {}

/// Provides a default implementation for `Broadcast` instances.
///
/// The default broadcast channel is initialized with a predefined sender capacity.
impl<T: BroadcastTrait> Default for Broadcast<T> {
    /// Creates a new `Broadcast` instance with default settings.
    ///
    /// # Returns
    ///
    /// - `Broadcast<T>` - A broadcast instance with default sender capacity.
    #[inline(always)]
    fn default() -> Self {
        let sender: BroadcastSender<T> = BroadcastSender::new(DEFAULT_BROADCAST_SENDER_CAPACITY);
        Self(sender)
    }
}

/// Implements core functionalities for the `Broadcast` struct.
impl<T: BroadcastTrait> Broadcast<T> {
    /// Creates a new `Broadcast` instance with a specified capacity.
    ///
    /// # Arguments
    ///
    /// - `Capacity` - The maximum number of messages that can be buffered.
    ///
    /// # Returns
    ///
    /// - `Broadcast<T>` - A new broadcast instance.
    #[inline(always)]
    pub fn new(capacity: Capacity) -> Self {
        let sender: BroadcastSender<T> = BroadcastSender::new(capacity);
        Self(sender)
    }

    /// Retrieves the current number of active receivers subscribed to this broadcast channel.
    ///
    /// # Returns
    ///
    /// - `ReceiverCount` - The total count of active receivers.
    #[inline(always)]
    pub fn receiver_count(&self) -> ReceiverCount {
        self.0.receiver_count()
    }

    /// Subscribes a new receiver to the broadcast channel.
    ///
    /// # Returns
    ///
    /// - `BroadcastReceiver<T>` - A new receiver instance.
    #[inline(always)]
    pub fn subscribe(&self) -> BroadcastReceiver<T> {
        self.0.subscribe()
    }

    /// Sends a message to all active receivers subscribed to this broadcast channel.
    ///
    /// # Arguments
    ///
    /// - `T` - The message to be broadcasted.
    ///
    /// # Returns
    ///
    /// - `BroadcastSendResult<T>` - Result indicating send status.
    #[inline(always)]
    pub fn send(&self, data: T) -> BroadcastSendResult<T> {
        self.0.send(data)
    }
}

```

# Path: hyperlane-broadcast\src\broadcast\mod.rs

```rust
pub mod r#const;
pub mod r#impl;
pub mod r#struct;
pub mod r#trait;
pub mod r#type;

```

# Path: hyperlane-broadcast\src\broadcast\struct.rs

```rust
use crate::*;

/// Represents a broadcast mechanism for sending messages to multiple receivers.
///
/// This struct encapsulates the core components required for broadcasting,
/// including the capacity of the broadcast channel and the sender responsible
/// for dispatching messages.
#[derive(Debug, Clone)]
pub struct Broadcast<T: BroadcastTrait>(pub(super) BroadcastSender<T>);

```

# Path: hyperlane-broadcast\src\broadcast\trait.rs

```rust
use crate::*;

/// Defines the essential traits required for types that can be broadcast.
///
/// Any type implementing `BroadcastTrait` must also implement `Clone` and `Debug`,
/// enabling efficient duplication and debugging within the broadcast system.
pub trait BroadcastTrait: Clone + Debug {}

```

# Path: hyperlane-broadcast\src\broadcast\type.rs

```rust
use crate::*;

/// Represents the number of active receivers subscribed to a broadcast channel.
pub type ReceiverCount = usize;

/// Represents an error that occurs when attempting to send a message via broadcast.
pub type BroadcastSendError<T> = SendError<T>;

/// Represents the result of a broadcast send operation, indicating either success with the number of receivers or an error.
pub type BroadcastSendResult<T> = Result<ReceiverCount, BroadcastSendError<T>>;

/// Represents a receiver endpoint for a broadcast channel, allowing consumption of broadcasted messages.
pub type BroadcastReceiver<T> = Receiver<T>;

/// Represents a sender endpoint for a broadcast channel, used to dispatch messages to all subscribed receivers.
pub type BroadcastSender<T> = Sender<T>;

/// Represents the maximum capacity or buffer size of a broadcast channel.
pub type Capacity = usize;

```

# Path: hyperlane-broadcast\src\broadcast_map\impl.rs

```rust
use crate::*;

/// Implements the `BroadcastMapTrait` for any type that also implements `Clone` and `Debug`.
/// This blanket implementation allows any clonable and debuggable type to be used as a value in the broadcast map system.
impl<T: Clone + Debug> BroadcastMapTrait for T {}

/// Provides a default implementation for `BroadcastMap` instances.
///
/// The default broadcast map is initialized as an empty `DashMap`.
impl<T: BroadcastMapTrait> Default for BroadcastMap<T> {
    /// Creates a new, empty `BroadcastMap` instance.
    ///
    /// # Returns
    ///
    /// - `BroadcastMap<T>` - An empty broadcast map.
    #[inline(always)]
    fn default() -> Self {
        Self(DashMap::with_hasher(BuildHasherDefault::default()))
    }
}

/// Implements core functionalities for the `BroadcastMap` struct.
impl<T: BroadcastMapTrait> BroadcastMap<T> {
    /// Creates a new, empty `BroadcastMap` instance.
    ///
    /// This is a convenience constructor that simply calls `default()`.
    ///
    /// # Returns
    ///
    /// - `BroadcastMap<T>` - An empty broadcast map.
    #[inline(always)]
    pub fn new() -> Self {
        Self::default()
    }

    /// Retrieves an immutable reference to the underlying `DashMapStringBroadcast`.
    ///
    /// This private helper method provides direct access to the internal map.
    ///
    /// # Returns
    ///
    /// - `&DashMapStringBroadcast<T>` - Reference to the internal map.
    #[inline(always)]
    fn get(&self) -> &DashMapStringBroadcast<T> {
        &self.0
    }

    /// Inserts a new broadcast channel into the map with a specified key and capacity.
    ///
    /// If a broadcast channel with the given key already exists, it will be replaced.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - Key convertible to `str`.
    /// - `capacity` - Maximum number of buffered messages.
    ///
    /// # Returns
    ///
    /// - `Option<Broadcast<T>>` - Previous broadcast channel if replaced.
    #[inline(always)]
    pub fn insert<K>(&self, key: K, capacity: Capacity) -> OptionBroadcast<T>
    where
        K: AsRef<str>,
    {
        let broadcast: Broadcast<T> = Broadcast::new(capacity);
        self.get().insert(key.as_ref().to_owned(), broadcast)
    }

    /// Retrieves the number of active receivers for the broadcast channel associated with the given key.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - Key convertible to `str`.
    ///
    /// # Returns
    ///
    /// - `Option<ReceiverCount>` - Number of receivers if channel exists.
    #[inline(always)]
    pub fn receiver_count<K>(&self, key: K) -> OptionReceiverCount
    where
        K: AsRef<str>,
    {
        self.get()
            .get(key.as_ref())
            .map(|receiver| receiver.receiver_count())
    }

    /// Subscribes a new receiver to the broadcast channel associated with the given key.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - Key convertible to `str`.
    ///
    /// # Returns
    ///
    /// - `Option<BroadcastReceiver<T>>` - New receiver if channel exists.
    #[inline(always)]
    pub fn subscribe<K>(&self, key: K) -> OptionBroadcastMapReceiver<T>
    where
        K: AsRef<str>,
    {
        self.get()
            .get(key.as_ref())
            .map(|receiver| receiver.subscribe())
    }

    /// Subscribes a new receiver to the broadcast channel associated with the given key.
    /// If the channel does not exist, it will be created with the specified capacity before subscribing.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - Key convertible to `str`.
    /// - `capacity` - Capacity for new channel if needed.
    ///
    /// # Returns
    ///
    /// - `BroadcastReceiver<T>` - New receiver for the channel.
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

    /// Sends a message to the broadcast channel associated with the given key.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - Key convertible to `str`.
    /// - `data` - Message to broadcast.
    ///
    /// # Returns
    ///
    /// - `Result<Option<ReceiverCount>, SendError<T>>` - Send result with receiver count or error.
    #[inline(always)]
    pub fn send<K: AsRef<str>>(&self, key: K, data: T) -> BroadcastMapSendResult<T> {
        match self.get().get(key.as_ref()) {
            Some(sender) => sender.send(data).map(Some),
            None => Ok(None),
        }
    }
}

```

# Path: hyperlane-broadcast\src\broadcast_map\mod.rs

```rust
pub mod r#impl;
pub mod r#struct;
pub mod r#trait;
pub mod r#type;

```

# Path: hyperlane-broadcast\src\broadcast_map\struct.rs

```rust
use crate::*;

/// Represents a concurrent, thread-safe map of broadcast channels, keyed by string.
///
/// This struct provides a way to manage multiple broadcast channels, each identified by a unique string,
/// allowing for dynamic creation, retrieval, and management of broadcast streams.
#[derive(Debug, Clone)]
pub struct BroadcastMap<T: BroadcastTrait>(pub(super) DashMapStringBroadcast<T>);

```

# Path: hyperlane-broadcast\src\broadcast_map\trait.rs

```rust
use crate::*;

/// Defines the essential traits required for types that can be used as values in a `BroadcastMap`.
///
/// Any type implementing `BroadcastMapTrait` must also implement `Clone` and `Debug`,
/// enabling efficient duplication and debugging within the broadcast map system.
pub trait BroadcastMapTrait: Clone + Debug {}

```

# Path: hyperlane-broadcast\src\broadcast_map\type.rs

```rust
use crate::*;

/// Represents an error that occurs when attempting to send a message via a broadcast channel within a map.
pub type BroadcastMapSendError<T> = SendError<T>;

/// Represents the result of a broadcast map send operation, indicating either success with an optional receiver count or an error.
pub type BroadcastMapSendResult<T> = Result<Option<ReceiverCount>, BroadcastMapSendError<T>>;

/// Represents a receiver endpoint for a broadcast channel within a map, allowing consumption of broadcasted messages.
pub type BroadcastMapReceiver<T> = Receiver<T>;

/// Represents an optional broadcast channel.
pub type OptionBroadcast<T> = Option<Broadcast<T>>;

/// Represents an optional receiver endpoint for a broadcast channel within a map.
pub type OptionBroadcastMapReceiver<T> = Option<BroadcastMapReceiver<T>>;

/// Represents a sender endpoint for a broadcast channel within a map, used to dispatch messages.
pub type BroadcastMapSender<T> = Sender<T>;

/// Represents an optional sender endpoint for a broadcast channel within a map.
pub type OptionBroadcastMapSender<T> = Option<BroadcastMapSender<T>>;

/// Represents an optional count of active receivers.
pub type OptionReceiverCount = Option<ReceiverCount>;

/// A concurrent, thread-safe map where keys are strings and values are broadcast channels.
pub type DashMapStringBroadcast<T> = DashMap<String, Broadcast<T>, BuildHasherDefault<XxHash3_64>>;

```

# Path: hyperlane-log\README.md


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

## Use sync

```rust
use hyperlane_log::*;

let log: Log = Log::new("./logs", 1_024_000);
log.error("error data!", |error| {
    let write_data: String = format!("User error func => {:?}\n", error);
    write_data
});
log.error(String::from("error data!"), |error| {
    let write_data: String = format!("User error func => {:?}\n", error);
    write_data
});
log.info("info data!", |info| {
    let write_data: String = format!("User info func => {:?}\n", info);
    write_data
});
log.info(String::from("info data!"), |info| {
    let write_data: String = format!("User info func => {:?}\n", info);
    write_data
});
log.debug("debug data!", |debug| {
    let write_data: String = format!("User debug func => {:#?}\n", debug);
    write_data
});
log.debug(String::from("debug data!"), |debug| {
    let write_data: String = format!("User debug func => {:#?}\n", debug);
    write_data
});
```

## Use async

```rust
use hyperlane_log::*;

let log: Log = Log::new("./logs", 1_024_000);
log.async_error("async error data!", |error| {
    let write_data: String = format!("User error func => {:?}\n", error);
    write_data
}).await;
log.async_error(String::from("async error data!"), |error| {
    let write_data: String = format!("User error func => {:?}\n", error);
    write_data
}).await;
log.async_info("async info data!", |info| {
    let write_data: String = format!("User info func => {:?}\n", info);
    write_data
}).await;
log.async_info(String::from("async info data!"), |info| {
    let write_data: String = format!("User info func => {:?}\n", info);
    write_data
}).await;
log.async_debug("async debug data!", |debug| {
    let write_data: String = format!("User debug func => {:#?}\n", debug);
    write_data
}).await;
log.async_debug(String::from("async debug data!"), |debug| {
    let write_data: String = format!("User debug func => {:#?}\n", debug);
    write_data
}).await;
```

## Disable log

```rust
let log: Log = Log::new("./logs", DISABLE_LOG_FILE_SIZE);
```

## Contact


# Path: hyperlane-log\src\cfg.rs

```rust
#[cfg(test)]
#[tokio::test]
async fn test() {
    use crate::*;
    let log: Log = Log::new("./logs", 1_024_000);
    let error_str: String = String::from("custom error message");
    log.error(error_str, |error| {
        let write_data: String = format!("User error func => {error:?}\n");
        write_data
    });
    let info_str: String = String::from("custom info message");
    log.info(info_str, |info| {
        let write_data: String = format!("User info func => {info:?}\n");
        write_data
    });
    let debug_str: String = String::from("custom debug message");
    log.debug(debug_str, |debug| {
        let write_data: String = format!("User debug func => {debug:#?}\n");
        write_data
    });
    let async_error_str: String = String::from("custom async error message");
    log.async_error(async_error_str, |error| {
        let write_data: String = format!("User error func => {error:?}\n");
        write_data
    })
    .await;
    let async_info_str: String = String::from("custom async info message");
    log.async_info(async_info_str, |info| {
        let write_data: String = format!("User info func => {info:?}\n");
        write_data
    })
    .await;
    let async_debug_str: String = String::from("custom async debug message");
    log.async_debug(async_debug_str, |debug| {
        let write_data: String = format!("User debug func => {debug:#?}\n");
        write_data
    })
    .await;
}

#[cfg(test)]
#[tokio::test]
async fn test_more_log_first() {
    use crate::*;
    let log: Log = Log::new("./logs", DISABLE_LOG_FILE_SIZE);
    log.error("error data => ", |error| {
        let write_data: String = format!("User error func => {error:?}\n");
        write_data
    });
    log.info("info data => ", |info| {
        let write_data: String = format!("User info func => {info:?}\n");
        write_data
    });
    log.debug("debug data => ", |debug| {
        let write_data: String = format!("User debug func => {debug:#?}\n");
        write_data
    });
    log.async_error("async error data => ", |error| {
        let write_data: String = format!("User error func => {error:?}\n");
        write_data
    })
    .await;
    log.async_info("async info data => ", |info| {
        let write_data: String = format!("User info func => {info:?}\n");
        write_data
    })
    .await;
    log.async_debug("async debug data => ", |debug| {
        let write_data: String = format!("User debug func => {debug:#?}\n");
        write_data
    })
    .await;
}

#[cfg(test)]
#[tokio::test]
async fn test_more_log_second() {
    use crate::*;
    for _ in 0..10 {
        let log: Log = Log::new("./logs", 512_000);
        log.error("error data!\n", common_log);
        log.async_error("async error data!\n", common_log).await;
    }
}

```

# Path: hyperlane-log\src\lib.rs

```rust
//! hyperlane-log
//!
//! A Rust logging library that supports both asynchronous and synchronous logging.
//! It provides multiple log levels, such as error, info, and debug.
//! Users can define custom log handling methods and configure log file paths.
//! The library supports log rotation, automatically creating a new log file
//! when the current file reaches the specified size limit.
//! It allows flexible logging configurations, making it suitable for
//! both high-performance asynchronous applications and
//! traditional synchronous logging scenarios. The asynchronous mode utilizes
//! Tokio's async channels for efficient log buffering,
//! while the synchronous mode writes logs directly to the file system.

pub(crate) mod cfg;
pub(crate) mod log;

pub use log::*;

pub(crate) use file_operation::*;
pub(crate) use hyperlane_time::*;
pub(crate) use std::{
    fs::read_dir,
    sync::{Arc, RwLock},
};

```

# Path: hyperlane-log\src\log\const.rs

```rust
/// Default directory path for storing log files.
pub const DEFAULT_LOG_DIR: &str = "./logs";

/// Subdirectory name for error logs.
pub const ERROR_DIR: &str = "error";

/// Subdirectory name for info logs.
pub const INFO_DIR: &str = "info";

/// Subdirectory name for debug logs.
pub const DEBUG_DIR: &str = "debug";

/// File extension for log files.
pub const LOG_EXTENSION: &str = "log";

/// Default starting index number for log files.
pub const DEFAULT_LOG_FILE_START_IDX: usize = 1;

/// Default maximum size limit for log files in bytes.
pub const DEFAULT_LOG_FILE_SIZE: usize = 1_024_000_000;

/// Special value indicating no size limit for log files.
pub const DISABLE_LOG_FILE_SIZE: usize = 0;

/// Root path symbol.
pub(crate) const ROOT_PATH: &str = "/";

/// Dot symbol.
pub(crate) const POINT: &str = ".";

/// Line break symbol.
pub(crate) const BR: &str = "\n";

```

# Path: hyperlane-log\src\log\fn.rs

```rust
use crate::*;

/// Extracts the second element (index number) from log filenames in a directory.
///
/// # Arguments
///
/// - `&str` - The directory path to scan for log files.
///
/// # Returns
///
/// - `usize` - The extracted index number or default start index.
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

/// Generates a log filename with given index using current date.
///
/// # Arguments
///
/// - `usize` - The index number for the log file.
///
/// # Returns
///
/// - `String` - The formatted log filename with path.
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

/// Generates directory name for current date's logs.
///
/// # Returns
///
/// - `String` - The directory name based on current date.
#[inline(always)]
pub(crate) fn get_file_dir_name() -> String {
    format!("{}{}", ROOT_PATH, date())
}

/// Constructs appropriate log file path considering size limits.
///
/// # Arguments
///
/// - `&str` - The system directory path.
/// - `&str` - The base path for logs.
/// - `&usize` - The maximum allowed file size in bytes.
///
/// # Returns
///
/// - `String` - The full path to appropriate log file.
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

/// Formats log data with timestamp for each line.
///
/// # Arguments
///
/// - `AsRef<str>` - The data to be logged, which will be converted to string slice.
///
/// # Returns
///
/// - `String` - The formatted log string with timestamps.
#[inline(always)]
pub fn common_log<T: AsRef<str>>(data: T) -> String {
    let mut log_string: String = String::new();
    for line in data.as_ref().lines() {
        let line_string: String = format!("{}: {}{}", time(), line, BR);
        log_string.push_str(&line_string);
    }
    log_string
}

/// Handles log data formatting by delegating to common_log.
///
/// # Arguments
///
/// - `AsRef<str>` - The data to be logged, which will be converted to string slice.
///
/// # Returns
///
/// - `String` - The formatted log string.
#[inline(always)]
pub fn log_handler<T: AsRef<str>>(log_data: T) -> String {
    common_log(log_data)
}

```

# Path: hyperlane-log\src\log\impl.rs

```rust
use crate::*;

/// Blanket implementation for any function matching LogFuncTrait signature.
///
/// This allows any compatible closure or function to be used as a log formatter.
impl<F, T> LogFuncTrait<T> for F
where
    F: Fn(T) -> String + Send + Sync,
    T: AsRef<str>,
{
}

/// Default implementation for Log configuration.
impl Default for Log {
    /// Creates default Log configuration.
    ///
    /// # Returns
    ///
    /// - `Self` - Default Log instance with default path and file size limit.
    #[inline(always)]
    fn default() -> Self {
        Self {
            path: DEFAULT_LOG_DIR.to_owned(),
            limit_file_size: DEFAULT_LOG_FILE_SIZE,
        }
    }
}

impl Log {
    /// Creates new Log configuration with specified parameters.
    ///
    /// # Arguments
    ///
    /// - `P: AsRef<str>` - The path for storing log files, which will be converted to string slice.
    /// - `usize` - The maximum file size limit in bytes.
    ///
    /// # Returns
    ///
    /// - `Self` - A new Log instance with specified configuration.
    #[inline(always)]
    pub fn new<P: AsRef<str>>(path: P, limit_file_size: usize) -> Self {
        Self {
            path: path.as_ref().to_owned(),
            limit_file_size,
        }
    }

    /// Sets the log file storage path.
    ///
    /// # Arguments
    ///
    /// - `P: AsRef<str>` - The new path for storing log files, which will be converted to string slice.
    ///
    /// # Returns
    ///
    /// - `&mut Self` - Mutable reference to self for method chaining.
    #[inline(always)]
    pub fn path<P: AsRef<str>>(&mut self, path: P) -> &mut Self {
        self.path = path.as_ref().to_owned();
        self
    }

    /// Sets the maximum size limit for log files.
    ///
    /// # Arguments
    ///
    /// - `usize` - The new maximum file size limit in bytes.
    ///
    /// # Returns
    ///
    /// - `&mut Self` - Mutable reference to self for method chaining.
    #[inline(always)]
    pub fn limit_file_size(&mut self, limit_file_size: usize) -> &mut Self {
        self.limit_file_size = limit_file_size;
        self
    }

    /// Checks if logging is enabled.
    ///
    /// # Returns
    ///
    /// - `bool` - True if logging is enabled.
    #[inline(always)]
    pub fn is_enable(&self) -> bool {
        self.limit_file_size != DISABLE_LOG_FILE_SIZE
    }

    /// Checks if logging is disabled.
    ///
    /// # Returns
    ///
    /// - `bool` - True if logging is disabled.
    #[inline(always)]
    pub fn is_disable(&self) -> bool {
        !self.is_enable()
    }

    /// Writes log data synchronously to specified directory.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The data to be logged, which will be converted to string slice.
    /// - `L: LogFuncTrait<T>` - The log formatting function.
    /// - `&str` - The subdirectory for log file.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to self for method chaining.
    fn write_sync<T, L>(&self, data: T, func: L, dir: &str) -> &Self
    where
        T: AsRef<str>,
        L: LogFuncTrait<T>,
    {
        if self.is_disable() {
            return self;
        }
        let out: String = func(data);
        let path: String = get_log_path(dir, &self.path, &self.limit_file_size);
        let _ = append_to_file(&path, out.as_bytes());
        self
    }

    /// Writes log data asynchronously to specified directory.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The data to be logged, which will be converted to string slice.
    /// - `L: LogFuncTrait<T>` - The log formatting function.
    /// - `&str` - The subdirectory for log file.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to self for method chaining.
    async fn write_async<T, L>(&self, data: T, func: L, dir: &str) -> &Self
    where
        T: AsRef<str>,
        L: LogFuncTrait<T>,
    {
        if self.is_disable() {
            return self;
        }
        let out: String = func(data);
        let path: String = get_log_path(dir, &self.path, &self.limit_file_size);
        let _ = async_append_to_file(&path, out.as_bytes()).await;
        self
    }

    /// Logs error message synchronously.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - Error data to be logged, which will be converted to string slice.
    /// - `L: LogFuncTrait<T>` - Log formatting function.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to self.
    pub fn error<T, L>(&self, data: T, func: L) -> &Self
    where
        T: AsRef<str>,
        L: LogFuncTrait<T>,
    {
        self.write_sync(data, func, ERROR_DIR)
    }

    /// Logs error message asynchronously.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - Error data to be logged, which will be converted to string slice.
    /// - `L: LogFuncTrait<T>` - Log formatting function.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to self.
    pub async fn async_error<T, L>(&self, data: T, func: L) -> &Self
    where
        T: AsRef<str>,
        L: LogFuncTrait<T>,
    {
        self.write_async(data, func, ERROR_DIR).await
    }

    /// Logs info message synchronously.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - Info data to be logged, which will be converted to string slice.
    /// - `L: LogFuncTrait<T>` - Log formatting function.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to self.
    pub fn info<T, L>(&self, data: T, func: L) -> &Self
    where
        T: AsRef<str>,
        L: LogFuncTrait<T>,
    {
        self.write_sync(data, func, INFO_DIR)
    }

    /// Logs info message asynchronously.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - Info data to be logged, which will be converted to string slice.
    /// - `L: LogFuncTrait<T>` - Log formatting function.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to self.
    pub async fn async_info<T, L>(&self, data: T, func: L) -> &Self
    where
        T: AsRef<str>,
        L: LogFuncTrait<T>,
    {
        self.write_async(data, func, INFO_DIR).await
    }

    /// Logs debug message synchronously.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - Debug data to be logged, which will be converted to string slice.
    /// - `L: LogFuncTrait<T>` - Log formatting function.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to self.
    pub fn debug<T, L>(&self, data: T, func: L) -> &Self
    where
        T: AsRef<str>,
        L: LogFuncTrait<T>,
    {
        self.write_sync(data, func, DEBUG_DIR)
    }

    /// Logs debug message asynchronously.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - Debug data to be logged, which will be converted to string slice.
    /// - `L: LogFuncTrait<T>` - Log formatting function.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to self.
    pub async fn async_debug<T, L>(&self, data: T, func: L) -> &Self
    where
        T: AsRef<str>,
        L: LogFuncTrait<T>,
    {
        self.write_async(data, func, DEBUG_DIR).await
    }
}

```

# Path: hyperlane-log\src\log\mod.rs

```rust
pub(crate) mod r#const;
pub(crate) mod r#fn;
pub(crate) mod r#impl;
pub(crate) mod r#struct;
pub(crate) mod r#trait;
pub(crate) mod r#type;

pub use r#const::*;
pub use r#fn::*;
pub use r#struct::*;
pub use r#trait::*;
pub use r#type::*;

```

# Path: hyperlane-log\src\log\struct.rs

```rust
/// Main configuration structure for log file output.
///
/// Controls where logs are stored and their maximum size limits.
/// Use Log::new() to create an instance with custom settings.
#[derive(Clone)]
pub struct Log {
    /// The directory path where log files will be stored.
    pub(super) path: String,
    /// The maximum allowed size (in bytes) for individual log files.
    /// Set to 0 to disable logging.
    pub(super) limit_file_size: usize,
}

```

# Path: hyperlane-log\src\log\trait.rs

```rust
/// Trait for log formatting functions.
///
/// Defines the interface for functions that format log data.
/// Implemented automatically for any compatible Fn(T) -> String.
///
/// # Generic Parameters
///
/// - `AsRef<str>` - The type of data to be formatted, which will be converted to string slice.
pub trait LogFuncTrait<T: AsRef<str>>: Fn(T) -> String + Send + Sync {}

```

# Path: hyperlane-log\src\log\type.rs

```rust
use crate::*;

/// A collection of named log formatting functions.
pub type ListLog<T> = Vec<(String, ArcLogFunc<T>)>;

/// Thread-safe shared reference to a collection of log functions.
pub type LogListArcLock<T> = Arc<RwLock<ListLog<T>>>;

/// Thread-safe shared reference to a Log configuration instance.
pub type LogArcLock = Arc<RwLock<Log>>;

/// Trait object representing a log formatting function.
pub type LogFunc<T> = dyn LogFuncTrait<T>;

/// Thread-safe shared reference to a log formatting function.
pub type ArcLogFunc<T> = Arc<LogFunc<T>>;

/// Thread-safe shared reference to a Log configuration.
pub type ArcLog = Arc<Log>;

```

# Path: hyperlane-macros\README.md


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

- `#[send]` - Send complete response (headers and body) after function execution
- `#[send_body]` - Send only response body after function execution
- `#[send_body_with_data("data")]` - Send only response body with specified data after function execution

### Flush Macros

- `#[flush]` - Flush response stream after function execution to ensure immediate data transmission

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
- `#[panic_hook]` - Execute function when a panic occurs within the server
- `#[prologue_macros(macro1, macro2, ...)]` - Injects a list of macros before the decorated function.
- `#[epilogue_macros(macro1, macro2, ...)]` - Injects a list of macros after the decorated function.

### Middleware Macros

- `#[request_middleware]` - Register a function as a request middleware
- `#[request_middleware(order)]` - Register a function as a request middleware with specified order
- `#[response_middleware]` - Register a function as a response middleware
- `#[response_middleware(order)]` - Register a function as a response middleware with specified order
- `#[panic_hook]` - Register a function as a panic hook
- `#[panic_hook(order)]` - Register a function as a panic hook with specified order

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
- **Hook macros** For hook-related macros that support an `order` parameter, if `order` is not specified, the hook will have higher priority than hooks with a specified `order` (applies only to macros like `#[request_middleware]`, `#[response_middleware]`, `#[panic_hook]`)
- **Multi-parameter support** Most data extraction macros support multiple parameters in a single call (e.g., `#[request_body(var1, var2)]`, `#[request_query("k1" => v1, "k2" => v2)]`). This reduces macro repetition and improves code readability.

### Best Practice Warning

- Request related macros are mostly query functions, while response related macros are mostly assignment functions.
- When using `prologue_hooks` or `epilogue_hooks` macros, it is not recommended to combine them with other macros (such as `#[get]`, `#[post]`, `#[http]`, etc.) on the same function. These macros should be placed in the hook functions themselves. If you are not clear about how macros are expanded, combining them may lead to problematic code behavior.

## Example Usage

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

#[panic_hook]
#[panic_hook(1)]
#[panic_hook("2")]
struct PanicHook;

impl ServerHook for PanicHook {
    async fn new(_ctx: &Context) -> Self {
        Self
    }

    #[epilogue_macros(
        response_version(HttpVersion::Http1_1),
        response_status_code(500),
        response_body("panic_hook"),
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
        response_header(SEC_WEBSOCKET_ACCEPT => &WebSocketFrame::generate_accept_key(ctx.try_get_request_header_back(SEC_WEBSOCKET_KEY).await.unwrap())),
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
    #[epilogue_macros(send, flush)]
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
    #[epilogue_macros(send_body, flush)]
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

    #[prologue_macros(ws, get, response_body("get"), send_body)]
    async fn handle(self, ctx: &Context) {}
}

#[route("/post")]
struct Post;

impl ServerHook for Post {
    async fn new(_ctx: &Context) -> Self {
        Self
    }

    #[prologue_macros(post, response_body("post"), send)]
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
        ctx.send_body_list_with_data(&body_list).await.unwrap();
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
        ctx.send_body_list_with_data(&body_list).await.unwrap();
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
        ctx.send_body_list_with_data(&body_list).await.unwrap();
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
        ctx.send_body_list_with_data(&body_list).await.unwrap();
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
        ctx.send_body_list_with_data(&body_list).await.unwrap();
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
    #[epilogue_macros(send, flush)]
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
    #[epilogue_macros(send, flush)]
    async fn complex_post_handler_with_ref_self(&self, ctx: &Context) {}
}

impl InjectComplexPost {
    #[post]
    async fn test_with_bool_param(_a: bool, ctx: &Context) {}

    #[get]
    async fn test_with_multiple_params(_a: bool, ctx: &Context, _b: i32) {}
}

#[response_body("standalone response body")]
async fn standalone_response_body_handler(ctx: &Context) {}

#[prologue_macros(get, response_body("standalone get handler"))]
async fn standalone_get_handler(ctx: &Context) {}

#[epilogue_macros(send, flush)]
async fn standalone_send_and_flush_handler(ctx: &Context) {}

#[request_body(_raw_body)]
async fn standalone_request_body_extractor(ctx: &Context) {}

#[methods(get, post)]
async fn standalone_multiple_methods_handler(ctx: &Context) {}

#[http_from_stream]
async fn standalone_http_stream_handler(ctx: &Context) {}

#[ws_from_stream]
async fn standalone_websocket_stream_handler(ctx: &Context) {}

#[prologue_macros(
    get,
    http,
    response_status_code(200),
    response_header(CONTENT_TYPE => TEXT_PLAIN),
    response_body("standalone complex handler")
)]
#[epilogue_macros(send, flush)]
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
        send
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

#[reject_host("badhost.com", "spam.com")]
async fn test_multi_reject_host(ctx: &Context) {
    println!("Reject host check passed");
}

#[referer("http://localhost", "http://127.0.0.1")]
async fn test_multi_referer(ctx: &Context) {
    println!("Referer check passed");
}

#[reject_referer("http://badsite.com", "http://spam.com")]
async fn test_multi_reject_referer(ctx: &Context) {
    println!("Reject referer check passed");
}

#[hyperlane(server1: Server, server2: Server)]
async fn test_multi_hyperlane() {
    println!("server1 and server2 initialized");
}

#[hyperlane(server: Server)]
#[hyperlane(config: ServerConfig)]
#[tokio::main]
async fn main() {
    config.disable_nodelay().await;
    server.config(config).await;
    let server_control_hook: ServerControlHook = server.run().await.unwrap_or_default();
    server_control_hook.wait().await;
}
```

## Contact


# Path: hyperlane-macros\debug\src\main.rs

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

#[panic_hook]
#[panic_hook(1)]
#[panic_hook("2")]
struct PanicHook;

impl ServerHook for PanicHook {
    async fn new(_ctx: &Context) -> Self {
        Self
    }

    #[epilogue_macros(
        response_version(HttpVersion::Http1_1),
        response_status_code(500),
        response_body("panic_hook"),
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
        response_header(SEC_WEBSOCKET_ACCEPT => &WebSocketFrame::generate_accept_key(ctx.try_get_request_header_back(SEC_WEBSOCKET_KEY).await.unwrap())),
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
    #[epilogue_macros(send, flush)]
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
    #[epilogue_macros(send_body, flush)]
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

    #[prologue_macros(ws, get, response_body("get"), send_body)]
    async fn handle(self, ctx: &Context) {}
}

#[route("/post")]
struct Post;

impl ServerHook for Post {
    async fn new(_ctx: &Context) -> Self {
        Self
    }

    #[prologue_macros(post, response_body("post"), send)]
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
        ctx.send_body_list_with_data(&body_list).await.unwrap();
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
        ctx.send_body_list_with_data(&body_list).await.unwrap();
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
        ctx.send_body_list_with_data(&body_list).await.unwrap();
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
        ctx.send_body_list_with_data(&body_list).await.unwrap();
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
        ctx.send_body_list_with_data(&body_list).await.unwrap();
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
    #[epilogue_macros(send, flush)]
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
    #[epilogue_macros(send, flush)]
    async fn complex_post_handler_with_ref_self(&self, ctx: &Context) {}
}

impl InjectComplexPost {
    #[post]
    async fn test_with_bool_param(_a: bool, ctx: &Context) {}

    #[get]
    async fn test_with_multiple_params(_a: bool, ctx: &Context, _b: i32) {}
}

#[response_body("standalone response body")]
async fn standalone_response_body_handler(ctx: &Context) {}

#[prologue_macros(get, response_body("standalone get handler"))]
async fn standalone_get_handler(ctx: &Context) {}

#[epilogue_macros(send, flush)]
async fn standalone_send_and_flush_handler(ctx: &Context) {}

#[request_body(_raw_body)]
async fn standalone_request_body_extractor(ctx: &Context) {}

#[methods(get, post)]
async fn standalone_multiple_methods_handler(ctx: &Context) {}

#[http_from_stream]
async fn standalone_http_stream_handler(ctx: &Context) {}

#[ws_from_stream]
async fn standalone_websocket_stream_handler(ctx: &Context) {}

#[prologue_macros(
    get,
    http,
    response_status_code(200),
    response_header(CONTENT_TYPE => TEXT_PLAIN),
    response_body("standalone complex handler")
)]
#[epilogue_macros(send, flush)]
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
        send
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

#[reject_host("badhost.com", "spam.com")]
async fn test_multi_reject_host(ctx: &Context) {
    println!("Reject host check passed");
}

#[referer("http://localhost", "http://127.0.0.1")]
async fn test_multi_referer(ctx: &Context) {
    println!("Referer check passed");
}

#[reject_referer("http://badsite.com", "http://spam.com")]
async fn test_multi_reject_referer(ctx: &Context) {
    println!("Reject referer check passed");
}

#[hyperlane(server1: Server, server2: Server)]
async fn test_multi_hyperlane() {
    println!("server1 and server2 initialized");
}

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

# Path: hyperlane-macros\src\lib.rs

```rust
//! hyperlane-macros
//!
//! A comprehensive collection of procedural macros for building
//! HTTP servers with enhanced functionality. This crate provides
//! attribute macros that simplify HTTP request handling, protocol
//! validation, response management, and request data extraction.

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

/// Restricts function execution to HTTP GET requests only.
///
/// This attribute macro ensures the decorated function only executes when the incoming request
/// uses the GET HTTP method. Requests with other methods will be filtered out.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/get")]
/// struct Get;
///
/// impl ServerHook for Get {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[prologue_macros(get, response_body("get"))]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl Get {
///     #[get]
///     async fn get_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[get]
/// async fn standalone_get_handler(ctx: &Context) {}
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn get(_attr: TokenStream, item: TokenStream) -> TokenStream {
    get_handler(item, Position::Prologue)
}

/// Restricts function execution to HTTP POST requests only.
///
/// This attribute macro ensures the decorated function only executes when the incoming request
/// uses the POST HTTP method. Requests with other methods will be filtered out.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/post")]
/// struct Post;
///
/// impl ServerHook for Post {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[prologue_macros(post, response_body("post"))]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl Post {
///     #[post]
///     async fn post_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[post]
/// async fn standalone_post_handler(ctx: &Context) {}
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn post(_attr: TokenStream, item: TokenStream) -> TokenStream {
    epilogue_handler(item, Position::Prologue)
}

/// Restricts function execution to HTTP PUT requests only.
///
/// This attribute macro ensures the decorated function only executes when the incoming request
/// uses the PUT HTTP method. Requests with other methods will be filtered out.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/put")]
/// struct Put;
///
/// impl ServerHook for Put {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[prologue_macros(put, response_body("put"))]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl Put {
///     #[put]
///     async fn put_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[put]
/// async fn standalone_put_handler(ctx: &Context) {}
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn put(_attr: TokenStream, item: TokenStream) -> TokenStream {
    put_handler(item, Position::Prologue)
}

/// Restricts function execution to HTTP DELETE requests only.
///
/// This attribute macro ensures the decorated function only executes when the incoming request
/// uses the DELETE HTTP method. Requests with other methods will be filtered out.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/delete")]
/// struct Delete;
///
/// impl ServerHook for Delete {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[prologue_macros(delete, response_body("delete"))]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl Delete {
///     #[delete]
///     async fn delete_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[delete]
/// async fn standalone_delete_handler(ctx: &Context) {}
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn delete(_attr: TokenStream, item: TokenStream) -> TokenStream {
    delete_handler(item, Position::Prologue)
}

/// Restricts function execution to HTTP PATCH requests only.
///
/// This attribute macro ensures the decorated function only executes when the incoming request
/// uses the PATCH HTTP method. Requests with other methods will be filtered out.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/patch")]
/// struct Patch;
///
/// impl ServerHook for Patch {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[prologue_macros(patch, response_body("patch"))]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl Patch {
///     #[patch]
///     async fn patch_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[patch]
/// async fn standalone_patch_handler(ctx: &Context) {}
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn patch(_attr: TokenStream, item: TokenStream) -> TokenStream {
    patch_handler(item, Position::Prologue)
}

/// Restricts function execution to HTTP HEAD requests only.
///
/// This attribute macro ensures the decorated function only executes when the incoming request
/// uses the HEAD HTTP method. Requests with other methods will be filtered out.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/head")]
/// struct Head;
///
/// impl ServerHook for Head {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[prologue_macros(head, response_body("head"))]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl Head {
///     #[head]
///     async fn head_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[head]
/// async fn standalone_head_handler(ctx: &Context) {}
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn head(_attr: TokenStream, item: TokenStream) -> TokenStream {
    head_handler(item, Position::Prologue)
}

/// Restricts function execution to HTTP OPTIONS requests only.
///
/// This attribute macro ensures the decorated function only executes when the incoming request
/// uses the OPTIONS HTTP method. Requests with other methods will be filtered out.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/options")]
/// struct Options;
///
/// impl ServerHook for Options {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[prologue_macros(options, response_body("options"))]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl Options {
///     #[options]
///     async fn options_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[options]
/// async fn standalone_options_handler(ctx: &Context) {}
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn options(_attr: TokenStream, item: TokenStream) -> TokenStream {
    options_handler(item, Position::Prologue)
}

/// Restricts function execution to HTTP CONNECT requests only.
///
/// This attribute macro ensures the decorated function only executes when the incoming request
/// uses the CONNECT HTTP method. Requests with other methods will be filtered out.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/connect")]
/// struct Connect;
///
/// impl ServerHook for Connect {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[prologue_macros(connect, response_body("connect"))]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl Connect {
///     #[connect]
///     async fn connect_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[connect]
/// async fn standalone_connect_handler(ctx: &Context) {}
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn connect(_attr: TokenStream, item: TokenStream) -> TokenStream {
    connect_handler(item, Position::Prologue)
}

/// Restricts function execution to HTTP TRACE requests only.
///
/// This attribute macro ensures the decorated function only executes when the incoming request
/// uses the TRACE HTTP method. Requests with other methods will be filtered out.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/trace")]
/// struct Trace;
///
/// impl ServerHook for Trace {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[prologue_macros(trace, response_body("trace"))]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl Trace {
///     #[trace]
///     async fn trace_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[trace]
/// async fn standalone_trace_handler(ctx: &Context) {}
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn trace(_attr: TokenStream, item: TokenStream) -> TokenStream {
    trace_handler(item, Position::Prologue)
}

/// Allows function to handle multiple HTTP methods.
///
/// This attribute macro configures the decorated function to execute for any of the specified
/// HTTP methods. Methods should be provided as a comma-separated list.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/get_post")]
/// struct GetPost;
///
/// impl ServerHook for GetPost {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[prologue_macros(
///         http,
///         methods(get, post),
///         response_body("get_post")
///     )]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl GetPost {
///     #[methods(get, post)]
///     async fn methods_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[methods(get, post)]
/// async fn standalone_methods_handler(ctx: &Context) {}
/// ```
///
/// The macro accepts a comma-separated list of HTTP method names (lowercase) and should be
/// applied to async functions that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn methods(attr: TokenStream, item: TokenStream) -> TokenStream {
    methods_macro(attr, item, Position::Prologue)
}

/// Restricts function execution to WebSocket upgrade requests only.
///
/// This attribute macro ensures the decorated function only executes when the incoming request
/// is a valid WebSocket upgrade request with proper request headers and protocol negotiation.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/ws")]
/// struct Websocket;
///
/// impl ServerHook for Websocket {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[ws]
///     #[ws_from_stream]
///     async fn handle(self, ctx: &Context) {
///         let body: RequestBody = ctx.get_request_body().await;
///         let body_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(&body);
///         ctx.send_body_list_with_data(&body_list).await.unwrap();
///     }
/// }
///
/// impl Websocket {
///     #[ws]
///     async fn ws_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[ws]
/// async fn standalone_ws_handler(ctx: &Context) {}
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn ws(_attr: TokenStream, item: TokenStream) -> TokenStream {
    ws_macro(item, Position::Prologue)
}

/// Restricts function execution to standard HTTP requests only.
///
/// This attribute macro ensures the decorated function only executes for standard HTTP requests,
/// excluding WebSocket upgrades and other protocol upgrade requests.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/http")]
/// struct HttpOnly;
///
/// impl ServerHook for HttpOnly {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[prologue_macros(http, response_body("http"))]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl HttpOnly {
///     #[http]
///     async fn http_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[http]
/// async fn standalone_http_handler(ctx: &Context) {}
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn http(_attr: TokenStream, item: TokenStream) -> TokenStream {
    http_macro(item, Position::Prologue)
}

/// Sets the HTTP status code for the response.
///
/// This attribute macro configures the HTTP status code that will be sent with the response.
/// The status code can be provided as a numeric literal or a global constant.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// const CUSTOM_STATUS_CODE: i32 = 200;
///
/// #[route("/response_status_code")]
/// struct ResponseStatusCode;
///
/// impl ServerHook for ResponseStatusCode {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[response_status_code(CUSTOM_STATUS_CODE)]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl ResponseStatusCode {
///     #[response_status_code(CUSTOM_STATUS_CODE)]
///     async fn response_status_code_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[response_status_code(200)]
/// async fn standalone_response_status_code_handler(ctx: &Context) {}
/// ```
///
/// The macro accepts a numeric HTTP status code or a global constant
/// and should be applied to async functions that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn response_status_code(attr: TokenStream, item: TokenStream) -> TokenStream {
    response_status_code_macro(attr, item, Position::Prologue)
}

/// Sets the HTTP reason phrase for the response.
///
/// This attribute macro configures the HTTP reason phrase that accompanies the status code.
/// The reason phrase can be provided as a string literal or a global constant.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// const CUSTOM_REASON: &str = "Accepted";
///
/// #[route("/response_reason")]
/// struct ResponseReason;
///
/// impl ServerHook for ResponseReason {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[response_reason_phrase(CUSTOM_REASON)]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl ResponseReason {
///     #[response_reason_phrase(CUSTOM_REASON)]
///     async fn response_reason_phrase_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[response_reason_phrase("OK")]
/// async fn standalone_response_reason_phrase_handler(ctx: &Context) {}
/// ```
///
/// The macro accepts a string literal or global constant for the reason phrase and should be
/// applied to async functions that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn response_reason_phrase(attr: TokenStream, item: TokenStream) -> TokenStream {
    response_reason_phrase_macro(attr, item, Position::Prologue)
}

/// Sets or replaces a specific HTTP response header.
///
/// This attribute macro configures a specific HTTP response header that will be sent with the response.
/// Both the header name and value can be provided as string literals or global constants.
/// Use `"key", "value"` to set a header (add to existing headers) or `"key" => "value"` to replace a header (overwrite existing).
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// const CUSTOM_HEADER_NAME: &str = "X-Custom-Header";
/// const CUSTOM_HEADER_VALUE: &str = "custom-value";
///
/// #[route("/response_header")]
/// struct ResponseHeader;
///
/// impl ServerHook for ResponseHeader {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[response_header(CUSTOM_HEADER_NAME => CUSTOM_HEADER_VALUE)]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl ResponseHeader {
///     #[response_header(CUSTOM_HEADER_NAME => CUSTOM_HEADER_VALUE)]
///     async fn response_header_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[route("/response_header")]
/// struct ResponseHeaderTest;
///
/// impl ServerHook for ResponseHeaderTest {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[response_body("Testing header set and replace operations")]
///     #[response_header("X-Add-Header", "add-value")]
///     #[response_header("X-Set-Header" => "set-value")]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// #[response_header("X-Custom" => "value")]
/// async fn standalone_response_header_handler(ctx: &Context) {}
/// ```
///
/// The macro accepts header name and header value, both can be string literals or global constants.
/// Use `"key", "value"` for setting headers and `"key" => "value"` for replacing headers.
/// Should be applied to async functions that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn response_header(attr: TokenStream, item: TokenStream) -> TokenStream {
    response_header_macro(attr, item, Position::Prologue)
}

/// Sets the HTTP response body.
///
/// This attribute macro configures the HTTP response body that will be sent with the response.
/// The body content can be provided as a string literal or a global constant.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// const RESPONSE_DATA: &str = "{\"status\": \"success\"}";
///
/// #[route("/response_body")]
/// struct ResponseBody;
///
/// impl ServerHook for ResponseBody {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[response_body(&RESPONSE_DATA)]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl ResponseBody {
///     #[response_body(&RESPONSE_DATA)]
///     async fn response_body_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[response_body("standalone response body")]
/// async fn standalone_response_body_handler(ctx: &Context) {}
/// ```
///
/// The macro accepts a string literal or global constant for the response body and should be
/// applied to async functions that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn response_body(attr: TokenStream, item: TokenStream) -> TokenStream {
    response_body_macro(attr, item, Position::Prologue)
}

/// Clears all response headers.
///
/// This attribute macro clears all response headers from the response.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/clear_response_headers")]
/// struct ClearResponseHeaders;
///
/// impl ServerHook for ClearResponseHeaders {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[prologue_macros(
///         clear_response_headers,
///         filter(ctx.get_request().await.is_unknown_method()),
///         response_body("clear_response_headers")
///     )]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl ClearResponseHeaders {
///     #[clear_response_headers]
///     async fn clear_response_headers_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[clear_response_headers]
/// async fn standalone_clear_response_headers_handler(ctx: &Context) {}
/// ```
///
/// The macro should be applied to async functions that accept a `&Context` parameter.   
#[proc_macro_attribute]
pub fn clear_response_headers(_attr: TokenStream, item: TokenStream) -> TokenStream {
    clear_response_headers_macro(item, Position::Prologue)
}

/// Sets the HTTP response version.
///
/// This attribute macro configures the HTTP response version that will be sent with the response.
/// The version can be provided as a variable or code block.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[request_middleware]
/// struct RequestMiddleware;
///
/// impl ServerHook for RequestMiddleware {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[epilogue_macros(
///         response_status_code(200),
///         response_version(HttpVersion::Http1_1),
///         response_header(SERVER => HYPERLANE)
///     )]
///     async fn handle(self, ctx: &Context) {}
/// }
/// ```
///
/// The macro accepts a variable or code block for the response version and should be
/// applied to async functions that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn response_version(attr: TokenStream, item: TokenStream) -> TokenStream {
    response_version_macro(attr, item, Position::Prologue)
}

/// Automatically sends the complete response after function execution.
///
/// This attribute macro ensures that the response (request headers and body) is automatically sent
/// to the client after the function completes execution.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/send")]
/// struct SendTest;
///
/// impl ServerHook for SendTest {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[epilogue_macros(send)]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl SendTest {
///     #[send]
///     async fn send_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[send]
/// async fn standalone_send_handler(ctx: &Context) {}
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn send(_attr: TokenStream, item: TokenStream) -> TokenStream {
    send_macro(item, Position::Epilogue)
}

/// Automatically sends only the response body after function execution.
///
/// This attribute macro ensures that only the response body is automatically sent
/// to the client after the function completes, handling request headers separately.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/send_body")]
/// struct SendBodyTest;
///
/// impl ServerHook for SendBodyTest {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[epilogue_macros(send_body)]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl SendBodyTest {
///     #[send_body]
///     async fn send_body_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[send_body]
/// async fn standalone_send_body_handler(ctx: &Context) {}
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn send_body(_attr: TokenStream, item: TokenStream) -> TokenStream {
    send_body_macro(item, Position::Epilogue)
}

/// Flushes the response stream after function execution.
///
/// This attribute macro ensures that the response stream is flushed to guarantee immediate
/// data transmission, forcing any buffered response data to be sent to the client.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/flush")]
/// struct FlushTest;
///
/// impl ServerHook for FlushTest {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[epilogue_macros(flush)]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl FlushTest {
///     #[flush]
///     async fn flush_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[flush]
/// async fn standalone_flush_handler(ctx: &Context) {}
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn flush(_attr: TokenStream, item: TokenStream) -> TokenStream {
    flush_macro(item, Position::Prologue)
}

/// Handles aborted request scenarios.
///
/// This attribute macro configures the function to handle cases where the client has
/// aborted the request, providing appropriate handling for interrupted or cancelled requests.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/aborted")]
/// struct Aborted;
///
/// impl ServerHook for Aborted {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[aborted]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl Aborted {
///     #[aborted]
///     async fn aborted_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[aborted]
/// async fn standalone_aborted_handler(ctx: &Context) {}
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn aborted(_attr: TokenStream, item: TokenStream) -> TokenStream {
    aborted_macro(item, Position::Prologue)
}

/// Handles closed connection scenarios.
///
/// This attribute macro configures the function to handle cases where the connection
/// has been closed, providing appropriate handling for terminated or disconnected connections.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/closed")]
/// struct ClosedTest;
///
/// impl ServerHook for ClosedTest {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[closed]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl ClosedTest {
///     #[closed]
///     async fn closed_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[closed]
/// async fn standalone_closed_handler(ctx: &Context) {}
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn closed(_attr: TokenStream, item: TokenStream) -> TokenStream {
    closed_macro(item, Position::Prologue)
}

/// Restricts function execution to HTTP/2 Cleartext (h2c) requests only.
///
/// This attribute macro ensures the decorated function only executes for HTTP/2 cleartext
/// requests that use the h2c upgrade mechanism.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/h2c")]
/// struct H2c;
///
/// impl ServerHook for H2c {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[prologue_macros(h2c, response_body("h2c"))]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl H2c {
///     #[h2c]
///     async fn h2c_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[h2c]
/// async fn standalone_h2c_handler(ctx: &Context) {}
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn h2c(_attr: TokenStream, item: TokenStream) -> TokenStream {
    h2c_macro(item, Position::Prologue)
}

/// Restricts function execution to HTTP/0.9 requests only.
///
/// This attribute macro ensures the decorated function only executes for HTTP/0.9
/// protocol requests, the earliest version of the HTTP protocol.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/http0_9")]
/// struct Http09;
///
/// impl ServerHook for Http09 {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[prologue_macros(http0_9, response_body("http0_9"))]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl Http09 {
///     #[http0_9]
///     async fn http0_9_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[http0_9]
/// async fn standalone_http0_9_handler(ctx: &Context) {}
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn http0_9(_attr: TokenStream, item: TokenStream) -> TokenStream {
    http0_9_macro(item, Position::Prologue)
}

/// Restricts function execution to HTTP/1.0 requests only.
///
/// This attribute macro ensures the decorated function only executes for HTTP/1.0
/// protocol requests.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/http1_0")]
/// struct Http10;
///
/// impl ServerHook for Http10 {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[prologue_macros(http1_0, response_body("http1_0"))]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl Http10 {
///     #[http1_0]
///     async fn http1_0_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[http1_0]
/// async fn standalone_http1_0_handler(ctx: &Context) {}
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn http1_0(_attr: TokenStream, item: TokenStream) -> TokenStream {
    http1_0_macro(item, Position::Prologue)
}

/// Restricts function execution to HTTP/1.1 requests only.
///
/// This attribute macro ensures the decorated function only executes for HTTP/1.1
/// protocol requests.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/http1_1")]
/// struct Http11;
///
/// impl ServerHook for Http11 {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[prologue_macros(http1_1, response_body("http1_1"))]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl Http11 {
///     #[http1_1]
///     async fn http1_1_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[http1_1]
/// async fn standalone_http1_1_handler(ctx: &Context) {}
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn http1_1(_attr: TokenStream, item: TokenStream) -> TokenStream {
    http1_1_macro(item, Position::Prologue)
}

/// Restricts function execution to HTTP/1.1 or higher protocol versions.
///
/// This attribute macro ensures the decorated function only executes for HTTP/1.1
/// or newer protocol versions, including HTTP/2, HTTP/3, and future versions.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/http1_1_or_higher")]
/// struct Http11OrHigher;
///
/// impl ServerHook for Http11OrHigher {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[prologue_macros(http1_1_or_higher, response_body("http1_1_or_higher"))]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl Http11OrHigher {
///     #[http1_1_or_higher]
///     async fn http1_1_or_higher_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[http1_1_or_higher]
/// async fn standalone_http1_1_or_higher_handler(ctx: &Context) {}
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn http1_1_or_higher(_attr: TokenStream, item: TokenStream) -> TokenStream {
    http1_1_or_higher_macro(item, Position::Prologue)
}

/// Restricts function execution to HTTP/2 requests only.
///
/// This attribute macro ensures the decorated function only executes for HTTP/2
/// protocol requests.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/http2")]
/// struct Http2;
///
/// impl ServerHook for Http2 {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[prologue_macros(http2, response_body("http2"))]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl Http2 {
///     #[http2]
///     async fn http2_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[http2]
/// async fn standalone_http2_handler(ctx: &Context) {}
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn http2(_attr: TokenStream, item: TokenStream) -> TokenStream {
    http2_macro(item, Position::Prologue)
}

/// Restricts function execution to HTTP/3 requests only.
///
/// This attribute macro ensures the decorated function only executes for HTTP/3
/// protocol requests, the latest version of the HTTP protocol.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/http3")]
/// struct Http3;
///
/// impl ServerHook for Http3 {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[prologue_macros(http3, response_body("http3"))]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl Http3 {
///     #[http3]
///     async fn http3_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[http3]
/// async fn standalone_http3_handler(ctx: &Context) {}
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn http3(_attr: TokenStream, item: TokenStream) -> TokenStream {
    http3_macro(item, Position::Prologue)
}

/// Restricts function execution to TLS-encrypted requests only.
///
/// This attribute macro ensures the decorated function only executes for requests
/// that use TLS/SSL encryption on the connection.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/tls")]
/// struct Tls;
///
/// impl ServerHook for Tls {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[prologue_macros(tls, response_body("tls"))]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl Tls {
///     #[tls]
///     async fn tls_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[tls]
/// async fn standalone_tls_handler(ctx: &Context) {}
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn tls(_attr: TokenStream, item: TokenStream) -> TokenStream {
    tls_macro(item, Position::Prologue)
}

/// Filters requests based on a boolean condition.
///
/// The function continues execution only if the provided code block returns `true`.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/unknown_method")]
/// struct UnknownMethod;
///
/// impl ServerHook for UnknownMethod {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[prologue_macros(
///         filter(ctx.get_request().await.is_unknown_method()),
///         response_body("unknown_method")
///     )]
///     async fn handle(self, ctx: &Context) {}
/// }
/// ```
#[proc_macro_attribute]
pub fn filter(attr: TokenStream, item: TokenStream) -> TokenStream {
    filter_macro(attr, item, Position::Prologue)
}

/// Rejects requests based on a boolean condition.
///
/// The function continues execution only if the provided code block returns `false`.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[response_middleware(2)]
/// struct ResponseMiddleware2;
///
/// impl ServerHook for ResponseMiddleware2 {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[prologue_macros(
///         reject(ctx.get_request().await.is_ws())
///     )]
///     async fn handle(self, ctx: &Context) {}
/// }
/// ```
#[proc_macro_attribute]
pub fn reject(attr: TokenStream, item: TokenStream) -> TokenStream {
    reject_macro(attr, item, Position::Prologue)
}

/// Restricts function execution to requests with a specific host.
///
/// This attribute macro ensures the decorated function only executes when the incoming request
/// has a host header that matches the specified value. Requests with different or missing host headers will be filtered out.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/host")]
/// struct Host;
///
/// impl ServerHook for Host {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[host("localhost")]
///     #[prologue_macros(response_body("host string literal: localhost"), send)]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl Host {
///     #[host("localhost")]
///     async fn host_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[host("localhost")]
/// async fn standalone_host_handler(ctx: &Context) {}
/// ```
///
/// The macro accepts a string literal specifying the expected host value and should be
/// applied to async functions that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn host(attr: TokenStream, item: TokenStream) -> TokenStream {
    host_macro(attr, item, Position::Prologue)
}

/// Reject requests that have no host header.
///
/// This attribute macro ensures the decorated function only executes when the incoming request
/// has a host header present. Requests without a host header will be filtered out.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/reject_host")]
/// struct RejectHost;
///
/// impl ServerHook for RejectHost {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[prologue_macros(
///         reject_host("filter.localhost"),
///         response_body("host filter string literal")
///     )]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl RejectHost {
///     #[reject_host("filter.localhost")]
///     async fn reject_host_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[reject_host("filter.localhost")]
/// async fn standalone_reject_host_handler(ctx: &Context) {}
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn reject_host(attr: TokenStream, item: TokenStream) -> TokenStream {
    reject_host_macro(attr, item, Position::Prologue)
}

/// Restricts function execution to requests with a specific referer.
///
/// This attribute macro ensures the decorated function only executes when the incoming request
/// has a referer header that matches the specified value. Requests with different or missing referer headers will be filtered out.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/referer")]
/// struct Referer;
///
/// impl ServerHook for Referer {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[prologue_macros(
///         referer("http://localhost"),
///         response_body("referer string literal: http://localhost")
///     )]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl Referer {
///     #[referer("http://localhost")]
///     async fn referer_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[referer("http://localhost")]
/// async fn standalone_referer_handler(ctx: &Context) {}
/// ```
///
/// The macro accepts a string literal specifying the expected referer value and should be
/// applied to async functions that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn referer(attr: TokenStream, item: TokenStream) -> TokenStream {
    referer_macro(attr, item, Position::Prologue)
}

/// Reject requests that have a specific referer header.
///
/// This attribute macro ensures the decorated function only executes when the incoming request
/// does not have a referer header that matches the specified value. Requests with the matching referer header will be filtered out.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/reject_referer")]
/// struct RejectReferer;
///
/// impl ServerHook for RejectReferer {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[prologue_macros(
///         reject_referer("http://localhost"),
///         response_body("referer filter string literal")
///     )]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl RejectReferer {
///     #[reject_referer("http://localhost")]
///     async fn reject_referer_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[reject_referer("http://localhost")]
/// async fn standalone_reject_referer_handler(ctx: &Context) {}
/// ```
///
/// The macro accepts a string literal specifying the referer value to filter out and should be
/// applied to async functions that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn reject_referer(attr: TokenStream, item: TokenStream) -> TokenStream {
    reject_referer_macro(attr, item, Position::Prologue)
}

/// Executes multiple specified functions before the main handler function.
///
/// This attribute macro configures multiple pre-execution hooks that run before the main function logic.
/// The specified hook functions will be called in the order provided, followed by the main function execution.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// struct PrologueHooks;
///
/// impl ServerHook for PrologueHooks {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[get]
///     #[http]
///     async fn handle(self, _ctx: &Context) {}
/// }
///
/// async fn prologue_hooks_fn(ctx: Context) {
///     let hook = PrologueHooks::new(&ctx).await;
///     hook.handle(&ctx).await;
/// }
///
/// #[route("/hook")]
/// struct Hook;
///
/// impl ServerHook for Hook {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[prologue_hooks(prologue_hooks_fn)]
///     #[response_body("Testing hook macro")]
///     async fn handle(self, ctx: &Context) {}
/// }
/// ```
///
/// The macro accepts a comma-separated list of function names as parameters. All hook functions
/// and the main function must accept a `Context` parameter. Avoid combining this macro with other
/// macros on the same function to prevent macro expansion conflicts.
#[proc_macro_attribute]
pub fn prologue_hooks(attr: TokenStream, item: TokenStream) -> TokenStream {
    prologue_hooks_macro(attr, item, Position::Prologue)
}

/// Executes multiple specified functions after the main handler function.
///
/// This attribute macro configures multiple post-execution hooks that run after the main function logic.
/// The main function will execute first, followed by the specified hook functions in the order provided.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// struct EpilogueHooks;
///
/// impl ServerHook for EpilogueHooks {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[response_status_code(200)]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// async fn epilogue_hooks_fn(ctx: Context) {
///     let hook = EpilogueHooks::new(&ctx).await;
///     hook.handle(&ctx).await;
/// }
///
/// #[route("/hook")]
/// struct Hook;
///
/// impl ServerHook for Hook {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[epilogue_hooks(epilogue_hooks_fn)]
///     #[response_body("Testing hook macro")]
///     async fn handle(self, ctx: &Context) {}
/// }
/// ```
///
/// The macro accepts a comma-separated list of function names as parameters. All hook functions
/// and the main function must accept a `Context` parameter. Avoid combining this macro with other
/// macros on the same function to prevent macro expansion conflicts.
#[proc_macro_attribute]
pub fn epilogue_hooks(attr: TokenStream, item: TokenStream) -> TokenStream {
    epilogue_hooks_macro(attr, item, Position::Epilogue)
}

/// Extracts the raw request body into a specified variable.
///
/// This attribute macro extracts the raw request body content into a variable
/// with the fixed type `RequestBody`. The body content is not parsed or deserialized.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/request_body")]
/// struct RequestBodyRoute;
///
/// impl ServerHook for RequestBodyRoute {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[response_body(&format!("raw body: {raw_body:?}"))]
///     #[request_body(raw_body)]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl RequestBodyRoute {
///     #[request_body(raw_body)]
///     async fn request_body_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[request_body(raw_body)]
/// async fn standalone_request_body_handler(ctx: &Context) {}
/// ```
///
/// # Multi-Parameter Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/multi_body")]
/// struct MultiBody;
///
/// impl ServerHook for MultiBody {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[response_body(&format!("bodies: {body1:?}, {body2:?}"))]
///     #[request_body(body1, body2)]
///     async fn handle(self, ctx: &Context) {}
/// }
/// ```
///
/// The macro accepts one or more variable names separated by commas.
/// Each variable will be available in the function scope as a `RequestBody` type.
#[proc_macro_attribute]
pub fn request_body(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_body_macro(attr, item, Position::Prologue)
}

/// Parses the request body as JSON into a specified variable and type with panic on parsing failure.
///
/// This attribute macro extracts and deserializes the request body content as JSON into a variable
/// with the specified type. The body content is parsed as JSON using serde.
/// If the request body does not exist or JSON parsing fails, the function will panic with an error message.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
/// use serde::{Deserialize, Serialize};
///
/// #[derive(Debug, Serialize, Deserialize, Clone)]
/// struct TestData {
///     name: String,
///     age: u32,
/// }
///
/// #[route("/request_body_json_result")]
/// struct RequestBodyJson;
///
/// impl ServerHook for RequestBodyJson {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[response_body(&format!("request data: {request_data_result:?}"))]
///     #[request_body_json_result(request_data_result: TestData)]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl RequestBodyJson {
///     #[request_body_json_result(request_data_result: TestData)]
///     async fn request_body_json_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[request_body_json_result(request_data_result: TestData)]
/// async fn standalone_request_body_json_handler(ctx: &Context) {}
/// ```
///
/// # Multi-Parameter Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
/// use serde::{Deserialize, Serialize};
///
/// #[derive(Debug, Serialize, Deserialize, Clone)]
/// struct User {
///     name: String,
/// }
///
/// #[derive(Debug, Serialize, Deserialize, Clone)]
/// struct Config {
///     debug: bool,
/// }
///
/// #[route("/request_body_json_result")]
/// struct TestData;
///
/// impl ServerHook for TestData {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[response_body(&format!("user: {user:?}, config: {config:?}"))]
///     #[request_body_json_result(user: User, config: Config)]
///     async fn handle(self, ctx: &Context) {}
/// }
/// ```
///
/// The macro accepts one or more `variable_name: Type` pairs separated by commas.
/// Each variable will be available in the function scope as a `Result<Type, serde_json::Error>`.
#[proc_macro_attribute]
pub fn request_body_json_result(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_body_json_result_macro(attr, item, Position::Prologue)
}

/// Parses the request body as JSON into a specified variable and type with panic on parsing failure.
///
/// This attribute macro extracts and deserializes the request body content as JSON into a variable
/// with the specified type. The body content is parsed as JSON using serde.
/// If the request body does not exist or JSON parsing fails, the function will panic with an error message.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
/// use serde::{Deserialize, Serialize};
///
/// #[derive(Debug, Serialize, Deserialize, Clone)]
/// struct TestData {
///     name: String,
///     age: u32,
/// }
///
/// #[route("/request_body_json")]
/// struct RequestBodyJson;
///
/// impl ServerHook for RequestBodyJson {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[response_body(&format!("request data: {request_data_result:?}"))]
///     #[request_body_json(request_data_result: TestData)]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl RequestBodyJson {
///     #[request_body_json(request_data_result: TestData)]
///     async fn request_body_json_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[request_body_json(request_data_result: TestData)]
/// async fn standalone_request_body_json_handler(ctx: &Context) {}
/// ```
///
/// # Multi-Parameter Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
/// use serde::{Deserialize, Serialize};
///
/// #[derive(Debug, Serialize, Deserialize, Clone)]
/// struct User {
///     name: String,
/// }
///
/// #[derive(Debug, Serialize, Deserialize, Clone)]
/// struct Config {
///     debug: bool,
/// }
///
/// #[route("/request_body_json")]
/// struct TestData;
///
/// impl ServerHook for TestData {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[response_body(&format!("user: {user:?}, config: {config:?}"))]
///     #[request_body_json(user: User, config: Config)]
///     async fn handle(self, ctx: &Context) {}
/// }
/// ```
///
/// The macro accepts one or more `variable_name: Type` pairs separated by commas.
/// Each variable will be available in the function scope as a `Result<Type, serde_json::Error>`.
///
/// # Panics
///
/// This macro will panic if the request body does not exist or JSON parsing fails.
#[proc_macro_attribute]
pub fn request_body_json(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_body_json_macro(attr, item, Position::Prologue)
}

/// Extracts a specific attribute value into a variable wrapped in Option type.
///
/// This attribute macro retrieves a specific attribute by key and makes it available
/// as a typed Option variable from the request context. The extracted value is wrapped
/// in an Option type to safely handle cases where the attribute may not exist.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
/// use serde::{Deserialize, Serialize};
///
/// const TEST_ATTRIBUTE_KEY: &str = "test_attribute_key";
///
/// #[derive(Debug, Serialize, Deserialize, Clone)]
/// struct TestData {
///     name: String,
///     age: u32,
/// }
///
/// #[route("/attribute_option")]
/// struct Attribute;
///
/// impl ServerHook for Attribute {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[response_body(&format!("request attribute: {request_attribute_option:?}"))]
///     #[attribute_option(TEST_ATTRIBUTE_KEY => request_attribute_option: TestData)]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl Attribute {
///     #[attribute_option(TEST_ATTRIBUTE_KEY => request_attribute_option: TestData)]
///     async fn attribute_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[attribute_option(TEST_ATTRIBUTE_KEY => request_attribute_option: TestData)]
/// async fn standalone_attribute_handler(ctx: &Context) {}
/// ```
///
/// The macro accepts a key-to-variable mapping in the format `key => variable_name: Type`.
/// The variable will be available as an `Option<Type>` in the function scope.
///
/// # Multi-Parameter Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/attribute_option")]
/// struct MultiAttr;
///
/// impl ServerHook for MultiAttr {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[response_body(&format!("attrs: {attr1:?}, {attr2:?}"))]
///     #[attribute_option("key1" => attr1: String, "key2" => attr2: i32)]
///     async fn handle(self, ctx: &Context) {}
/// }
/// ```
///
/// The macro accepts multiple `key => variable_name: Type` tuples separated by commas.
#[proc_macro_attribute]
pub fn attribute_option(attr: TokenStream, item: TokenStream) -> TokenStream {
    attribute_option_macro(attr, item, Position::Prologue)
}

/// Extracts a specific attribute value into a variable with panic on missing value.
///
/// This attribute macro retrieves a specific attribute by key and makes it available
/// as a typed variable from the request context. If the attribute does not exist,
/// the function will panic with an error message indicating the missing attribute.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
/// use serde::{Deserialize, Serialize};
///
/// const TEST_ATTRIBUTE_KEY: &str = "test_attribute_key";
///
/// #[derive(Debug, Serialize, Deserialize, Clone)]
/// struct TestData {
///     name: String,
///     age: u32,
/// }
///
/// #[route("/attribute")]
/// struct Attribute;
///
/// impl ServerHook for Attribute {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[response_body(&format!("request attribute: {request_attribute:?}"))]
///     #[attribute(TEST_ATTRIBUTE_KEY => request_attribute: TestData)]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl Attribute {
///     #[attribute(TEST_ATTRIBUTE_KEY => request_attribute: TestData)]
///     async fn attribute_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[attribute(TEST_ATTRIBUTE_KEY => request_attribute: TestData)]
/// async fn standalone_attribute_handler(ctx: &Context) {}
/// ```
///
/// The macro accepts a key-to-variable mapping in the format `key => variable_name: Type`.
/// The variable will be available as an `Type` in the function scope.
///
/// # Multi-Parameter Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/attribute")]
/// struct MultiAttr;
///
/// impl ServerHook for MultiAttr {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[response_body(&format!("attrs: {attr1}, {attr2}"))]
///     #[attribute("key1" => attr1: String, "key2" => attr2: i32)]
///     async fn handle(self, ctx: &Context) {}
/// }
/// ```
///
/// The macro accepts multiple `key => variable_name: Type` tuples separated by commas.
///
/// # Panics
///
/// This macro will panic if the requested attribute does not exist in the request context.
#[proc_macro_attribute]
pub fn attribute(attr: TokenStream, item: TokenStream) -> TokenStream {
    attribute_macro(attr, item, Position::Prologue)
}

/// Extracts all attributes into a ThreadSafeAttributeStore variable.
///
/// This attribute macro retrieves all available attributes from the request context
/// and makes them available as a ThreadSafeAttributeStore for comprehensive attribute access.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/attributes")]
/// struct Attributes;
///
/// impl ServerHook for Attributes {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[response_body(&format!("request attributes: {request_attributes:?}"))]
///     #[attributes(request_attributes)]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl Attributes {
///     #[attributes(request_attributes)]
///     async fn attributes_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[attributes(request_attributes)]
/// async fn standalone_attributes_handler(ctx: &Context) {}
/// ```
///
/// The macro accepts a variable name that will contain a HashMap of all attributes.
/// The variable will be available as a HashMap in the function scope.
///
/// # Multi-Parameter Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/multi_attrs")]
/// struct MultiAttrs;
///
/// impl ServerHook for MultiAttrs {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[response_body(&format!("attrs1: {attrs1:?}, attrs2: {attrs2:?}"))]
///     #[attributes(attrs1, attrs2)]
///     async fn handle(self, ctx: &Context) {}
/// }
/// ```
///
/// The macro accepts multiple variable names separated by commas.
#[proc_macro_attribute]
pub fn attributes(attr: TokenStream, item: TokenStream) -> TokenStream {
    attributes_macro(attr, item, Position::Prologue)
}

/// Extracts a specific route parameter into a variable wrapped in Option type.
///
/// This attribute macro retrieves a specific route parameter by key and makes it
/// available as an Option variable. Route parameters are extracted from the URL path segments
/// and wrapped in an Option type to safely handle cases where the parameter may not exist.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/route_param_option/:test")]
/// struct RouteParam;
///
/// impl ServerHook for RouteParam {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[response_body(&format!("route param: {request_route_param:?}"))]
///     #[route_param_option("test" => request_route_param)]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl RouteParam {
///     #[route_param_option("test" => request_route_param)]
///     async fn route_param_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[route_param_option("test" => request_route_param)]
/// async fn standalone_route_param_handler(ctx: &Context) {}
/// ```
///
/// The macro accepts a key-to-variable mapping in the format `"key" => variable_name`.
/// The variable will be available as an `Option<String>` in the function scope.
///
/// # Multi-Parameter Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/multi_param/:id/:name")]
/// struct MultiParam;
///
/// impl ServerHook for MultiParam {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[response_body(&format!("id: {id:?}, name: {name:?}"))]
///     #[route_param_option("id" => id, "name" => name)]
///     async fn handle(self, ctx: &Context) {}
/// }
/// ```
///
/// The macro accepts multiple `"key" => variable_name` pairs separated by commas.
#[proc_macro_attribute]
pub fn route_param_option(attr: TokenStream, item: TokenStream) -> TokenStream {
    route_param_option_macro(attr, item, Position::Prologue)
}

/// Extracts a specific route parameter into a variable with panic on missing value.
///
/// This attribute macro retrieves a specific route parameter by key and makes it
/// available as a variable. Route parameters are extracted from the URL path segments.
/// If the requested route parameter does not exist, the function will panic with an error message.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/route_param/:test")]
/// struct RouteParam;
///
/// impl ServerHook for RouteParam {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[response_body(&format!("route param: {request_route_param:?}"))]
///     #[route_param("test" => request_route_param)]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl RouteParam {
///     #[route_param("test" => request_route_param)]
///     async fn route_param_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[route_param("test" => request_route_param)]
/// async fn standalone_route_param_handler(ctx: &Context) {}
/// ```
///
/// The macro accepts a key-to-variable mapping in the format `"key" => variable_name`.
/// The variable will be available as an `String` in the function scope.
///
///
/// # Multi-Parameter Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/multi_param/:id/:name")]
/// struct MultiParam;
///
/// impl ServerHook for MultiParam {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[response_body(&format!("id: {id:?}, name: {name:?}"))]
///     #[route_param("id" => id, "name" => name)]
///     async fn handle(self, ctx: &Context) {}
/// }
/// ```
///
/// The macro accepts multiple `"key" => variable_name` pairs separated by commas.
///
/// # Panics
///
/// This macro will panic if the requested route parameter does not exist in the URL path.
#[proc_macro_attribute]
pub fn route_param(attr: TokenStream, item: TokenStream) -> TokenStream {
    route_param_macro(attr, item, Position::Prologue)
}

/// Extracts all route parameters into a collection variable.
///
/// This attribute macro retrieves all available route parameters from the URL path
/// and makes them available as a collection for comprehensive route parameter access.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/route_params/:test")]
/// struct RouteParams;
///
/// impl ServerHook for RouteParams {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[response_body(&format!("request route params: {request_route_params:?}"))]
///     #[route_params(request_route_params)]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl RouteParams {
///     #[route_params(request_route_params)]
///     async fn route_params_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[route_params(request_route_params)]
/// async fn standalone_route_params_handler(ctx: &Context) {}
/// ```
///
/// The macro accepts a variable name that will contain all route parameters.
/// The variable will be available as a RouteParams type in the function scope.
///
/// # Multi-Parameter Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/multi_params/:id")]
/// struct MultiParams;
///
/// impl ServerHook for MultiParams {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[response_body(&format!("params1: {params1:?}, params2: {params2:?}"))]
///     #[route_params(params1, params2)]
///     async fn handle(self, ctx: &Context) {}
/// }
/// ```
///
/// The macro accepts multiple variable names separated by commas.
#[proc_macro_attribute]
pub fn route_params(attr: TokenStream, item: TokenStream) -> TokenStream {
    route_params_macro(attr, item, Position::Prologue)
}

/// Extracts a specific request query parameter into a variable wrapped in Option type.
///
/// This attribute macro retrieves a specific request query parameter by key and makes it
/// available as an Option variable. Query parameters are extracted from the URL request query string
/// and wrapped in an Option type to safely handle cases where the parameter may not exist.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/request_query_option")]
/// struct RequestQuery;
///
/// impl ServerHook for RequestQuery {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[prologue_macros(
///         request_query_option("test" => request_query_option),
///         response_body(&format!("request query: {request_query_option:?}")),
///         send
///     )]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl RequestQuery {
///     #[request_query_option("test" => request_query_option)]
///     async fn request_query_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[request_query_option("test" => request_query_option)]
/// async fn standalone_request_query_handler(ctx: &Context) {}
/// ```
///
/// The macro accepts a key-to-variable mapping in the format `"key" => variable_name`.
/// The variable will be available as an `Option<RequestQuerysValue>` in the function scope.
///
/// Supports multiple parameters: `#[request_query_option("k1" => v1, "k2" => v2)]`
#[proc_macro_attribute]
pub fn request_query_option(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_query_option_macro(attr, item, Position::Prologue)
}

/// Extracts a specific request query parameter into a variable with panic on missing value.
///
/// This attribute macro retrieves a specific request query parameter by key and makes it
/// available as a variable. Query parameters are extracted from the URL request query string.
/// If the requested query parameter does not exist, the function will panic with an error message.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/request_query")]
/// struct RequestQuery;
///
/// impl ServerHook for RequestQuery {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[prologue_macros(
///         request_query("test" => request_query),
///         response_body(&format!("request query: {request_query}")),
///         send
///     )]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl RequestQuery {
///     #[request_query("test" => request_query)]
///     async fn request_query_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[request_query("test" => request_query)]
/// async fn standalone_request_query_handler(ctx: &Context) {}
/// ```
///
/// The macro accepts a key-to-variable mapping in the format `"key" => variable_name`.
/// The variable will be available as an `RequestQuerysValue` in the function scope.
///
/// Supports multiple parameters: `#[request_query("k1" => v1, "k2" => v2)]`
///
/// # Panics
///
/// This macro will panic if the requested query parameter does not exist in the URL query string.
#[proc_macro_attribute]
pub fn request_query(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_query_macro(attr, item, Position::Prologue)
}

/// Extracts all request query parameters into a RequestQuerys variable.
///
/// This attribute macro retrieves all available request query parameters from the URL request query string
/// and makes them available as a RequestQuerys for comprehensive request query parameter access.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/request_querys")]
/// struct RequestQuerys;
///
/// impl ServerHook for RequestQuerys {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[prologue_macros(
///         request_querys(request_querys),
///         response_body(&format!("request querys: {request_querys:?}")),
///         send
///     )]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl RequestQuerys {
///     #[request_querys(request_querys)]
///     async fn request_querys_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[request_querys(request_querys)]
/// async fn standalone_request_querys_handler(ctx: &Context) {}
/// ```
///
/// The macro accepts a variable name that will contain all request query parameters.
/// The variable will be available as a collection in the function scope.
///
/// Supports multiple parameters: `#[request_querys(querys1, querys2)]`
#[proc_macro_attribute]
pub fn request_querys(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_querys_macro(attr, item, Position::Prologue)
}

/// Extracts a specific HTTP request header into a variable wrapped in Option type.
///
/// This attribute macro retrieves a specific HTTP request header by name and makes it
/// available as an Option variable. Header values are extracted from the request request headers collection
/// and wrapped in an Option type to safely handle cases where the header may not exist.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/request_header_option")]
/// struct RequestHeader;
///
/// impl ServerHook for RequestHeader {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[prologue_macros(
///         request_header_option(HOST => request_header_option),
///         response_body(&format!("request header: {request_header_option:?}")),
///         send
///     )]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl RequestHeader {
///     #[request_header_option(HOST => request_header_option)]
///     async fn request_header_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[request_header_option(HOST => request_header_option)]
/// async fn standalone_request_header_handler(ctx: &Context) {}
/// ```
///
/// The macro accepts a request header name-to-variable mapping in the format `HEADER_NAME => variable_name`
/// or `"Header-Name" => variable_name`. The variable will be available as an `Option<RequestHeadersValueItem>`.
#[proc_macro_attribute]
pub fn request_header_option(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_header_option_macro(attr, item, Position::Prologue)
}

/// Extracts a specific HTTP request header into a variable with panic on missing value.
///
/// This attribute macro retrieves a specific HTTP request header by name and makes it
/// available as a variable. Header values are extracted from the request request headers collection.
/// If the requested header does not exist, the function will panic with an error message.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/request_header")]
/// struct RequestHeader;
///
/// impl ServerHook for RequestHeader {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[prologue_macros(
///         request_header(HOST => request_header),
///         response_body(&format!("request header: {request_header}")),
///         send
///     )]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl RequestHeader {
///     #[request_header(HOST => request_header)]
///     async fn request_header_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[request_header(HOST => request_header)]
/// async fn standalone_request_header_handler(ctx: &Context) {}
/// ```
///
/// The macro accepts a request header name-to-variable mapping in the format `HEADER_NAME => variable_name`
/// or `"Header-Name" => variable_name`. The variable will be available as an `RequestHeadersValueItem`.
///
/// # Panics
///
/// This macro will panic if the requested header does not exist in the HTTP request headers.
#[proc_macro_attribute]
pub fn request_header(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_header_macro(attr, item, Position::Prologue)
}

/// Extracts all HTTP request headers into a collection variable.
///
/// This attribute macro retrieves all available HTTP request headers from the request
/// and makes them available as a collection for comprehensive request header access.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/request_headers")]
/// struct RequestHeaders;
///
/// impl ServerHook for RequestHeaders {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[prologue_macros(
///         request_headers(request_headers),
///         response_body(&format!("request headers: {request_headers:?}")),
///         send
///     )]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl RequestHeaders {
///     #[request_headers(request_headers)]
///     async fn request_headers_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[request_headers(request_headers)]
/// async fn standalone_request_headers_handler(ctx: &Context) {}
/// ```
///
/// The macro accepts a variable name that will contain all HTTP request headers.
/// The variable will be available as a RequestHeaders type in the function scope.
#[proc_macro_attribute]
pub fn request_headers(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_headers_macro(attr, item, Position::Prologue)
}

/// Extracts a specific cookie value or all cookies into a variable wrapped in Option type.
///
/// This attribute macro supports two syntaxes:
/// 1. `cookie(key => variable_name)` - Extract a specific cookie value by key, wrapped in Option
/// 2. `cookie(variable_name)` - Extract all cookies as a raw string, wrapped in Option
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/cookie")]
/// struct Cookie;
///
/// impl ServerHook for Cookie {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[response_body(&format!("Session cookie: {session_cookie1_option:?}, {session_cookie2_option:?}"))]
///     #[request_cookie_option("test1" => session_cookie1_option, "test2" => session_cookie2_option)]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl Cookie {
///     #[response_body(&format!("Session cookie: {session_cookie1_option:?}, {session_cookie2_option:?}"))]
///     #[request_cookie_option("test1" => session_cookie1_option, "test2" => session_cookie2_option)]
///     async fn request_cookie_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[response_body(&format!("Session cookie: {session_cookie1_option:?}, {session_cookie2_option:?}"))]
/// #[request_cookie_option("test1" => session_cookie1_option, "test2" => session_cookie2_option)]
/// async fn standalone_request_cookie_handler(ctx: &Context) {}
/// ```
///
/// For specific cookie extraction, the variable will be available as `Option<String>`.
/// For all cookies extraction, the variable will be available as `String`.
#[proc_macro_attribute]
pub fn request_cookie_option(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_cookie_option_macro(attr, item, Position::Prologue)
}

/// Extracts a specific cookie value or all cookies into a variable with panic on missing value.
///
/// This attribute macro supports two syntaxes:
/// 1. `cookie(key => variable_name)` - Extract a specific cookie value by key, panics if missing
/// 2. `cookie(variable_name)` - Extract all cookies as a raw string, panics if missing
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/cookie")]
/// struct Cookie;
///
/// impl ServerHook for Cookie {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[response_body(&format!("Session cookie: {session_cookie1}, {session_cookie2}"))]
///     #[request_cookie("test1" => session_cookie1, "test2" => session_cookie2)]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl Cookie {
///     #[response_body(&format!("Session cookie: {session_cookie1}, {session_cookie2}"))]
///     #[request_cookie("test1" => session_cookie1, "test2" => session_cookie2)]
///     async fn request_cookie_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[response_body(&format!("Session cookie: {session_cookie1}, {session_cookie2}"))]
/// #[request_cookie("test1" => session_cookie1, "test2" => session_cookie2)]
/// async fn standalone_request_cookie_handler(ctx: &Context) {}
/// ```
///
/// For specific cookie extraction, the variable will be available as `String`.
/// For all cookies extraction, the variable will be available as `String`.
///
/// # Panics
///
/// This macro will panic if the requested cookie does not exist in the HTTP request headers.
#[proc_macro_attribute]
pub fn request_cookie(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_cookie_macro(attr, item, Position::Prologue)
}

/// Extracts all cookies as a raw string into a variable.
///
/// This attribute macro retrieves the entire Cookie header from the request and makes it
/// available as a String variable. If no Cookie header is present, an empty string is used.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/cookies")]
/// struct Cookies;
///
/// impl ServerHook for Cookies {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[response_body(&format!("All cookies: {cookie_value:?}"))]
///     #[request_cookies(cookie_value)]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl Cookies {
///     #[request_cookies(cookie_value)]
///     async fn request_cookies_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[request_cookies(cookie_value)]
/// async fn standalone_request_cookies_handler(ctx: &Context) {}
/// ```
///
/// The macro accepts a variable name that will contain all cookies.
/// The variable will be available as a Cookies type in the function scope.
#[proc_macro_attribute]
pub fn request_cookies(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_cookies_macro(attr, item, Position::Prologue)
}

/// Extracts the HTTP request version into a variable.
///
/// This attribute macro retrieves the HTTP version from the request and makes it
/// available as a variable. The version represents the HTTP protocol version used.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/request_version")]
/// struct RequestVersionTest;
///
/// impl ServerHook for RequestVersionTest {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[response_body(&format!("HTTP Version: {http_version}"))]
///     #[request_version(http_version)]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl RequestVersionTest {
///     #[request_version(http_version)]
///     async fn request_version_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[request_version(http_version)]
/// async fn standalone_request_version_handler(ctx: &Context) {}
/// ```
///
/// The macro accepts a variable name that will contain the HTTP request version.
/// The variable will be available as a RequestVersion type in the function scope.
#[proc_macro_attribute]
pub fn request_version(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_version_macro(attr, item, Position::Prologue)
}

/// Extracts the HTTP request path into a variable.
///
/// This attribute macro retrieves the request path from the HTTP request and makes it
/// available as a variable. The path represents the URL path portion of the request.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/request_path")]
/// struct RequestPathTest;
///
/// impl ServerHook for RequestPathTest {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[response_body(&format!("Request Path: {request_path}"))]
///     #[request_path(request_path)]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl RequestPathTest {
///     #[request_path(request_path)]
///     async fn request_path_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[request_path(request_path)]
/// async fn standalone_request_path_handler(ctx: &Context) {}
/// ```
///
/// The macro accepts a variable name that will contain the HTTP request path.
/// The variable will be available as a RequestPath type in the function scope.
#[proc_macro_attribute]
pub fn request_path(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_path_macro(attr, item, Position::Prologue)
}

/// Creates a new instance of a specified type with a given variable name.
///
/// This attribute macro generates an instance initialization at the beginning of the function.
///
/// # Usage
///
/// ```rust,no_run
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[hyperlane(server: Server)]
/// #[hyperlane(config: ServerConfig)]
/// #[tokio::main]
/// async fn main() {
///     config.disable_nodelay().await;
///     server.config(config).await;
///     let server_hook: ServerControlHook = server.run().await.unwrap_or_default();
///     server_hook.wait().await;
/// }
/// ```
///
/// The macro accepts a `variable_name: Type` pair.
/// The variable will be available as an instance of the specified type in the function scope.
#[proc_macro_attribute]
pub fn hyperlane(attr: TokenStream, item: TokenStream) -> TokenStream {
    hyperlane_macro(attr, item)
}

/// Registers a function as a route handler.
///
/// This attribute macro registers the decorated function as a route handler for a given path.
/// This macro requires the `#[hyperlane(server: Server)]` macro to be used to define the server instance.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/response")]
/// struct Response;
///
/// impl ServerHook for Response {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[response_body("response")]
///     async fn handle(self, ctx: &Context) {}
/// }
/// ```
///
/// # Parameters
///
/// - `path`: String literal defining the route path
///
/// # Dependencies
///
/// This macro depends on the `#[hyperlane(server: Server)]` macro to define the server instance.
#[proc_macro_attribute]
pub fn route(attr: TokenStream, item: TokenStream) -> TokenStream {
    route_macro(attr, item)
}

/// Registers a function as a request middleware.
///
/// This attribute macro registers the decorated function to be executed as a middleware
/// for incoming requests. This macro requires the `#[hyperlane(server: Server)]` macro to be used to define the server instance.
///
/// # Note
///
/// If an order parameter is not specified, the hook will have a higher priority than hooks with a specified order.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[request_middleware]
/// struct RequestMiddleware;
///
/// impl ServerHook for RequestMiddleware {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[epilogue_macros(
///         response_status_code(200),
///         response_version(HttpVersion::Http1_1),
///         response_header(SERVER => HYPERLANE)
///     )]
///     async fn handle(self, ctx: &Context) {}
/// }
/// ```
///
/// # Dependencies
///
/// This macro depends on the `#[hyperlane(server: Server)]` macro to define the server instance.
#[proc_macro_attribute]
pub fn request_middleware(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_middleware_macro(attr, item)
}

/// Registers a function as a response middleware.
///
/// This attribute macro registers the decorated function to be executed as a middleware
/// for outgoing responses. This macro requires the `#[hyperlane(server: Server)]` macro to be used to define the server instance.
///
/// # Note
///
/// If an order parameter is not specified, the hook will have a higher priority than hooks with a specified order.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[response_middleware]
/// struct ResponseMiddleware1;
///
/// impl ServerHook for ResponseMiddleware1 {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     async fn handle(self, ctx: &Context) {}
/// }
/// ```
///
/// # Dependencies
///
/// This macro depends on the `#[hyperlane(server: Server)]` macro to define the server instance.
#[proc_macro_attribute]
pub fn response_middleware(attr: TokenStream, item: TokenStream) -> TokenStream {
    response_middleware_macro(attr, item)
}

/// Registers a function as a panic hook.
///
/// This attribute macro registers the decorated function to handle panics that occur
/// during request processing. This macro requires the `#[hyperlane(server: Server)]` macro to be used to define the server instance.
///
/// # Note
///
/// If an order parameter is not specified, the hook will have a higher priority than hooks with a specified order.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[panic_hook]
/// #[panic_hook(1)]
/// #[panic_hook("2")]
/// struct PanicHook;
///
/// impl ServerHook for PanicHook {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[epilogue_macros(response_body("panic_hook"), send)]
///     async fn handle(self, ctx: &Context) {}
/// }
/// ```
///
/// # Dependencies
///
/// This macro depends on the `#[hyperlane(server: Server)]` macro to define the server instance.
#[proc_macro_attribute]
pub fn panic_hook(attr: TokenStream, item: TokenStream) -> TokenStream {
    panic_hook_macro(attr, item)
}

/// Injects a list of macros before the decorated function.
///
/// The macros are applied in head-insertion order, meaning the first macro in the list
/// is the outermost macro.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/prologue_macros")]
/// struct PrologueMacros;
///
/// impl ServerHook for PrologueMacros {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[prologue_macros(post, response_body("prologue_macros"), send)]
///     async fn handle(self, ctx: &Context) {}
/// }
/// ```
#[proc_macro_attribute]
pub fn prologue_macros(attr: TokenStream, item: TokenStream) -> TokenStream {
    prologue_macros_macro(attr, item)
}

/// Injects a list of macros after the decorated function.
///
/// The macros are applied in tail-insertion order, meaning the last macro in the list
/// is the outermost macro.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[response_middleware(2)]
/// struct ResponseMiddleware2;
///
/// impl ServerHook for ResponseMiddleware2 {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[epilogue_macros(send, flush)]
///     async fn handle(self, ctx: &Context) {}
/// }
/// ```
#[proc_macro_attribute]
pub fn epilogue_macros(attr: TokenStream, item: TokenStream) -> TokenStream {
    epilogue_macros_macro(attr, item)
}

/// Sends only the response body with data after function execution.
///
/// This attribute macro ensures that only the response body is automatically sent
/// to the client after the function completes, handling request headers separately,
/// with the specified data.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/send_body_with_data")]
/// struct SendBodyWithData;
///
/// impl ServerHook for SendBodyWithData {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[epilogue_macros(send_body_with_data("Response body content"))]
///     async fn handle(self, ctx: &Context) {}
/// }
/// ```
///
/// The macro accepts data to send and should be applied to async functions
/// that accept a `&Context` parameter.
#[proc_macro_attribute]
pub fn send_body_with_data(attr: TokenStream, item: TokenStream) -> TokenStream {
    send_body_with_data_macro(attr, item, Position::Epilogue)
}

/// Wraps function body with WebSocket stream processing.
///
/// This attribute macro generates code that wraps the function body with a check to see if
/// data can be read from a WebSocket stream. The function body is only executed
/// if data is successfully read from the stream.
///
/// This attribute macro generates code that wraps the function body with a check to see if
/// data can be read from a WebSocket stream. The function body is only executed
/// if data is successfully read from the stream.
///
/// # Arguments
///
/// - `TokenStream`: The buffer to read from the WebSocket stream.
/// - `TokenStream`: The function item to be modified
///
/// # Returns
///
/// Returns a TokenStream containing the modified function with WebSocket stream processing logic.
///
/// # Examples
///
/// Using no parameters (default buffer size):
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/ws")]
/// struct Websocket;
///
/// impl ServerHook for Websocket {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[ws]
///     #[ws_from_stream]
///     async fn handle(self, ctx: &Context) {
///         let body: RequestBody = ctx.get_request_body().await;
///         let body_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(&body);
///         ctx.send_body_list_with_data(&body_list).await.unwrap();
///     }
/// }
/// ```
///
/// Using only request config:
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/ws")]
/// struct Websocket;
///
/// impl ServerHook for Websocket {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[ws]
///     #[ws_from_stream(RequestConfig::default())]
///     async fn handle(self, ctx: &Context) {
///         let body: RequestBody = ctx.get_request_body().await;
///         let body_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(&body);
///         ctx.send_body_list_with_data(&body_list).await.unwrap();
///     }
/// }
/// ```
///
/// Using variable name to store request data:
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/ws")]
/// struct Websocket;
///
/// impl ServerHook for Websocket {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[ws]
///     #[ws_from_stream(request)]
///     async fn handle(self, ctx: &Context) {
///         let body: &RequestBody = &request.get_body();
///         let body_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(body);
///         ctx.send_body_list_with_data(&body_list).await.unwrap();
///     }
/// }
/// ```
///
/// Using request config and variable name:
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/ws")]
/// struct Websocket;
///
/// impl ServerHook for Websocket {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[ws]
///     #[ws_from_stream(RequestConfig::default(), request)]
///     async fn handle(self, ctx: &Context) {
///         let body: &RequestBody = request.get_body();
///         let body_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(&body);
///         ctx.send_body_list_with_data(&body_list).await.unwrap();
///     }
/// }
/// ```
///
/// Using variable name and request config (reversed order):
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/ws")]
/// struct Websocket;
///
/// impl ServerHook for Websocket {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[ws]
///     #[ws_from_stream(request, RequestConfig::default())]
///     async fn handle(self, ctx: &Context) {
///         let body: &RequestBody = request.get_body();
///         let body_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(&body);
///         ctx.send_body_list_with_data(&body_list).await.unwrap();
///     }
/// }
///
/// impl Websocket {
///     #[ws_from_stream(request)]
///     async fn ws_from_stream_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[ws_from_stream]
/// async fn standalone_ws_from_stream_handler(ctx: &Context) {}
/// ```
#[proc_macro_attribute]
pub fn ws_from_stream(attr: TokenStream, item: TokenStream) -> TokenStream {
    ws_from_stream_macro(attr, item)
}

/// Wraps function body with HTTP stream processing.
///
/// This attribute macro generates code that wraps the function body with a check to see if
/// data can be read from an HTTP stream. The function body is only executed
/// if data is successfully read from the stream.
///
/// This attribute macro generates code that wraps the function body with a check to see if
/// data can be read from an HTTP stream. The function body is only executed
/// if data is successfully read from the stream.
///
/// # Arguments
///
/// - `TokenStream`: The buffer to read from the HTTP stream.
/// - `TokenStream`: The function item to be modified
///
/// # Returns
///
/// Returns a TokenStream containing the modified function with HTTP stream processing logic.
///
/// # Examples
///
/// Using with epilogue_macros:
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/http_from_stream")]
/// struct HttpFromStreamTest;
///
/// impl ServerHook for HttpFromStreamTest {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[epilogue_macros(
///         request_query("test" => request_query_option),
///         response_body(&format!("request query: {request_query_option:?}")),
///         send,
///         http_from_stream(RequestConfig::default())
///     )]
///     async fn handle(self, ctx: &Context) {}
/// }
/// ```
///
/// Using with variable name:
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[route("/http_from_stream")]
/// struct HttpFromStreamTest;
///
/// impl ServerHook for HttpFromStreamTest {
///     async fn new(_ctx: &Context) -> Self {
///         Self
///     }
///
///     #[epilogue_macros(
///         http_from_stream(_request)
///     )]
///     async fn handle(self, ctx: &Context) {}
/// }
///
/// impl HttpFromStreamTest {
///     #[http_from_stream(_request)]
///     async fn http_from_stream_with_ref_self(&self, ctx: &Context) {}
/// }
///
/// #[http_from_stream]
/// async fn standalone_http_from_stream_handler(ctx: &Context) {}
/// ```
#[proc_macro_attribute]
pub fn http_from_stream(attr: TokenStream, item: TokenStream) -> TokenStream {
    http_from_stream_macro(attr, item)
}

```

# Path: hyperlane-macros\src\aborted\fn.rs

```rust
use crate::*;

/// Expands the macro to generate an asynchronous aborted call.
///
/// This macro takes a `TokenStream` as input, which typically represents
/// the context of a function or block, and inserts a call to `.aborted().await`
/// on that context. This is useful for ensuring that a component gracefully
/// handles being aborted.
///
/// # Arguments
///
/// - `TokenStream` - The input `TokenStream` to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// Returns the expanded `TokenStream` with the aborted call inserted.
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

# Path: hyperlane-macros\src\aborted\mod.rs

```rust
mod r#fn;

pub(crate) use r#fn::*;

```

# Path: hyperlane-macros\src\closed\fn.rs

```rust
use crate::*;

/// Expands the macro to generate an asynchronous closed call.
///
/// This macro takes a `TokenStream` as input, which typically represents
/// the context of a function or block, and inserts a call to `.closed().await`
/// on that context. This is useful for ensuring that a component gracefully
/// handles being closed.
///
/// # Arguments
///
/// - `TokenStream` - The input `TokenStream` to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// Returns the expanded `TokenStream` with the closed call inserted.
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

# Path: hyperlane-macros\src\closed\mod.rs

```rust
mod r#fn;

pub(crate) use r#fn::*;

```

# Path: hyperlane-macros\src\common\const.rs

```rust
pub(crate) const SERVER_TYPE_KEY: &str = "Server";

```

# Path: hyperlane-macros\src\common\enum.rs

```rust
use crate::*;

/// Defines the type of macro handler.
///
/// This enum distinguishes between simple macros that do not accept attributes
/// and more complex macros that can process attribute inputs. It is used to route
/// macro invocations to the appropriate expansion logic based on their expected syntax.
pub(crate) enum Handler {
    /// A macro handler for macros that accept attribute arguments.
    ///
    /// This variant is used for macros that support syntax like `#[my_macro(...)]`,
    /// where the content inside the parentheses is parsed and processed as input.
    /// The `MacroHandlerWithAttr` contains the logic to interpret and expand such macros.
    WithAttr(MacroHandlerWithAttr),
    /// A macro handler for simple macros that do not take any attributes.
    ///
    /// This variant is used for attribute-like macros that are invoked as `#[my_macro]`
    /// without any additional arguments. The associated `MacroHandlerPosition` is responsible
    /// for handling the macro at a specific location in the syntax tree.
    NoAttrPosition(MacroHandlerPosition),
    /// A macro handler for macros that accept attribute arguments and depend on position.
    ///
    /// This variant is used for macros with syntax like `#[my_macro(...)]`, similar to `WithAttr`.
    /// The difference is that `WithAttrPosition` also incorporates the syntactic position
    /// of the macro invocation into the expansion logic.
    /// The `MacroHandlerWithAttrPosition` handles both the attribute input and the positional context.
    WithAttrPosition(MacroHandlerWithAttrPosition),
}

/// Defines the position where code should be injected in a function.
pub(crate) enum Position {
    /// Injects code at the beginning of the function body.
    Prologue,
    /// Injects code at the end of the function body.
    Epilogue,
}

```

# Path: hyperlane-macros\src\common\fn.rs

```rust
use crate::*;

/// Expands macro with code inserted before method body.
///
/// # Arguments
///
/// - `TokenStream` - The input token stream to process.
/// - `impl FnOnce(&Ident) -> TokenStream2` - Function to generate code inserted before.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with inserted code.
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

/// Expands macro with code inserted after method body.
///
/// # Arguments
///
/// - `TokenStream` - The input `TokenStream` to process.
/// - `impl FnOnce(&Ident) -> TokenStream2` - A closure that takes a context identifier and returns a `TokenStream` to be inserted at the end of the method.
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

/// Injects code into a method at a specified position.
///
/// # Arguments
///
/// - `Position` - The position at which to inject the code (`Prologue` or `Epilogue`).
/// - `TokenStream` - The input `TokenStream` of the method to modify.
/// - `impl FnOnce(&Ident) -> TokenStream2` - A closure that generates the code to be injected, based on the method's context identifier.
///
/// # Returns
///
/// - `TokenStream` - Returns the modified `TokenStream` with the injected code.
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

/// Parses context identifier from function signature.
///
/// # Arguments
///
/// - `&Signature` - The function signature to parse.
///
/// # Returns
///
/// - `syn::Result<&Ident>` - Returns a `syn::Result` containing the context identifier if successful, or an error otherwise.
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

/// Parses self from method signature and returns the context identifier (second parameter).
///
/// # Arguments
///
/// - `&Signature` - The method signature to parse.
///
/// # Returns
///
/// - `syn::Result<&Ident>` - Returns the context identifier from the second parameter.
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

/// Checks if a type matches `::hyperlane::Context`.
///
/// This function checks if the given type is a reference to `::hyperlane::Context`.
///
/// # Arguments
///
/// - `&Type` - The type to check.
///
/// # Returns
///
/// - `bool` - Returns `true` if the type is `&::hyperlane::Context` or `&Context`, `false` otherwise.
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

/// Parses context identifier from function signature by searching all parameters.
///
/// This function iterates through all function parameters and returns the first one
/// that has type `::hyperlane::Context`. It supports:
/// 1. Methods with self: Searches from the second parameter onwards
/// 2. Functions without self: Searches from the first parameter onwards
/// 3. Context parameter can be at any position
///
/// # Arguments
///
/// - `&Signature` - The function signature to parse.
///
/// # Returns
///
/// - `syn::Result<&Ident>` - Returns the context identifier.
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

/// Convert an optional expression into an `Option<isize>` token stream.
///
/// This function supports integer and string literals only:
/// - Integer literals are parsed and converted into `Some(isize)`.
/// - String literals are parsed into `isize` and wrapped in `Some(...)`.
/// - Any other expression types will result in `None`.
/// - If `opt_expr` is `None`, the result is also `None`.
///
/// # Arguments
///
/// - `&Option<Expr>` - An optional reference to the expression to convert.
///
/// # Returns
///
/// - `TokenStream` - A `TokenStream2` representing `Some(isize)` for supported literals, or `None` otherwise.
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

/// Checks if an expression is an integer literal or RequestConfig::default().
///
/// # Arguments
///
/// - `expr` - The expression to check.
///
/// # Returns
///
/// - `bool` - Returns `true` if the expression is an integer literal or RequestConfig::default(), `false` otherwise.
pub(crate) fn is_integer_literal(expr: &Expr) -> bool {
    // Check for integer literals
    if matches!(
        expr,
        Expr::Lit(ExprLit {
            lit: Lit::Int(_),
            ..
        })
    ) {
        return true;
    }

    // Check for RequestConfig::default() function calls
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

# Path: hyperlane-macros\src\common\impl.rs

```rust
use crate::*;

/// Parses the attributes for the `OrderAttr` macro.
///
/// This implementation of the `Parse` trait allows `syn` to parse
/// an optional `order` from the macro's attribute tokens.
/// If no order is provided, it defaults to `0`.
impl Parse for OrderAttr {
    /// Parses the input stream into an `OrderAttr` struct.
    ///
    /// # Arguments
    ///
    /// - `input` - The token stream to parse.
    ///
    /// # Returns
    ///
    /// A `Result` containing the parsed `OrderAttr` or an error.
    fn parse(input: ParseStream) -> Result<Self> {
        if input.is_empty() {
            return Ok(OrderAttr { order: None });
        }
        let expr: Expr = input.parse()?;
        Ok(OrderAttr { order: Some(expr) })
    }
}

```

# Path: hyperlane-macros\src\common\mod.rs

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

# Path: hyperlane-macros\src\common\struct.rs

```rust
use crate::*;

/// Represents a parsed macro attribute containing an optional order.
///
/// This struct is used during macro parsing to hold the extracted order expression.
/// Hooks or attributes that do not specify an order will have `None`.
#[derive(Clone)]
pub(crate) struct OrderAttr {
    /// The optional order expression provided in the macro attribute.
    pub(crate) order: Option<Expr>,
}

/// Represents a macro that can be injected.
///
/// This struct is used to define a macro that can be collected and used by the `inventory` crate.
pub(crate) struct InjectableMacro {
    /// The name of the macro.
    pub(crate) name: &'static str,
    /// The handler for the macro.
    pub(crate) handler: Handler,
}

```

# Path: hyperlane-macros\src\common\type.rs

```rust
use crate::*;

/// A type alias for a simple macro handler function.
///
/// This handler takes a single `TokenStream` as input and returns a `TokenStream`.
pub(crate) type MacroHandlerPosition = fn(TokenStream, Position) -> TokenStream;

/// A type alias for a macro handler function that accepts attributes.
///
/// This handler takes two `TokenStream`s as input (one for attributes, one for the item)
/// and returns a `TokenStream`.
pub(crate) type MacroHandlerWithAttr = fn(TokenStream, TokenStream) -> TokenStream;

/// A type alias for a macro handler function that accepts attributes and a position.
///
/// This handler takes two `TokenStream`s as input (one for attributes, one for the item),
/// a `Position` enum, and returns a `TokenStream`.
pub(crate) type MacroHandlerWithAttrPosition =
    fn(TokenStream, TokenStream, Position) -> TokenStream;

```

# Path: hyperlane-macros\src\filter\fn.rs

```rust
use crate::*;

/// Filters requests based on a boolean condition.
///
/// The function continues execution only if the provided code block returns `true`.
///
/// # Arguments
///
/// - `TokenStream` - A code block that returns a boolean value.
/// - `TokenStream` - The function to which the attribute is applied.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The modified function wrapped with a conditional guard;
///   the original function body is executed only if the condition is `true`,
///   otherwise the function returns early without doing anything.
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

# Path: hyperlane-macros\src\filter\mod.rs

```rust
mod r#fn;

pub(crate) use r#fn::*;

```

# Path: hyperlane-macros\src\flush\fn.rs

```rust
use crate::*;

/// Expands macro to generate async flush call.
///
/// # Arguments
///
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with flush call.
pub(crate) fn flush_macro(item: TokenStream, position: Position) -> TokenStream {
    inject(position, item, |context| {
        quote! {
            let _ = #context.flush().await;
        }
    })
}

inventory::submit! {
    InjectableMacro {
        name: "flush",
        handler: Handler::NoAttrPosition(flush_macro),
    }
}

```

# Path: hyperlane-macros\src\flush\mod.rs

```rust
mod r#fn;

pub(crate) use r#fn::*;

```

# Path: hyperlane-macros\src\from_stream\impl.rs

```rust
use crate::*;

/// Implementation of Parse trait for FromStreamData.
///
/// This implementation handles parsing of macro attributes that specify stream processing parameters.
/// It supports various parameter combinations including request config, variable name, or both.
/// The parser validates input syntax and semantic correctness according to the macro's requirements.
///
/// # Arguments
/// - `input`: The parse stream containing the token stream to be parsed
///
/// # Returns
/// Returns a `syn::Result<Self>` containing the parsed FromStreamData on success,
/// or a syn::Error with appropriate error message on failure
///
/// # Errors
/// This function returns an error when:
/// - No parameters are provided
/// - Two request config parameters are provided
/// - Two variable name parameters are provided
/// - Additional unexpected tokens are present after valid parameters
/// - A comma is present without a second parameter following it
impl Parse for FromStreamData {
    /// Parses the input token stream into a FromStreamData structure.
    ///
    /// This method implements the core parsing logic for the FromStream macro attribute.
    /// It handles three possible parameter configurations:
    /// 1. Single parameter: interpreted as request config if integer literal, otherwise as variable name
    /// 2. Two parameters: first as request config, second as variable name (order independent)
    /// 3. No parameters: results in an error
    ///
    /// The method performs comprehensive validation of the input syntax and semantics,
    /// ensuring that the resulting FromStreamData structure is valid and consistent.
    ///
    /// # Arguments
    /// - `ParseStream`: The ParseStream containing the token stream to be parsed
    ///
    /// # Returns
    /// Returns `syn::Result<Self>` where:
    /// - Ok(FromStreamData) contains the successfully parsed data with request config and variable name
    /// - Err(syn::Error) contains an appropriate error message for invalid input
    ///
    /// # Errors
    /// The function returns errors in the following cases:
    /// - Empty input: when no parameters are provided
    /// - Two integer literals: when both parameters are request configs
    /// - Two non-integer expressions: when both parameters are variable names
    /// - Malformed syntax: when comma is present without a second parameter
    /// - Extra tokens: when additional tokens are present after valid parameters
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

# Path: hyperlane-macros\src\from_stream\mod.rs

```rust
mod r#impl;
mod r#struct;

pub(crate) use r#struct::*;

```

# Path: hyperlane-macros\src\from_stream\struct.rs

```rust
use crate::*;

/// Represents data for stream processing.
///
/// This struct holds the request_config and variable name for stream processing.
pub(crate) struct FromStreamData {
    /// The request config to read from the stream.
    pub(crate) request_config: Option<Expr>,
    /// The variable name to store the read data.
    pub(crate) variable_name: Option<Expr>,
}

```

# Path: hyperlane-macros\src\hook\fn.rs

```rust
use crate::*;

/// Registers a panic hook.
///
/// This macro takes a struct as input and registers it as a panic hook.
/// The registered struct will be used to create handlers when a panic occurs within the application.
///
/// # Arguments
///
/// - `TokenStream` - The attribute `TokenStream`, which can optionally specify an `order`.
/// - `TokenStream` - The input `TokenStream` representing the struct to be registered as a hook.
///
/// # Note
///
/// If an order parameter is not specified, the hook will have a higher priority than hooks with a specified order.
///
/// # Returns
///
/// Returns the expanded `TokenStream` with the hook registration.
pub(crate) fn panic_hook_macro(attr: TokenStream, item: TokenStream) -> TokenStream {
    let attr_args: OrderAttr = parse_macro_input!(attr as OrderAttr);
    let order: TokenStream2 = expr_to_isize(&attr_args.order);
    let input_struct: ItemStruct = parse_macro_input!(item as ItemStruct);
    let struct_name: &Ident = &input_struct.ident;
    let gen_code: TokenStream2 = quote! {
        #input_struct
        ::hyperlane::inventory::submit! {
            ::hyperlane::HookMacro {
                hook_type: ::hyperlane::HookType::PanicHook(#order),
                handler: ::hyperlane::HookHandlerSpec::Factory(|| ::hyperlane::server_hook_factory::<#struct_name>()),
            }
        }
    };
    gen_code.into()
}

inventory::submit! {
    InjectableMacro {
        name: "panic_hook",
        handler: Handler::WithAttr(panic_hook_macro),
    }
}

/// Expands macro to add multiple pre-hook function calls.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream containing a list of function names.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// Returns the expanded `TokenStream` with multiple pre-hook calls.
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

/// Expands macro to add multiple post-hook function calls.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream containing a list of function names.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// Returns the expanded `TokenStream` with multiple post-hook calls.
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

# Path: hyperlane-macros\src\hook\mod.rs

```rust
mod r#fn;

pub(crate) use r#fn::*;

```

# Path: hyperlane-macros\src\host\fn.rs

```rust
use crate::*;

/// Filters requests matching the specified host.
/// Supports both single and multiple host value checks.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with host filter.
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

/// Rejects requests matching the specified host.
/// Supports both single and multiple host value checks.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with host rejection filter.
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

# Path: hyperlane-macros\src\host\impl.rs

```rust
use crate::*;

/// Implementation of Parse trait for MultiHostData.
///
/// Parses host value expressions from input stream.
/// Supports both single and multiple host values.
///
/// # Arguments
///
/// - `ParseStream` - The input parse stream.
///
/// # Returns
///
/// - `syn::Result<MultiHostData>` - Parsed MultiHostData or error.
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

# Path: hyperlane-macros\src\host\mod.rs

```rust
pub(crate) mod r#fn;
pub(crate) mod r#impl;
pub(crate) mod r#struct;

pub(crate) use r#fn::*;
pub(crate) use r#struct::*;

```

# Path: hyperlane-macros\src\host\struct.rs

```rust
use crate::*;

/// Host data container storing host value expressions.
///
/// Used for host matching in request processing.
/// Supports both single and multiple host values.
pub(crate) struct MultiHostData {
    /// Vector of host value expressions to match against.
    pub(crate) host_values: Vec<Expr>,
}

```

# Path: hyperlane-macros\src\http\fn.rs

```rust
use crate::*;

/// Implements an HTTP method macro.
///
/// This macro generates a handler function for a specific HTTP method (e.g., GET, POST).
/// It expands to a check that aborts the request if the HTTP method does not match.
///
/// # Arguments
///
/// - `$name` - The name of the generated handler function.
/// - `$method` - The HTTP method as a string literal (e.g., "get", "post").
///
/// # Returns
///
/// Returns a macro that generates a handler function for the specified HTTP method.
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
impl_http_method_macro!(epilogue_handler, "post");
impl_http_method_macro!(put_handler, "put");
impl_http_method_macro!(delete_handler, "delete");
impl_http_method_macro!(patch_handler, "patch");
impl_http_method_macro!(head_handler, "head");
impl_http_method_macro!(options_handler, "options");
impl_http_method_macro!(connect_handler, "connect");
impl_http_method_macro!(trace_handler, "trace");

/// Creates a method check function for HTTP request validation.
///
/// # Arguments
///
/// - `method_name` - The HTTP method name as a string.
/// - `span` - The span for error reporting.
///
/// # Returns
///
/// Returns a closure that generates the method check code.
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

/// Handles HTTP requests for multiple method types.
///
/// This macro allows a handler to respond to multiple HTTP methods.
/// It generates code that checks if the request method matches any of the specified methods.
///
/// # Arguments
///
/// - `TokenStream` - The attribute `TokenStream` containing the list of allowed HTTP methods.
/// - `TokenStream` - The input `TokenStream` representing the handler function.
/// - `Position` - The position at which to inject the method check code.
///
/// # Returns
///
/// Returns the expanded `TokenStream` with the methods check code injected.
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

# Path: hyperlane-macros\src\http\mod.rs

```rust
mod r#fn;

pub(crate) use r#fn::*;

```

# Path: hyperlane-macros\src\hyperlane\fn.rs

```rust
use crate::*;

/// Main macro for creating and configuring a Hyperlane server instance.
/// Supports both single and multiple variable-type pair initialization.
///
/// This macro expects an attribute in the format `#[hyperlane(variable_name: TypeName)]`
/// or `#[hyperlane(var1: Type1, var2: Type2, ...)]`.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream, containing the variable and type name.
/// - `TokenStream` - The input token stream to process, typically an `async fn`.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with server initialization.
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
                let mut hooks: Vec<::hyperlane::HookMacro> = inventory::iter().cloned().collect();
                assert_hook_unique_order(hooks.clone());
                hooks.sort_by_key(|hook| hook.hook_type.try_get());
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

# Path: hyperlane-macros\src\hyperlane\impl.rs

```rust
use crate::*;

/// Implementation of the `Parse` trait for `MultiHyperlaneAttr`.
///
/// This implementation allows parsing multiple variable-type pairs from a token stream,
/// expecting the format `variable_name: TypeName, variable_name2: TypeName2, ...`.
/// Also supports single pair format for backward compatibility.
///
/// # Arguments
///
/// - `ParseStream` - The `ParseStream` to parse from.
///
/// # Returns
///
/// A `syn::Result` containing the parsed `MultiHyperlaneAttr` or an error.
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

# Path: hyperlane-macros\src\hyperlane\mod.rs

```rust
pub(crate) mod r#fn;
pub(crate) mod r#impl;
pub(crate) mod r#struct;

pub(crate) use r#fn::*;
pub(crate) use r#struct::*;

```

# Path: hyperlane-macros\src\hyperlane\struct.rs

```rust
use crate::*;

/// Represents attributes for the Hyperlane macro.
///
/// Used to store parsed variable-type pairs from macro input.
/// Supports both single and multiple pairs.
pub(crate) struct MultiHyperlaneAttr {
    /// Vector of variable-type pairs.
    pub(crate) params: Vec<(Ident, Ident)>,
}

```

# Path: hyperlane-macros\src\inject\fn.rs

```rust
use crate::*;

/// Applies a macro to a token stream.
///
/// This function takes a macro's metadata and a token stream, finds the corresponding
/// registered macro, and applies it.
///
/// # Arguments
///
/// - `&Meta` - The metadata of the macro to apply.
/// - `TokenStream` - The token stream to apply the macro to.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// The resulting token stream after applying the macro.
///
/// # Panics
///
/// This function will panic if the macro is not found, if the macro format is unsupported,
/// or if a simple macro is given attributes.
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

/// Injects a list of macros before the decorated function.
///
/// The macros are applied in head-insertion order, meaning the first macro in the list
/// is the outermost macro.
///
/// # Arguments
///
/// - `TokenStream` - The token stream representing the attributes of the macro.
/// - `TokenStream` - The token stream representing the item to which the macro is applied.
///
/// # Returns
///
/// The resulting token stream after applying all the prologue hooks.
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

/// Injects a list of macros after the decorated function.
///
/// The macros are applied in tail-insertion order, meaning the last macro in the list
/// is the outermost macro.
///
/// # Arguments
///
/// - `TokenStream` - The token stream representing the attributes of the macro.
/// - `TokenStream` - The token stream representing the item to which the macro is applied.
///
/// # Returns
///
/// The resulting token stream after applying all the epilogue hooks.
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

# Path: hyperlane-macros\src\inject\mod.rs

```rust
pub(crate) mod r#fn;

pub(crate) use r#fn::*;

```

# Path: hyperlane-macros\src\protocol\fn.rs

```rust
use crate::*;

/// Checks if request is WebSocket protocol.
///
/// # Arguments
///
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with protocol check.
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

/// Checks if request is HTTP protocol.
///
/// # Arguments
///
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with protocol check.
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

/// Implements a protocol check macro.
///
/// This macro generates a function that checks if the request matches a specific protocol.
/// If the protocol does not match, the request is aborted.
///
/// # Arguments
///
/// - `$name`: The name of the generated macro function.
/// - `$check`: The name of the method to call on the request to perform the protocol check (e.g., `is_h2c`).
macro_rules! impl_protocol_check_macro {
    ($name:ident, $check:ident, $str_name:expr) => {
        /// Checks if the request matches a specific protocol.
        ///
        /// # Arguments
        ///
        /// - `TokenStream` - The input token stream to process.
        /// - `Position` - The position to inject the code.
        ///
        /// # Returns
        ///
        /// The expanded token stream with protocol check.
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

# Path: hyperlane-macros\src\protocol\mod.rs

```rust
mod r#fn;

pub(crate) use r#fn::*;

```

# Path: hyperlane-macros\src\referer\fn.rs

```rust
use crate::*;

/// Filters requests matching the specified Referer header.
/// Supports both single and multiple referer value checks.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with Referer filter.
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

/// Rejects requests matching the specified Referer header.
/// Supports both single and multiple referer value checks.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with Referer rejection filter.
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

# Path: hyperlane-macros\src\referer\impl.rs

```rust
use crate::*;

/// Implementation of Parse trait for MultiRefererData.
///
/// Parses referer value expressions from input stream.
/// Supports both single and multiple referer values.
///
/// # Arguments
///
/// - `ParseStream` - The input parse stream.
///
/// # Returns
///
/// - `syn::Result<MultiRefererData>` - Parsed MultiRefererData or error.
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

# Path: hyperlane-macros\src\referer\mod.rs

```rust
mod r#fn;
mod r#impl;
mod r#struct;

pub(crate) use r#fn::*;
pub(crate) use r#struct::*;

```

# Path: hyperlane-macros\src\referer\struct.rs

```rust
use crate::*;

/// Referer data container storing referer value expressions.
///
/// Used for Referer header matching in request processing.
/// Supports both single and multiple referer values.
pub(crate) struct MultiRefererData {
    /// Vector of referer value expressions to match against.
    pub(crate) referer_values: Vec<Expr>,
}

```

# Path: hyperlane-macros\src\reject\fn.rs

```rust
use crate::*;

/// Rejects requests based on a boolean condition.
///
/// The function returns early if the provided code block returns `true`.
///
/// # Arguments
///
/// - `TokenStream` - A code block that returns a boolean value.
/// - `TokenStream` - The function to which the attribute is applied.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The modified function wrapped with a conditional check;
///   if the condition evaluates to `true`, the function returns early,
///   otherwise the original function body is executed.
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

# Path: hyperlane-macros\src\reject\mod.rs

```rust
mod r#fn;

pub(crate) use r#fn::*;

```

# Path: hyperlane-macros\src\request\fn.rs

```rust
use crate::*;

/// Gets raw request body and assigns to specified variable.
/// Supports both single and multiple variable extraction.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with body extraction.
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

/// Parses request body as JSON and assigns to specified variable.
/// Supports both single and multiple variable-type pair extraction.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with JSON parsing.
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

/// Parses request body as JSON and assigns to specified variable.
/// Supports both single and multiple variable-type pair extraction.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with JSON parsing.
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

/// Gets request attribute by key and assigns to specified variable.
/// Supports both single and multiple attribute extraction.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with attribute extraction.
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

/// Gets request attribute by key and assigns to specified variable.
/// Supports both single and multiple attribute extraction.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with attribute extraction.
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

/// Gets all request attributes and assigns to specified variable.
/// Supports both single and multiple variable extraction.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with attributes extraction.
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

/// Gets route parameter by key and assigns to specified variable.
/// Supports both single and multiple route parameter extraction.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with route param extraction.
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

/// Gets route parameter by key and assigns to specified variable.
/// Supports both single and multiple route parameter extraction.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with route param extraction.
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

/// Gets all route parameters and assigns to specified variable.
/// Supports both single and multiple variable extraction.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with route params extraction.
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

/// Gets request query parameter by key and assigns to specified variable.
/// Supports both single and multiple parameter extraction.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with query param extraction.
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

/// Gets request query parameter by key and assigns to specified variable.
/// Supports both single and multiple parameter extraction.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with query param extraction.
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

/// Gets all request query parameters and assigns to specified variable.
/// Supports both single and multiple variable extraction.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with query params extraction.
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

/// Gets request header by key and assigns to specified variable.
/// Supports both single and multiple header extraction.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with header extraction.
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

/// Gets request header by key and assigns to specified variable.
/// Supports both single and multiple header extraction.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with header extraction.
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

/// Gets all request headers and assigns to specified variable.
/// Supports both single and multiple variable extraction.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with headers extraction.
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

/// Gets request cookie by key and assigns to specified variable.
/// Supports both single and multiple cookie extraction.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with cookie extraction.
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

/// Gets request cookie by key and assigns to specified variable.
/// Supports both single and multiple cookie extraction.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with cookie extraction.
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

/// Gets all request cookies and assigns to specified variable.
/// Supports both single and multiple variable extraction.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with cookies extraction.
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

/// Gets request version and assigns to specified variable.
/// Supports both single and multiple variable extraction.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with version extraction.
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

/// Gets request path and assigns to specified variable.
/// Supports both single and multiple variable extraction.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with path extraction.
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

# Path: hyperlane-macros\src\request\impl.rs

```rust
use crate::*;

/// Implementation of Parse trait for RequestMethods.
///
/// Parses HTTP methods from input stream.
///
/// # Arguments
///
/// - `ParseStream` - The input parse stream.
///
/// # Returns
///
/// - `syn::Result<RequestMethods>` - Parsed RequestMethods or error.
impl Parse for RequestMethods {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        Ok(RequestMethods {
            methods: Punctuated::parse_separated_nonempty(input)?,
        })
    }
}

/// Implementation of Parse trait for MultiRequestBodyData.
///
/// Parses request body variables from input stream.
/// Supports both single and multiple variables.
///
/// # Arguments
///
/// - `ParseStream` - The input parse stream.
///
/// # Returns
///
/// - `syn::Result<MultiRequestBodyData>` - Parsed MultiRequestBodyData or error.
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

/// Implementation of Parse trait for MultiRequestBodyJsonData.
///
/// Parses request body JSON variable-type pairs from input stream.
/// Supports both single and multiple pairs.
///
/// # Arguments
///
/// - `ParseStream` - The input parse stream.
///
/// # Returns
///
/// - `syn::Result<MultiRequestBodyJsonData>` - Parsed MultiRequestBodyJsonData or error.
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

/// Implementation of Parse trait for MultiAttributeData.
///
/// Parses attribute key-variable-type tuples from input stream.
/// Supports both single and multiple tuples.
///
/// # Arguments
///
/// - `ParseStream` - The input parse stream.
///
/// # Returns
///
/// - `syn::Result<MultiAttributeData>` - Parsed MultiAttributeData or error.
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

/// Implementation of Parse trait for MultiAttributesData.
///
/// Parses attributes variables from input stream.
/// Supports both single and multiple variables.
///
/// # Arguments
///
/// - `ParseStream` - The input parse stream.
///
/// # Returns
///
/// - `syn::Result<MultiAttributesData>` - Parsed MultiAttributesData or error.
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

/// Implementation of Parse trait for MultiRouteParamData.
///
/// Parses route parameter key-variable pairs from input stream.
/// Supports both single and multiple pairs.
///
/// # Arguments
///
/// - `ParseStream` - The input parse stream.
///
/// # Returns
///
/// - `syn::Result<MultiRouteParamData>` - Parsed MultiRouteParamData or error.
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

/// Implementation of Parse trait for MultiRouteParamsData.
///
/// Parses route parameters variables from input stream.
/// Supports both single and multiple variables.
///
/// # Arguments
///
/// - `ParseStream` - The input parse stream.
///
/// # Returns
///
/// - `syn::Result<MultiRouteParamsData>` - Parsed MultiRouteParamsData or error.
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

/// Implementation of Parse trait for MultiQueryData.
///
/// Parses query parameter key-variable pairs from input stream.
/// Supports both single and multiple pairs.
///
/// # Arguments
///
/// - `ParseStream` - The input parse stream.
///
/// # Returns
///
/// - `syn::Result<MultiQueryData>` - Parsed MultiQueryData or error.
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

/// Implementation of Parse trait for MultiQuerysData.
///
/// Parses query parameters variables from input stream.
/// Supports both single and multiple variables.
///
/// # Arguments
///
/// - `ParseStream` - The input parse stream.
///
/// # Returns
///
/// - `syn::Result<MultiQuerysData>` - Parsed MultiQuerysData or error.
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

/// Implementation of Parse trait for MultiHeaderData.
///
/// Parses header key-variable pairs from input stream.
/// Supports both single and multiple pairs.
///
/// # Arguments
///
/// - `ParseStream` - The input parse stream.
///
/// # Returns
///
/// - `syn::Result<MultiHeaderData>` - Parsed MultiHeaderData or error.
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

/// Implementation of Parse trait for MultiHeadersData.
///
/// Parses headers variables from input stream.
/// Supports both single and multiple variables.
///
/// # Arguments
///
/// - `ParseStream` - The input parse stream.
///
/// # Returns
///
/// - `syn::Result<MultiHeadersData>` - Parsed MultiHeadersData or error.
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

/// Implementation of Parse trait for MultiCookieData.
///
/// Parses cookie key-variable pairs from input stream.
/// Supports both single and multiple pairs.
///
/// # Arguments
///
/// - `ParseStream` - The input parse stream.
///
/// # Returns
///
/// - `syn::Result<MultiCookieData>` - Parsed MultiCookieData or error.
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

/// Implementation of Parse trait for MultiCookiesData.
///
/// Parses cookies variables from input stream.
/// Supports both single and multiple variables.
///
/// # Arguments
///
/// - `ParseStream` - The input parse stream.
///
/// # Returns
///
/// - `syn::Result<MultiCookiesData>` - Parsed MultiCookiesData or error.
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

/// Implementation of Parse trait for MultiRequestVersionData.
///
/// Parses request version variables from input stream.
/// Supports both single and multiple variables.
///
/// # Arguments
///
/// - `ParseStream` - The input parse stream.
///
/// # Returns
///
/// - `syn::Result<MultiRequestVersionData>` - Parsed MultiRequestVersionData or error.
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

/// Implementation of Parse trait for MultiRequestPathData.
///
/// Parses request path variables from input stream.
/// Supports both single and multiple variables.
///
/// # Arguments
///
/// - `ParseStream` - The input parse stream.
///
/// # Returns
///
/// - `syn::Result<MultiRequestPathData>` - Parsed MultiRequestPathData or error.
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

```

# Path: hyperlane-macros\src\request\mod.rs

```rust
mod r#fn;
mod r#impl;
mod r#struct;

pub(crate) use r#fn::*;
pub(crate) use r#struct::*;

```

# Path: hyperlane-macros\src\request\struct.rs

```rust
use crate::*;

/// Container for HTTP methods data.
///
/// Used to store parsed HTTP methods from macro input.
pub(crate) struct RequestMethods {
    /// The parsed HTTP methods as punctuated identifiers.
    pub(crate) methods: Punctuated<Ident, Token![,]>,
}

/// Container for request body data.
///
/// Used to store parsed request body variables from macro input.
/// Supports both single and multiple variables.
pub(crate) struct MultiRequestBodyData {
    /// Vector of request body variables.
    pub(crate) variables: Vec<Ident>,
}

/// Container for JSON request body data.
///
/// Used to store parsed JSON request body variable-type pairs from macro input.
/// Supports both single and multiple variable-type pairs.
pub(crate) struct MultiRequestBodyJsonData {
    /// Vector of JSON request body variable-type pairs.
    pub(crate) params: Vec<(Ident, Type)>,
}

/// Container for request attributes data.
///
/// Used to store parsed attribute key-variable-type tuples from macro input.
/// Supports both single and multiple tuples.
pub(crate) struct MultiAttributeData {
    /// Vector of attribute key-variable-type tuples.
    pub(crate) params: Vec<(Expr, Ident, Type)>,
}

/// Container for request attributes collection data.
///
/// Used to store parsed attributes variables from macro input.
/// Supports both single and multiple variables.
pub(crate) struct MultiAttributesData {
    /// Vector of attributes variables.
    pub(crate) variables: Vec<Ident>,
}

/// Container for route parameters data.
///
/// Used to store parsed route parameter key-variable pairs from macro input.
/// Supports both single and multiple pairs.
pub(crate) struct MultiRouteParamData {
    /// Vector of route parameter key-variable pairs.
    pub(crate) params: Vec<(Expr, Ident)>,
}

/// Container for route parameters collection data.
///
/// Used to store parsed route parameters variables from macro input.
/// Supports both single and multiple variables.
pub(crate) struct MultiRouteParamsData {
    /// Vector of route parameters variables.
    pub(crate) variables: Vec<Ident>,
}

/// Container for query parameters data.
///
/// Used to store parsed query parameter key-variable pairs from macro input.
/// Supports both single and multiple pairs.
pub(crate) struct MultiQueryData {
    /// Vector of query parameter key-variable pairs.
    pub(crate) params: Vec<(Expr, Ident)>,
}

/// Container for query parameters collection data.
///
/// Used to store parsed query parameters variables from macro input.
/// Supports both single and multiple variables.
pub(crate) struct MultiQuerysData {
    /// Vector of query parameters variables.
    pub(crate) variables: Vec<Ident>,
}

/// Container for request headers data.
///
/// Used to store parsed header key-variable pairs from macro input.
/// Supports both single and multiple pairs.
pub(crate) struct MultiHeaderData {
    /// Vector of header key-variable pairs.
    pub(crate) params: Vec<(Expr, Ident)>,
}

/// Container for request headers collection data.
///
/// Used to store parsed headers variables from macro input.
/// Supports both single and multiple variables.
pub(crate) struct MultiHeadersData {
    /// Vector of headers variables.
    pub(crate) variables: Vec<Ident>,
}

/// Container for request cookies data.
///
/// Used to store parsed cookie key-variable pairs from macro input.
/// Supports both single and multiple pairs.
pub(crate) struct MultiCookieData {
    /// Vector of cookie key-variable pairs.
    pub(crate) params: Vec<(Expr, Ident)>,
}

/// Container for request cookies collection data.
///
/// Used to store parsed cookies variables from macro input.
/// Supports both single and multiple variables.
pub(crate) struct MultiCookiesData {
    /// Vector of cookies variables.
    pub(crate) variables: Vec<Ident>,
}

/// Container for request version data.
///
/// Used to store parsed request version variables from macro input.
/// Supports both single and multiple variables.
pub(crate) struct MultiRequestVersionData {
    /// Vector of request version variables.
    pub(crate) variables: Vec<Ident>,
}

/// Container for request path data.
///
/// Used to store parsed request path variables from macro input.
/// Supports both single and multiple variables.
pub(crate) struct MultiRequestPathData {
    /// Vector of request path variables.
    pub(crate) variables: Vec<Ident>,
}

```

# Path: hyperlane-macros\src\request_middleware\fn.rs

```rust
use crate::*;

/// Registers a request middleware.
///
/// This macro takes a struct as input and registers it as a request middleware.
/// The registered struct will be used to create handlers that are called before the main request handler.
///
/// # Arguments
///
/// - `TokenStream` - The attribute `TokenStream`, which can optionally specify an `order`.
/// - `TokenStream` - The input token stream representing the struct to be registered as a middleware.
///
/// # Note
///
/// If an order parameter is not specified, the hook will have a higher priority than hooks with a specified order.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with the middleware registration.
pub(crate) fn request_middleware_macro(attr: TokenStream, item: TokenStream) -> TokenStream {
    let attr_args: OrderAttr = parse_macro_input!(attr as OrderAttr);
    let order: TokenStream2 = expr_to_isize(&attr_args.order);
    let input_struct: ItemStruct = parse_macro_input!(item as ItemStruct);
    let struct_name: &Ident = &input_struct.ident;
    let gen_code: TokenStream2 = quote! {
        #input_struct
        ::hyperlane::inventory::submit! {
            ::hyperlane::HookMacro {
                hook_type: ::hyperlane::HookType::RequestMiddleware(#order),
                handler: ::hyperlane::HookHandlerSpec::Factory(|| ::hyperlane::server_hook_factory::<#struct_name>()),
            }
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

# Path: hyperlane-macros\src\request_middleware\mod.rs

```rust
pub(crate) mod r#fn;

pub(crate) use r#fn::*;

```

# Path: hyperlane-macros\src\response\enum.rs

```rust
/// Defines operations that can be performed on response headers.
pub(crate) enum HeaderOperation {
    /// Sets an existing header value, replacing it if it already exists.
    Set,
    /// Adds a new header value, keeping any existing values with the same key.
    Add,
}

```

# Path: hyperlane-macros\src\response\fn.rs

```rust
use crate::*;

/// Sets response status code from macro input.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with status code setting.
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

/// Sets response reason phrase from macro input.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with reason phrase setting.
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

/// Sets or replaces response header from macro input.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with header operation.
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

/// Sets response body from macro input.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with body setting.
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

/// Clears all response headers from macro input.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with header operation.
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

/// Sets response version from macro input.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with version setting.
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

# Path: hyperlane-macros\src\response\impl.rs

```rust
use crate::*;

/// Implementation of Parse trait for ResponseHeaderData.
///
/// Parses header key, operation and value from input stream.
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

/// Implementation of Parse trait for ResponseBodyData.
///
/// Parses response body expression from input stream.
impl Parse for ResponseBodyData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let body: Expr = input.parse()?;
        Ok(ResponseBodyData { body })
    }
}

```

# Path: hyperlane-macros\src\response\mod.rs

```rust
mod r#enum;
mod r#fn;
mod r#impl;
mod r#struct;

pub(crate) use r#enum::*;
pub(crate) use r#fn::*;
pub(crate) use r#struct::*;

```

# Path: hyperlane-macros\src\response\struct.rs

```rust
use crate::*;

/// Represents data for a send operation.
///
/// This struct holds the data to send.
pub(crate) struct SendData {
    /// The data to send.
    pub(crate) data: Expr,
}

```

# Path: hyperlane-macros\src\response_middleware\fn.rs

```rust
use crate::*;

/// Registers a response middleware.
///
/// This macro takes a struct as input and registers it as a response middleware.
/// The registered struct will be used to create handlers that are called after the main request handler but before the response is sent.
///
/// # Arguments
///
/// - `TokenStream` - The attribute `TokenStream`, which can optionally specify an `order`.
/// - `TokenStream` - The input token stream representing the struct to be registered as a middleware.
///
/// # Note
///
/// If an order parameter is not specified, the hook will have a higher priority than hooks with a specified order.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with the middleware registration.
pub(crate) fn response_middleware_macro(attr: TokenStream, item: TokenStream) -> TokenStream {
    let attr_args: OrderAttr = parse_macro_input!(attr as OrderAttr);
    let order: TokenStream2 = expr_to_isize(&attr_args.order);
    let input_struct: ItemStruct = parse_macro_input!(item as ItemStruct);
    let struct_name: &Ident = &input_struct.ident;
    let gen_code: TokenStream2 = quote! {
        #input_struct
        ::hyperlane::inventory::submit! {
            ::hyperlane::HookMacro {
                hook_type: ::hyperlane::HookType::ResponseMiddleware(#order),
                handler: ::hyperlane::HookHandlerSpec::Factory(|| ::hyperlane::server_hook_factory::<#struct_name>()),
            }
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

# Path: hyperlane-macros\src\response_middleware\mod.rs

```rust
pub(crate) mod r#fn;

pub(crate) use r#fn::*;

```

# Path: hyperlane-macros\src\route\fn.rs

```rust
use crate::*;

/// Internal implementation for the `route` attribute macro.
///
/// This function processes the route attribute and generates code to register
/// the decorated struct as a route handler in the inventory system.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream containing route parameters (path)
/// - `TokenStream` - The struct token stream being decorated
///
/// # Returns
///
/// A `TokenStream` containing the original struct and inventory registration code
///
/// # Generated Code
///
/// The macro generates:
/// - The original struct unchanged
/// - An `inventory::submit!` block that registers a `HookMacro` instance
/// - A handler factory that creates boxed handlers for the struct
pub(crate) fn route_macro(attr: TokenStream, item: TokenStream) -> TokenStream {
    let route_attr: RouteAttr = parse_macro_input!(attr as RouteAttr);
    let path: &Expr = &route_attr.path;
    let input_struct: ItemStruct = parse_macro_input!(item as ItemStruct);
    let struct_name: &Ident = &input_struct.ident;
    let gen_code: TokenStream2 = quote! {
        #input_struct
        ::hyperlane::inventory::submit! {
            ::hyperlane::HookMacro {
                hook_type: ::hyperlane::HookType::Route(#path),
                handler: ::hyperlane::HookHandlerSpec::Factory(|| ::hyperlane::server_hook_factory::<#struct_name>()),
            }
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

# Path: hyperlane-macros\src\route\impl.rs

```rust
use crate::*;

/// Implements the `Parse` trait for `RouteAttr`.
///
/// This implementation defines how to parse a `TokenStream` into a `RouteAttr` struct,
/// extracting the path expression from the input.
impl Parse for RouteAttr {
    fn parse(input: ParseStream) -> Result<Self> {
        let first_expr: Expr = input.parse()?;
        Ok(RouteAttr { path: first_expr })
    }
}

```

# Path: hyperlane-macros\src\route\mod.rs

```rust
pub(crate) mod r#fn;
pub(crate) mod r#impl;
pub(crate) mod r#struct;

pub(crate) use r#fn::*;
pub(crate) use r#struct::*;

```

# Path: hyperlane-macros\src\route\struct.rs

```rust
use crate::*;

/// Represents the attributes for the `route` macro.
///
/// This struct parses the input attributes for the `route` macro,
/// specifically extracting the path for the route.
pub(crate) struct RouteAttr {
    /// The path expression for the route.
    pub(crate) path: Expr,
}

```

# Path: hyperlane-macros\src\send\fn.rs

```rust
use crate::*;

/// Sends the response with both headers and body.
///
/// # Arguments
///
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with send operation.
pub(crate) fn send_macro(item: TokenStream, position: Position) -> TokenStream {
    inject(position, item, |context| {
        quote! {
            let _ = #context.send().await;
        }
    })
}

inventory::submit! {
    InjectableMacro {
        name: "send",
        handler: Handler::NoAttrPosition(send_macro),
    }
}

/// Sends only the response body.
///
/// # Arguments
///
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with body send operation.
pub(crate) fn send_body_macro(item: TokenStream, position: Position) -> TokenStream {
    inject(position, item, |context| {
        quote! {
            let _ = #context.send_body().await;
        }
    })
}

inventory::submit! {
    InjectableMacro {
        name: "send_body",
        handler: Handler::NoAttrPosition(send_body_macro),
    }
}

/// Sends only the response body with specified data.
///
/// # Arguments
///
/// - `attr` - The attribute token stream containing the data to send.
/// - `item` - The input token stream to process.
/// - `position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with body send operation.
pub(crate) fn send_body_with_data_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let send_data: SendData = parse_macro_input!(attr as SendData);
    let data: Expr = send_data.data;
    inject(position, item, |context| {
        quote! {
            let _ = #context.send_body_with_data(#data).await;
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

# Path: hyperlane-macros\src\send\impl.rs

```rust
use crate::*;

/// Implementation of Parse trait for SendData.
///     
/// Parses data to send from input stream.
impl Parse for SendData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let data: Expr = input.parse()?;
        Ok(SendData { data })
    }
}

```

# Path: hyperlane-macros\src\send\mod.rs

```rust
mod r#fn;
mod r#impl;
mod r#struct;

pub(crate) use r#fn::*;
pub(crate) use r#struct::*;

```

# Path: hyperlane-macros\src\send\struct.rs

```rust
use crate::*;

/// Represents data for a response header.
///
/// This struct holds the key, value, and operation for a response header.
pub(crate) struct ResponseHeaderData {
    /// The header key.
    pub(crate) key: Expr,
    /// The header value.
    pub(crate) value: Expr,
    /// The operation to perform on the header (add or set).
    pub(crate) operation: HeaderOperation,
}

/// Represents data for a response body.
///
/// This struct holds the expression for the response body.
pub(crate) struct ResponseBodyData {
    /// The response body expression.
    pub(crate) body: Expr,
}

```

# Path: hyperlane-macros\src\stream\fn.rs

```rust
use crate::*;
use syn::Ident;

/// Generates stream processing loop based on context and data.
///
/// This function abstracts the common logic between HTTP and WebSocket stream macros.
/// It creates a token stream that wraps function body with a loop that reads from
/// a specified stream method.
///
/// # Arguments
///
/// - `&Ident` - The context identifier to use for stream access
/// - `&str` - The stream method to call (e.g., "http_from_stream" or "ws_from_stream")
/// - `&FromStreamData` - The FromStreamData containing request config and variable name
/// - `&[Stmt]` - The statements to execute when data is successfully read
///
/// # Returns
///
/// - `TokenStream2` - The generated loop code as a token stream
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

/// Wraps function body with HTTP stream processing.
///
/// This macro generates code that wraps the function body with a check to see if
/// data can be read from an HTTP stream. The function body is only executed
/// if data is successfully read from the stream.
///
/// # Arguments
///
/// - `TokenStream` - The attribute containing the request config and variable name.
/// - `TokenStream` - The input token stream to process.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with HTTP stream processing.
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

/// Wraps function body with WebSocket stream processing.
///
/// This macro generates code that wraps the function body with a check to see if
/// data can be read from a WebSocket stream. The function body is only executed
/// if data is successfully read from the stream.
///
/// # Arguments
///
/// - `attr` - The attribute containing the request config and variable name.
/// - `item` - The input token stream to process.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with WebSocket stream processing.
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

# Path: hyperlane-macros\src\stream\mod.rs

```rust
mod r#fn;

pub(crate) use r#fn::*;

```

# Path: hyperlane-plugin-websocket\README.md


## hyperlane-plugin-websocket

[Official Documentation](https://docs.ltpp.vip/hyperlane-plugin-websocket/)

[Api Docs](https://docs.rs/hyperlane-plugin-websocket/latest/http_type/)

> A WebSocket plugin for the Hyperlane framework, providing robust WebSocket communication capabilities and integrating with hyperlane-broadcast for efficient message dissemination.

## Installation

To use this crate, you can run cmd:

```shell
cargo add hyperlane-plugin-websocket
```

## Use

```rust
use hyperlane::*;
use hyperlane_plugin_websocket::*;

struct RequestMiddleware {
    socket_addr: String,
}
struct UpgradeHook;
struct ServerPanicHook {
    response_body: String,
    content_type: String,
}
struct GroupChat;
struct PrivateChat {
    config: WebSocketConfig<String>,
}
struct ConnectedHook {
    receiver_count: ReceiverCount,
    data: String,
    group_broadcast_type: BroadcastType<String>,
    private_broadcast_type: BroadcastType<String>,
}
struct PrivateClosedHook {
    body: String,
    receiver_count: ReceiverCount,
}
struct SendedHook {
    msg: String,
}
struct GroupChatRequestHook {
    body: RequestBody,
    receiver_count: ReceiverCount,
}
struct GroupClosedHook {
    body: String,
    receiver_count: ReceiverCount,
}
struct PrivateChatRequestHook {
    body: RequestBody,
    receiver_count: ReceiverCount,
}

static BROADCAST_MAP: OnceLock<WebSocket> = OnceLock::new();

fn get_broadcast_map() -> &'static WebSocket {
    BROADCAST_MAP.get_or_init(WebSocket::new)
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
                .await
                .unwrap();
        }
    }
}

impl ServerHook for ConnectedHook {
    async fn new(ctx: &Context) -> Self {
        let group_name: String = ctx
            .try_get_route_param("group_name")
            .await
            .unwrap_or_default();
        let group_broadcast_type: BroadcastType<String> =
            BroadcastType::PointToGroup(group_name);
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
        let _ = std::io::Write::flush(&mut std::io::stdout());
    }
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
        let _ = std::io::Write::flush(&mut std::io::stdout());
    }
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
        let _ = std::io::Write::flush(&mut std::io::stdout());
    }
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
        let _ = std::io::Write::flush(&mut std::io::stdout());
    }
}

impl ServerHook for PrivateClosedHook {
    async fn new(ctx: &Context) -> Self {
        let my_name: String = ctx.try_get_route_param("my_name").await.unwrap();
        let your_name: String = ctx.try_get_route_param("your_name").await.unwrap();
        let key: BroadcastType<String> = BroadcastType::PointToPoint(my_name, your_name);
        let receiver_count: ReceiverCount =
            get_broadcast_map().receiver_count_after_closed(key);
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
        let _ = std::io::Write::flush(&mut std::io::stdout());
    }
}

impl ServerHook for SendedHook {
    async fn new(ctx: &Context) -> Self {
        let msg: String = ctx.get_response_body_string().await;
        Self { msg }
    }

    async fn handle(self, _ctx: &Context) {
        println!("[sended_hook]msg => {}", self.msg);
        let _ = std::io::Write::flush(&mut std::io::stdout());
    }
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

impl ServerHook for ServerPanicHook {
    async fn new(ctx: &Context) -> Self {
        let error: Panic = ctx.try_get_panic().await.unwrap_or_default();
        let response_body: String = error.to_string();
        let content_type: String =
            ContentType::format_content_type_with_charset(TEXT_PLAIN, UTF8);
        Self {
            response_body,
            content_type,
        }
    }

    async fn handle(self, ctx: &Context) {
        let _ = ctx
            .set_response_version(HttpVersion::Http1_1)
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

async fn main() {
    let server: Server = Server::new().await;
    let config: ServerConfig = ServerConfig::new().await;
    config.host("0.0.0.0").await;
    config.port(60000).await;
    config.request_config(RequestConfig::default()).await;
    config.disable_linger().await;
    config.disable_nodelay().await;
    server.config(config).await;
    server.request_middleware::<RequestMiddleware>().await;
    server.request_middleware::<UpgradeHook>().await;
    server.route::<GroupChat>("/{group_name}").await;
    server.route::<PrivateChat>("/{my_name}/{your_name}").await;
    let server_control_hook: ServerControlHook = server.run().await.unwrap_or_default();
    server_control_hook.wait().await;
}
```

## Contact


# Path: hyperlane-plugin-websocket\src\lib.rs

```rust
//! A WebSocket plugin for the Hyperlane framework.
//!
//! A WebSocket plugin for the Hyperlane framework,
//! providing robust WebSocket communication capabilities and integrating
//! with hyperlane-broadcast for efficient message dissemination.

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

# Path: hyperlane-plugin-websocket\src\tests\cfg.rs

```rust
use crate::*;

#[tokio::test]
async fn test_server() {
    struct RequestMiddleware {
        socket_addr: String,
    }
    struct UpgradeHook;
    struct ServerPanicHook {
        response_body: String,
        content_type: String,
    }
    struct GroupChat;
    struct PrivateChat {
        config: WebSocketConfig<String>,
    }
    struct ConnectedHook {
        receiver_count: ReceiverCount,
        data: String,
        group_broadcast_type: BroadcastType<String>,
        private_broadcast_type: BroadcastType<String>,
    }
    struct PrivateClosedHook {
        body: String,
        receiver_count: ReceiverCount,
    }
    struct SendedHook {
        msg: String,
    }
    struct GroupChatRequestHook {
        body: RequestBody,
        receiver_count: ReceiverCount,
    }
    struct GroupClosedHook {
        body: String,
        receiver_count: ReceiverCount,
    }
    struct PrivateChatRequestHook {
        body: RequestBody,
        receiver_count: ReceiverCount,
    }

    static BROADCAST_MAP: OnceLock<WebSocket> = OnceLock::new();

    fn get_broadcast_map() -> &'static WebSocket {
        BROADCAST_MAP.get_or_init(WebSocket::new)
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
                    .await
                    .unwrap();
            }
        }
    }

    impl ServerHook for ConnectedHook {
        async fn new(ctx: &Context) -> Self {
            let group_name: String = ctx
                .try_get_route_param("group_name")
                .await
                .unwrap_or_default();
            let group_broadcast_type: BroadcastType<String> =
                BroadcastType::PointToGroup(group_name);
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
            let _ = std::io::Write::flush(&mut std::io::stdout());
        }
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
            let _ = std::io::Write::flush(&mut std::io::stdout());
        }
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
            let _ = std::io::Write::flush(&mut std::io::stdout());
        }
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
            let _ = std::io::Write::flush(&mut std::io::stdout());
        }
    }

    impl ServerHook for PrivateClosedHook {
        async fn new(ctx: &Context) -> Self {
            let my_name: String = ctx.try_get_route_param("my_name").await.unwrap();
            let your_name: String = ctx.try_get_route_param("your_name").await.unwrap();
            let key: BroadcastType<String> = BroadcastType::PointToPoint(my_name, your_name);
            let receiver_count: ReceiverCount =
                get_broadcast_map().receiver_count_after_closed(key);
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
            let _ = std::io::Write::flush(&mut std::io::stdout());
        }
    }

    impl ServerHook for SendedHook {
        async fn new(ctx: &Context) -> Self {
            let msg: String = ctx.get_response_body_string().await;
            Self { msg }
        }

        async fn handle(self, _ctx: &Context) {
            println!("[sended_hook]msg => {}", self.msg);
            let _ = std::io::Write::flush(&mut std::io::stdout());
        }
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

    impl ServerHook for ServerPanicHook {
        async fn new(ctx: &Context) -> Self {
            let error: Panic = ctx.try_get_panic().await.unwrap_or_default();
            let response_body: String = error.to_string();
            let content_type: String =
                ContentType::format_content_type_with_charset(TEXT_PLAIN, UTF8);
            Self {
                response_body,
                content_type,
            }
        }

        async fn handle(self, ctx: &Context) {
            let _ = ctx
                .set_response_version(HttpVersion::Http1_1)
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

    async fn main() {
        let server: Server = Server::new().await;
        let config: ServerConfig = ServerConfig::new().await;
        config.host("0.0.0.0").await;
        config.port(60000).await;
        config.request_config(RequestConfig::default()).await;
        config.disable_linger().await;
        config.disable_nodelay().await;
        server.config(config).await;
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

    main().await;
}

```

# Path: hyperlane-plugin-websocket\src\tests\mod.rs

```rust
mod cfg;

```

# Path: hyperlane-plugin-websocket\src\websocket\const.rs

```rust
/// Represents the prefix for point-to-point broadcast keys.
///
/// This constant is used to construct unique keys for point-to-point WebSocket broadcasts.
pub(crate) const POINT_TO_POINT_KEY: &str = "ptp-";

/// Represents the prefix for point-to-group broadcast keys.
///
/// This constant is used to construct unique keys for point-to-group WebSocket broadcasts.
pub(crate) const POINT_TO_GROUP_KEY: &str = "ptg-";

```

# Path: hyperlane-plugin-websocket\src\websocket\enum.rs

```rust
use crate::*;

/// Represents the type of broadcast for WebSocket messages.
///
/// This enum allows specifying whether a message is intended for a direct
/// point-to-point communication between two entities or for a group of entities.
///
/// # Type Parameters
///
/// - `T`: The type used to identify points or groups, which must implement `BroadcastTypeTrait`.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum BroadcastType<T: BroadcastTypeTrait> {
    /// Indicates a point-to-point broadcast between two specific entities.
    ///
    /// The tuple contains the identifiers of the two entities involved in the communication.
    PointToPoint(T, T),
    /// Indicates a broadcast to a specific group of entities.
    ///
    /// The tuple contains the identifier of the group.
    PointToGroup(T),
    /// Represents an unknown or unhandled broadcast type.
    ///
    /// This variant is used as a default or fallback for unhandled cases.
    Unknown,
}

```

# Path: hyperlane-plugin-websocket\src\websocket\impl.rs

```rust
use crate::*;

/// Allows `String` to be used as a broadcast identifier.
impl BroadcastTypeTrait for String {}

/// Allows string slices to be used as broadcast identifiers.
impl BroadcastTypeTrait for &str {}

/// Allows `char` to be used as a broadcast identifier.
impl BroadcastTypeTrait for char {}

/// Allows `bool` to be used as a broadcast identifier.
impl BroadcastTypeTrait for bool {}

/// Allows `i8` to be used as a broadcast identifier.
impl BroadcastTypeTrait for i8 {}

/// Allows `i16` to be used as a broadcast identifier.
impl BroadcastTypeTrait for i16 {}

/// Allows `i32` to be used as a broadcast identifier.
impl BroadcastTypeTrait for i32 {}

/// Allows `i64` to be used as a broadcast identifier.
impl BroadcastTypeTrait for i64 {}

/// Allows `i128` to be used as a broadcast identifier.
impl BroadcastTypeTrait for i128 {}

/// Allows `isize` to be used as a broadcast identifier.
impl BroadcastTypeTrait for isize {}

/// Allows `u8` to be used as a broadcast identifier.
impl BroadcastTypeTrait for u8 {}

/// Allows `u16` to be used as a broadcast identifier.
impl BroadcastTypeTrait for u16 {}

/// Allows `u32` to be used as a broadcast identifier.
impl BroadcastTypeTrait for u32 {}

/// Allows `u64` to be used as a broadcast identifier.
impl BroadcastTypeTrait for u64 {}

/// Allows `u128` to be used as a broadcast identifier.
impl BroadcastTypeTrait for u128 {}

/// Allows `usize` to be used as a broadcast identifier.
impl BroadcastTypeTrait for usize {}

/// Allows `f32` to be used as a broadcast identifier.
impl BroadcastTypeTrait for f32 {}

/// Allows `f64` to be used as a broadcast identifier.
impl BroadcastTypeTrait for f64 {}

/// Allows `IpAddr` to be used as a broadcast identifier.
impl BroadcastTypeTrait for IpAddr {}

/// Allows `Ipv4Addr` to be used as a broadcast identifier.
impl BroadcastTypeTrait for Ipv4Addr {}

/// Allows `Ipv6Addr` to be used as a broadcast identifier.
impl BroadcastTypeTrait for Ipv6Addr {}

/// Allows `SocketAddr` to be used as a broadcast identifier.
impl BroadcastTypeTrait for SocketAddr {}

/// Allows `NonZeroU8` to be used as a broadcast identifier.
impl BroadcastTypeTrait for NonZeroU8 {}

/// Allows `NonZeroU16` to be used as a broadcast identifier.
impl BroadcastTypeTrait for NonZeroU16 {}

/// Allows `NonZeroU32` to be used as a broadcast identifier.
impl BroadcastTypeTrait for NonZeroU32 {}

/// Allows `NonZeroU64` to be used as a broadcast identifier.
impl BroadcastTypeTrait for NonZeroU64 {}

/// Allows `NonZeroU128` to be used as a broadcast identifier.
impl BroadcastTypeTrait for NonZeroU128 {}

/// Allows `NonZeroUsize` to be used as a broadcast identifier.
impl BroadcastTypeTrait for NonZeroUsize {}

/// Allows `NonZeroI8` to be used as a broadcast identifier.
impl BroadcastTypeTrait for NonZeroI8 {}

/// Allows `NonZeroI16` to be used as a broadcast identifier.
impl BroadcastTypeTrait for NonZeroI16 {}

/// Allows `NonZeroI32` to be used as a broadcast identifier.
impl BroadcastTypeTrait for NonZeroI32 {}

/// Allows `NonZeroI64` to be used as a broadcast identifier.
impl BroadcastTypeTrait for NonZeroI64 {}

/// Allows `NonZeroI128` to be used as a broadcast identifier.
impl BroadcastTypeTrait for NonZeroI128 {}

/// Allows `NonZeroIsize` to be used as a broadcast identifier.
impl BroadcastTypeTrait for NonZeroIsize {}

/// Allows `Infallible` to be used as a broadcast identifier.
impl BroadcastTypeTrait for Infallible {}

/// Allows references to `String` to be used as broadcast identifiers.
impl BroadcastTypeTrait for &String {}

/// Allows double references to string slices to be used as broadcast identifiers.
impl BroadcastTypeTrait for &&str {}

/// Allows references to `char` to be used as broadcast identifiers.
impl BroadcastTypeTrait for &char {}

/// Allows references to `bool` to be used as broadcast identifiers.
impl BroadcastTypeTrait for &bool {}

/// Allows references to `i8` to be used as broadcast identifiers.
impl BroadcastTypeTrait for &i8 {}

/// Allows references to `i16` to be used as broadcast identifiers.
impl BroadcastTypeTrait for &i16 {}

/// Allows references to `i32` to be used as broadcast identifiers.
impl BroadcastTypeTrait for &i32 {}

/// Allows references to `i64` to be used as broadcast identifiers.
impl BroadcastTypeTrait for &i64 {}

/// Allows references to `i128` to be used as broadcast identifiers.
impl BroadcastTypeTrait for &i128 {}

/// Allows references to `isize` to be used as broadcast identifiers.
impl BroadcastTypeTrait for &isize {}

/// Allows references to `u8` to be used as broadcast identifiers.
impl BroadcastTypeTrait for &u8 {}

/// Allows references to `u16` to be used as broadcast identifiers.
impl BroadcastTypeTrait for &u16 {}

/// Allows references to `u32` to be used as broadcast identifiers.
impl BroadcastTypeTrait for &u32 {}

/// Allows references to `u64` to be used as
/// Implements `BroadcastTypeTrait` for `&u128`.
///
/// This allows references to `u128` to be used as a broadcast identifier.
impl BroadcastTypeTrait for &u128 {}

/// Implements `BroadcastTypeTrait` for `&usize`.
///
/// This allows references to `usize` to be used as a broadcast identifier.
impl BroadcastTypeTrait for &usize {}

/// Implements `BroadcastTypeTrait` for `&f32`.
///
/// This allows references to `f32` to be used as a broadcast identifier.
impl BroadcastTypeTrait for &f32 {}

/// Implements `BroadcastTypeTrait` for `&f64`.
///
/// This allows references to `f64` to be used as a broadcast identifier.
impl BroadcastTypeTrait for &f64 {}

/// Implements `BroadcastTypeTrait` for `&IpAddr`.
///
/// This allows references to `IpAddr` to be used as a broadcast identifier.
impl BroadcastTypeTrait for &IpAddr {}

/// Implements `BroadcastTypeTrait` for `&Ipv4Addr`.
///
/// This allows references to `Ipv4Addr` to be used as a broadcast identifier.
impl BroadcastTypeTrait for &Ipv4Addr {}

/// Implements `BroadcastTypeTrait` for `&Ipv6Addr`.
///
/// This allows references to `Ipv6Addr` to be used as a broadcast identifier.
impl BroadcastTypeTrait for &Ipv6Addr {}

/// Implements `BroadcastTypeTrait` for `&SocketAddr`.
///
/// This allows references to `SocketAddr` to be used as a broadcast identifier.
impl BroadcastTypeTrait for &SocketAddr {}

/// Implements `BroadcastTypeTrait` for `&NonZeroU8`.
///
/// This allows references to `NonZeroU8` to be used as a broadcast identifier.
impl BroadcastTypeTrait for &NonZeroU8 {}

/// Implements `BroadcastTypeTrait` for `&NonZeroU16`.
///
/// This allows references to `NonZeroU16` to be used as a broadcast identifier.
impl BroadcastTypeTrait for &NonZeroU16 {}

/// Implements `BroadcastTypeTrait` for `&NonZeroU32`.
///
/// This allows references to `NonZeroU32` to be used as a broadcast identifier.
impl BroadcastTypeTrait for &NonZeroU32 {}

/// Implements `BroadcastTypeTrait` for `&NonZeroU64`.
///
/// This allows references to `NonZeroU64` to be used as a broadcast identifier.
impl BroadcastTypeTrait for &NonZeroU64 {}

/// Implements `BroadcastTypeTrait` for `&NonZeroU128`.
///
/// This allows references to `NonZeroU128` to be used as a broadcast identifier.
impl BroadcastTypeTrait for &NonZeroU128 {}

/// Implements `BroadcastTypeTrait` for `&NonZeroUsize`.
///
/// This allows references to `NonZeroUsize` to be used as a broadcast identifier.
impl BroadcastTypeTrait for &NonZeroUsize {}

/// Implements `BroadcastTypeTrait` for `&NonZeroI8`.
///
/// This allows references to `NonZeroI8` to be used as a broadcast identifier.
impl BroadcastTypeTrait for &NonZeroI8 {}

/// Implements `BroadcastTypeTrait` for `&NonZeroI16`.
///
/// This allows references to `NonZeroI16` to be used as a broadcast identifier.
impl BroadcastTypeTrait for &NonZeroI16 {}

/// Implements `BroadcastTypeTrait` for `&NonZeroI32`.
///
/// This allows references to `NonZeroI32` to be used as a broadcast identifier.
impl BroadcastTypeTrait for &NonZeroI32 {}

/// Implements `BroadcastTypeTrait` for `&NonZeroI64`.
///
/// This allows references to `NonZeroI64` to be used as a broadcast identifier.
impl BroadcastTypeTrait for &NonZeroI64 {}

/// Implements `BroadcastTypeTrait` for `&NonZeroI128`.
///
/// This allows references to `NonZeroI128` to be used as a broadcast identifier.
impl BroadcastTypeTrait for &NonZeroI128 {}

/// Implements `BroadcastTypeTrait` for `&NonZeroIsize`.
///
/// This allows references to `NonZeroIsize` to be used as a broadcast identifier.
impl BroadcastTypeTrait for &NonZeroIsize {}

/// Implements `BroadcastTypeTrait` for `&Infallible`.
///
/// This allows references to `Infallible` to be used as a broadcast identifier.
impl BroadcastTypeTrait for &Infallible {}

/// Implements the `Default` trait for `BroadcastType`.
///
/// The default value is `BroadcastType::Unknown`.
///
/// # Type Parameters
///
/// - `B`: The type parameter for `BroadcastType`, which must implement `BroadcastTypeTrait`.
impl<B: BroadcastTypeTrait> Default for BroadcastType<B> {
    #[inline(always)]
    fn default() -> Self {
        BroadcastType::Unknown
    }
}

impl<B: BroadcastTypeTrait> BroadcastType<B> {
    /// Generates a unique key string for a given broadcast type.
    ///
    /// For point-to-point types, the keys are sorted to ensure consistent key generation
    /// regardless of the order of the input keys.
    ///
    /// # Arguments
    ///
    /// - `BroadcastType<B>` - The broadcast type for which to generate the key.
    ///
    /// # Returns
    ///
    /// - `String` - The unique key string for the broadcast type.
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

/// Implements the `Default` trait for `WebSocketConfig`.
///
/// Provides a default configuration for WebSocket connections, including
/// default hook types that do nothing.
///
/// # Type Parameters
///
/// - `B`: The type parameter for `WebSocketConfig`, which must implement `BroadcastTypeTrait`.
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
    /// Creates a new WebSocket configuration with default values.
    ///
    /// # Returns
    ///
    /// - `WebSocketConfig<B>` - A new WebSocket configuration instance.
    #[inline(always)]
    pub fn new() -> Self {
        Self::default()
    }
}

impl<B: BroadcastTypeTrait> WebSocketConfig<B> {
    /// Sets the request configuration for the WebSocket connection.
    ///
    /// # Arguments
    ///
    /// - `RequestConfig` - The request configuration to use for this WebSocket.
    ///
    /// # Returns
    ///
    /// - `WebSocketConfig<B>` - The modified WebSocket configuration instance.
    #[inline(always)]
    pub fn set_request_config(mut self, request_config: RequestConfig) -> Self {
        self.request_config = request_config;
        self
    }

    /// Sets the capacity for the broadcast sender.
    ///
    /// # Arguments
    ///
    /// - `Capacity` - The desired capacity.
    ///
    /// # Returns
    ///
    /// - `WebSocketConfig<B>` - The modified WebSocket configuration instance.
    #[inline(always)]
    pub fn set_capacity(mut self, capacity: Capacity) -> Self {
        self.capacity = capacity;
        self
    }

    /// Sets the context for the WebSocket connection.
    ///
    /// # Arguments
    ///
    /// - `Context` - The context object to associate with the WebSocket.
    ///
    /// # Returns
    ///
    /// - `WebSocketConfig<B>` - The modified WebSocket configuration instance.
    #[inline(always)]
    pub fn set_context(mut self, context: Context) -> Self {
        self.context = context;
        self
    }

    /// Sets the broadcast type for the WebSocket connection.
    ///
    /// # Arguments
    ///
    /// - `BroadcastType<B>` - The broadcast type to use for this WebSocket.
    ///
    /// # Returns
    ///
    /// - `WebSocketConfig<B>` - The modified WebSocket configuration instance.
    #[inline(always)]
    pub fn set_broadcast_type(mut self, broadcast_type: BroadcastType<B>) -> Self {
        self.broadcast_type = broadcast_type;
        self
    }

    /// Retrieves a reference to the context associated with this configuration.
    ///
    /// # Returns
    ///
    /// - `&Context` - A reference to the context object.
    #[inline(always)]
    pub fn get_context(&self) -> &Context {
        &self.context
    }

    /// Retrieves the request configuration for this WebSocket.
    ///
    /// # Returns
    ///
    /// - `RequestConfig` - The request configuration object.
    #[inline(always)]
    pub fn get_request_config(&self) -> RequestConfig {
        self.request_config
    }

    /// Retrieves the capacity configured for the broadcast sender.
    ///
    /// # Returns
    ///
    /// - `Capacity` - The capacity.
    #[inline(always)]
    pub fn get_capacity(&self) -> Capacity {
        self.capacity
    }

    /// Retrieves a reference to the broadcast type configured for this WebSocket.
    ///
    /// # Returns
    ///
    /// - `&BroadcastType<B>` - A reference to the broadcast type object.
    #[inline(always)]
    pub fn get_broadcast_type(&self) -> &BroadcastType<B> {
        &self.broadcast_type
    }

    /// Sets the connected hook handler.
    ///
    /// This hook is executed when the WebSocket connection is established.
    ///
    /// # Type Parameters
    ///
    /// - `S`: The hook type, which must implement `ServerHook`.
    ///
    /// # Returns
    ///
    /// The modified `WebSocketConfig` instance.
    ///
    /// # Examples
    ///
    /// ```rust,ignore
    /// struct MyConnectedHook;
    /// impl ServerHook for MyConnectedHook {
    ///     async fn new(_ctx: &Context) -> Self { Self }
    ///     async fn handle(self, ctx: &Context) { /* ... */ }
    /// }
    ///
    /// let config = WebSocketConfig::new()
    ///     .set_connected_hook::<MyConnectedHook>();
    /// ```
    #[inline(always)]
    pub fn set_connected_hook<S>(mut self) -> Self
    where
        S: ServerHook,
    {
        self.connected_hook = server_hook_factory::<S>();
        self
    }

    /// Sets the request hook handler.
    ///
    /// This hook is executed when a new request is received on the WebSocket.
    ///
    /// # Type Parameters
    ///
    /// - `S`: The hook type, which must implement `ServerHook`.
    ///
    /// # Returns
    ///
    /// The modified `WebSocketConfig` instance.
    ///
    /// # Examples
    ///
    /// ```rust,ignore
    /// struct MyRequestHook;
    /// impl ServerHook for MyRequestHook {
    ///     async fn new(_ctx: &Context) -> Self { Self }
    ///     async fn handle(self, ctx: &Context) { /* ... */ }
    /// }
    ///
    /// let config = WebSocketConfig::new()
    ///     .set_request_hook::<MyRequestHook>();
    /// ```
    #[inline(always)]
    pub fn set_request_hook<S>(mut self) -> Self
    where
        S: ServerHook,
    {
        self.request_hook = server_hook_factory::<S>();
        self
    }

    /// Sets the sended hook handler.
    ///
    /// This hook is executed after a message has been successfully sent over the WebSocket.
    ///
    /// # Type Parameters
    ///
    /// - `S`: The hook type, which must implement `ServerHook`.
    ///
    /// # Returns
    ///
    /// The modified `WebSocketConfig` instance.
    ///
    /// # Examples
    ///
    /// ```rust,ignore
    /// struct MySendedHook;
    /// impl ServerHook for MySendedHook {
    ///     async fn new(_ctx: &Context) -> Self { Self }
    ///     async fn handle(self, ctx: &Context) { /* ... */ }
    /// }
    ///
    /// let config = WebSocketConfig::new()
    ///     .set_sended_hook::<MySendedHook>();
    /// ```
    #[inline(always)]
    pub fn set_sended_hook<S>(mut self) -> Self
    where
        S: ServerHook,
    {
        self.sended_hook = server_hook_factory::<S>();
        self
    }

    /// Sets the closed hook handler.
    ///
    /// This hook is executed when the WebSocket connection is closed.
    ///
    /// # Type Parameters
    ///
    /// - `S`: The hook type, which must implement `ServerHook`.
    ///
    /// # Returns
    ///
    /// The modified `WebSocketConfig` instance.
    ///
    /// # Examples
    ///
    /// ```rust,ignore
    /// struct MyClosedHook;
    /// impl ServerHook for MyClosedHook {
    ///     async fn new(_ctx: &Context) -> Self { Self }
    ///     async fn handle(self, ctx: &Context) { /* ... */ }
    /// }
    ///
    /// let config = WebSocketConfig::new()
    ///     .set_closed_hook::<MyClosedHook>();
    /// ```
    #[inline(always)]
    pub fn set_closed_hook<S>(mut self) -> Self
    where
        S: ServerHook,
    {
        self.closed_hook = server_hook_factory::<S>();
        self
    }

    /// Retrieves a reference to the connected hook handler.
    ///
    /// # Returns
    ///
    /// - `&ServerHookHandler` - A reference to the connected hook handler.
    #[inline(always)]
    pub fn get_connected_hook(&self) -> &ServerHookHandler {
        &self.connected_hook
    }

    /// Retrieves a reference to the request hook handler.
    ///
    /// # Returns
    ///
    /// - `&ServerHookHandler` - A reference to the request hook handler.
    #[inline(always)]
    pub fn get_request_hook(&self) -> &ServerHookHandler {
        &self.request_hook
    }

    /// Retrieves a reference to the sended hook handler.
    ///
    /// # Returns
    ///
    /// - `&ServerHookHandler` - A reference to the sended hook handler.
    #[inline(always)]
    pub fn get_sended_hook(&self) -> &ServerHookHandler {
        &self.sended_hook
    }

    /// Retrieves a reference to the closed hook handler.
    ///
    /// # Returns
    ///
    /// - `&ServerHookHandler` - A reference to the closed hook handler.
    #[inline(always)]
    pub fn get_closed_hook(&self) -> &ServerHookHandler {
        &self.closed_hook
    }
}

impl WebSocket {
    /// Creates a new WebSocket instance.
    ///
    /// Initializes with a default broadcast map.
    ///
    /// # Returns
    ///
    /// - `WebSocket` - A new WebSocket instance.
    #[inline(always)]
    pub fn new() -> Self {
        Self::default()
    }

    /// Subscribes to a broadcast type or inserts a new one if it doesn't exist.
    ///
    /// # Type Parameters
    ///
    /// - `B`: The type implementing `BroadcastTypeTrait`.
    ///
    /// # Arguments
    ///
    /// - `BroadcastType<B>` - The broadcast type to subscribe to.
    /// - `Capacity` - The capacity for the broadcast sender if a new one is inserted.
    ///
    /// # Returns
    ///
    /// - `BroadcastMapReceiver<Vec<u8>>` - A broadcast map receiver for the specified broadcast type.
    #[inline(always)]
    fn subscribe_unwrap_or_insert<B: BroadcastTypeTrait>(
        &self,
        broadcast_type: BroadcastType<B>,
        capacity: Capacity,
    ) -> BroadcastMapReceiver<Vec<u8>> {
        let key: String = BroadcastType::get_key(broadcast_type);
        self.broadcast_map.subscribe_or_insert(&key, capacity)
    }

    /// Subscribes to a point-to-point broadcast.
    ///
    /// # Type Parameters
    ///
    /// - `B`: The type implementing `BroadcastTypeTrait`.
    ///
    /// # Arguments
    ///
    /// - `&B` - The first identifier for the point-to-point communication.
    /// - `&B` - The second identifier for the point-to-point communication.
    /// - `Capacity` - The capacity for the broadcast sender.
    ///
    /// # Returns
    ///
    /// - `BroadcastMapReceiver<Vec<u8>>` - A broadcast map receiver for the point-to-point broadcast.
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

    /// Subscribes to a point-to-group broadcast.
    ///
    /// # Type Parameters
    ///
    /// - `B`: The type implementing `BroadcastTypeTrait`.
    ///
    /// # Arguments
    ///
    /// - `&B` - The identifier for the group.
    /// - `Capacity` - The capacity for the broadcast sender.
    ///
    /// # Returns
    ///
    /// - `BroadcastMapReceiver<Vec<u8>>` - A broadcast map receiver for the point-to-group broadcast.
    #[inline(always)]
    fn point_to_group<B: BroadcastTypeTrait>(
        &self,
        key: &B,
        capacity: Capacity,
    ) -> BroadcastMapReceiver<Vec<u8>> {
        self.subscribe_unwrap_or_insert(BroadcastType::PointToGroup(key.clone()), capacity)
    }

    /// Retrieves the current receiver count for a given broadcast type.
    ///
    /// # Type Parameters
    ///
    /// - `B`: The type implementing `BroadcastTypeTrait`.
    ///
    /// # Arguments
    ///
    /// - `BroadcastType<B>` - The broadcast type for which to get the receiver count.
    ///
    /// # Returns
    ///
    /// - `ReceiverCount` - The number of active receivers for the broadcast type, or 0 if not found.
    #[inline(always)]
    pub fn receiver_count<B: BroadcastTypeTrait>(
        &self,
        broadcast_type: BroadcastType<B>,
    ) -> ReceiverCount {
        let key: String = BroadcastType::get_key(broadcast_type);
        self.broadcast_map.receiver_count(&key).unwrap_or(0)
    }

    /// Calculates the receiver count before a connection is established.
    ///
    /// Ensures the count does not exceed the maximum allowed value minus one.
    ///
    /// # Type Parameters
    ///
    /// - `B`: The type implementing `BroadcastTypeTrait`.
    ///
    /// # Arguments
    ///
    /// - `BroadcastType<B>` - The broadcast type for which to get the receiver count.
    ///
    /// # Returns
    ///
    /// - `ReceiverCount` - The receiver count after the connection is established.
    #[inline(always)]
    pub fn receiver_count_before_connected<B: BroadcastTypeTrait>(
        &self,
        broadcast_type: BroadcastType<B>,
    ) -> ReceiverCount {
        let count: ReceiverCount = self.receiver_count(broadcast_type);
        count.clamp(0, ReceiverCount::MAX - 1) + 1
    }

    /// Calculates the receiver count after a connection is closed.
    ///
    /// Ensures the count does not go below 0.
    ///
    /// # Type Parameters
    ///
    /// - `B`: The type implementing `BroadcastTypeTrait`.
    ///
    /// # Arguments
    ///
    /// - `BroadcastType<B>` - The broadcast type for which to get the receiver count.
    ///
    /// # Returns
    ///
    /// - `ReceiverCount` - The receiver count after the connection is closed.
    #[inline(always)]
    pub fn receiver_count_after_closed<B: BroadcastTypeTrait>(
        &self,
        broadcast_type: BroadcastType<B>,
    ) -> ReceiverCount {
        let count: ReceiverCount = self.receiver_count(broadcast_type);
        count.clamp(1, ReceiverCount::MAX) - 1
    }

    /// Sends data to all active receivers for a given broadcast type.
    ///
    /// # Type Parameters
    ///
    /// - `T`: The type of data to send, which must be convertible to `Vec<u8>`.
    /// - `B`: The type implementing `BroadcastTypeTrait`.
    ///
    /// # Arguments
    ///
    /// - `BroadcastType<B>` - The broadcast type to which to send the data.
    /// - `T` - The data to send.
    ///
    /// # Returns
    ///
    /// - `BroadcastMapSendResult<Vec<u8>>` - A result indicating the success or failure of the send operation.
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

    /// Runs the WebSocket connection, handling incoming requests and outgoing messages.
    ///
    /// This asynchronous function continuously monitors for new WebSocket requests
    /// and incoming broadcast messages, processing them according to the configured hooks.
    ///
    /// # Type Parameters
    ///
    /// - `B`: The type implementing `BroadcastTypeTrait`.
    ///
    /// # Arguments
    ///
    /// - `WebSocketConfig<B>` - The WebSocket configuration containing the configuration for this WebSocket instance.
    ///
    /// # Panics
    ///
    /// Panics if the context in the WebSocket configuration is not set (i.e., it's the default context).
    /// Panics if the broadcast type in the WebSocket configuration is `BroadcastType::Unknown`.
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
                        if ctx.send_body_list_with_data(&frame_list).await.is_ok() {
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

# Path: hyperlane-plugin-websocket\src\websocket\mod.rs

```rust
pub(crate) mod r#const;
pub(crate) mod r#enum;
pub(crate) mod r#impl;
pub(crate) mod r#struct;
pub(crate) mod r#trait;

```

# Path: hyperlane-plugin-websocket\src\websocket\struct.rs

```rust
use crate::*;

/// Represents a WebSocket instance.
///
/// This struct manages broadcast capabilities and holds the internal broadcast map
/// responsible for handling message distribution to various WebSocket connections.
#[derive(Debug, Clone, Default)]
pub struct WebSocket {
    /// The internal broadcast map.
    ///
    /// This map is used for managing WebSocket message distribution.
    pub(super) broadcast_map: BroadcastMap<Vec<u8>>,
}

/// Configuration for a WebSocket connection.
///
/// This struct encapsulates all necessary parameters for setting up and managing
/// a WebSocket connection, including context, buffer sizes, capacity, broadcast type,
/// and hook handlers for different lifecycle events.
///
/// # Type Parameters
///
/// - `B`: The type used for broadcast keys, which must implement `BroadcastTypeTrait`.
#[derive(Clone)]
pub struct WebSocketConfig<B: BroadcastTypeTrait> {
    /// The Hyperlane context.
    ///
    /// This context is associated with this WebSocket connection.
    pub(super) context: Context,
    /// The request config.
    ///
    /// This configuration is used for managing WebSocket request processing,
    /// including connection upgrade handling and request lifecycle management.
    pub(super) request_config: RequestConfig,
    /// The capacity.
    ///
    /// This is the capacity of the broadcast sender channel.
    pub(super) capacity: Capacity,
    /// The broadcast type.
    ///
    /// This defines the type of broadcast this WebSocket connection will participate in
    /// (point-to-point or point-to-group).
    pub(super) broadcast_type: BroadcastType<B>,
    /// The connected hook handler.
    ///
    /// This hook is executed when the WebSocket connection is established.
    pub(super) connected_hook: ServerHookHandler,
    /// The request hook handler.
    ///
    /// This hook is executed when a new request is received on the WebSocket.
    pub(super) request_hook: ServerHookHandler,
    /// The sended hook handler.
    ///
    /// This hook is executed after a message has been successfully sent over the WebSocket.
    pub(super) sended_hook: ServerHookHandler,
    /// The closed hook handler.
    ///
    /// This hook is executed when the WebSocket connection is closed.
    pub(super) closed_hook: ServerHookHandler,
}

```

# Path: hyperlane-plugin-websocket\src\websocket\trait.rs

```rust
/// A trait for types that can be used as broadcast identifiers.
///
/// Types implementing this trait must be convertible to a string,
/// be partially orderable, and be cloneable.
pub trait BroadcastTypeTrait: ToString + PartialOrd + Clone {}

```

# Path: hyperlane-quick-start\README.md


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


# Path: hyperlane-quick-start\README.ZH-CN.md


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


# Path: hyperlane-quick-start\app\lib.rs

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
use hyperlane_utils::*;

use hyperlane_plugin::log::*;

```

# Path: hyperlane-quick-start\app\exception\mod.rs

```rust
pub mod application;
pub mod framework;

pub use framework::*;

use super::*;

```

# Path: hyperlane-quick-start\app\exception\framework\impl.rs

```rust
use super::*;

impl ServerHook for PanicHook {
    async fn new(_ctx: &Context) -> Self {
        Self
    }

    #[epilogue_macros(
        response_version(HttpVersion::Http1_1),
        response_status_code(500),
        clear_response_headers,
        response_body(&response_body),
        response_header(SERVER => HYPERLANE),
        response_version(HttpVersion::Http1_1),
        response_header(CONTENT_TYPE, &content_type),
        send
    )]
    async fn handle(self, ctx: &Context) {
        let error: Panic = ctx.try_get_panic().await.unwrap_or_default();
        let error_message: String = error.to_string();
        log_error(&error_message).await;
        let api_response: ApiResponse<()> =
            ApiResponse::error_with_code(ResponseCode::InternalError, error_message);
        let response_body: Vec<u8> = api_response.to_json_bytes();
        let content_type: String =
            ContentType::format_content_type_with_charset(APPLICATION_JSON, UTF8);
    }
}

```

# Path: hyperlane-quick-start\app\exception\framework\mod.rs

```rust
mod r#impl;
mod r#struct;

pub use r#struct::*;

use super::*;
use model::data_transfer::common::*;

```

# Path: hyperlane-quick-start\app\exception\framework\struct.rs

```rust
use super::*;

#[panic_hook]
pub struct PanicHook;

```

# Path: hyperlane-quick-start\app\middleware\mod.rs

```rust
pub mod request;
pub mod response;

use super::*;

```

# Path: hyperlane-quick-start\app\middleware\request\mod.rs

```rust
pub mod cross;
pub mod response;
pub mod upgrade;

pub use cross::*;
pub use response::*;
pub use upgrade::*;

use super::*;

```

# Path: hyperlane-quick-start\app\middleware\request\cross\impl.rs

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

# Path: hyperlane-quick-start\app\middleware\request\cross\mod.rs

```rust
mod r#impl;
mod r#struct;

pub use r#struct::*;

use super::*;

```

# Path: hyperlane-quick-start\app\middleware\request\cross\struct.rs

```rust
use super::*;

#[request_middleware(1)]
pub struct CrossMiddleware;

```

# Path: hyperlane-quick-start\app\middleware\request\response\impl.rs

```rust
use super::*;

impl ServerHook for ResponseHeaderMiddleware {
    async fn new(_ctx: &Context) -> Self {
        Self
    }

    #[epilogue_macros(
        response_header(DATE => gmt()),
        response_header(SERVER => HYPERLANE),
        response_header(CONNECTION => KEEP_ALIVE),
        response_header(CONTENT_TYPE => content_type),
        response_header("SocketAddr" => socket_addr_string),
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

# Path: hyperlane-quick-start\app\middleware\request\response\mod.rs

```rust
mod r#impl;
mod r#struct;

pub use r#struct::*;

use super::*;
use hyperlane_config::application::templates::*;

```

# Path: hyperlane-quick-start\app\middleware\request\response\struct.rs

```rust
use super::*;

#[request_middleware(2)]
pub struct ResponseHeaderMiddleware;

#[request_middleware(3)]
pub struct ResponseStatusCodeMiddleware;

#[request_middleware(4)]
pub struct ResponseBodyMiddleware;

```

# Path: hyperlane-quick-start\app\middleware\request\upgrade\impl.rs

```rust
use super::*;

impl ServerHook for UpgradeMiddleware {
    async fn new(_ctx: &Context) -> Self {
        Self
    }

    #[ws]
    #[epilogue_macros(
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

# Path: hyperlane-quick-start\app\middleware\request\upgrade\mod.rs

```rust
mod r#impl;
mod r#struct;

pub use r#struct::*;

use super::*;

```

# Path: hyperlane-quick-start\app\middleware\request\upgrade\struct.rs

```rust
use super::*;

#[request_middleware(5)]
pub struct UpgradeMiddleware;

```

# Path: hyperlane-quick-start\app\middleware\response\mod.rs

```rust
pub mod log;
pub mod send;

pub use log::*;
pub use send::*;

use super::*;

```

# Path: hyperlane-quick-start\app\middleware\response\log\impl.rs

```rust
use super::*;

impl ServerHook for LogMiddleware {
    async fn new(_ctx: &Context) -> Self {
        Self
    }

    async fn handle(self, ctx: &Context) {
        let request: String = ctx.get_request().await.get_string();
        let response: String = ctx.get_response().await.get_string();
        log_info(request).await;
        log_info(response).await
    }
}

```

# Path: hyperlane-quick-start\app\middleware\response\log\mod.rs

```rust
mod r#impl;
mod r#struct;

pub use r#struct::*;

use super::*;

```

# Path: hyperlane-quick-start\app\middleware\response\log\struct.rs

```rust
use super::*;

#[response_middleware(2)]
pub struct LogMiddleware;

```

# Path: hyperlane-quick-start\app\middleware\response\send\impl.rs

```rust
use super::*;

impl ServerHook for SendMiddleware {
    async fn new(_ctx: &Context) -> Self {
        Self
    }

    #[epilogue_macros(http, reject(ctx.get_request_upgrade_type().await.is_ws()), send)]
    async fn handle(self, ctx: &Context) {}
}

```

# Path: hyperlane-quick-start\app\middleware\response\send\mod.rs

```rust
mod r#impl;
mod r#struct;

pub use r#struct::*;

use super::*;

```

# Path: hyperlane-quick-start\app\middleware\response\send\struct.rs

```rust
use super::*;

#[response_middleware(1)]
pub struct SendMiddleware;

```

# Path: hyperlane-quick-start\app\model\mod.rs

```rust
pub mod application;
pub mod data_transfer;
pub mod param;

use super::*;

use serde::{Deserialize, Serialize};
use serde_with::skip_serializing_none;
use utoipa::ToSchema;

```

# Path: hyperlane-quick-start\app\model\data_transfer\mod.rs

```rust
pub mod common;

use super::*;

```

# Path: hyperlane-quick-start\app\model\data_transfer\common\enum.rs

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

# Path: hyperlane-quick-start\app\model\data_transfer\common\impl.rs

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

# Path: hyperlane-quick-start\app\model\data_transfer\common\mod.rs

```rust
mod r#enum;
mod r#impl;
mod r#struct;

pub use r#enum::*;
pub use r#struct::*;

use super::*;

```

# Path: hyperlane-quick-start\app\model\data_transfer\common\struct.rs

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

# Path: hyperlane-quick-start\app\model\param\mod.rs

```rust
pub mod websocket;

use super::*;

```

# Path: hyperlane-quick-start\app\model\param\websocket\mod.rs

```rust
mod r#struct;

pub use r#struct::*;

use super::*;

use serde::{Deserialize, Serialize};

```

# Path: hyperlane-quick-start\app\model\param\websocket\struct.rs

```rust
use super::*;

#[derive(Debug, Clone, Default, Data, Deserialize, Serialize)]
pub struct WebSocketMessage {
    pub name: String,
    pub message: String,
}

```

# Path: hyperlane-quick-start\app\view\favicon\fn.rs

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

# Path: hyperlane-quick-start\app\view\favicon\mod.rs

```rust
mod r#fn;

pub use r#fn::*;

use super::*;
use hyperlane_config::business::logo_img::*;

```

# Path: hyperlane-quick-start\config\lib.rs

```rust
pub mod application;
pub mod framework;

use hyperlane::*;

```

# Path: hyperlane-quick-start\config\application\mod.rs

```rust
pub mod hello;
pub mod logo_img;
pub mod not_found;
pub mod templates;

```

# Path: hyperlane-quick-start\config\application\hello\const.rs

```rust
pub const NAME_KEY: &str = "name";

```

# Path: hyperlane-quick-start\config\application\hello\mod.rs

```rust
mod r#const;

pub use r#const::*;

```

# Path: hyperlane-quick-start\config\application\logo_img\const.rs

```rust
pub const LOGO_IMG_URL: &str = "https://docs.ltpp.vip/img/hyperlane.png";

```

# Path: hyperlane-quick-start\config\application\logo_img\mod.rs

```rust
mod r#const;

pub use r#const::*;

```

# Path: hyperlane-quick-start\config\application\not_found\const.rs

```rust
pub const NOT_FOUND_HTML: &str = include_str!("../../../resources/static/not_found/index.html");

```

# Path: hyperlane-quick-start\config\application\not_found\mod.rs

```rust
mod r#const;

pub use r#const::*;

```

# Path: hyperlane-quick-start\config\application\templates\const.rs

```rust
pub const INDEX_HTML: &str = include_str!("../../../resources/templates/index/index.html");

```

# Path: hyperlane-quick-start\config\application\templates\mod.rs

```rust
mod r#const;

pub use r#const::*;

```

# Path: hyperlane-quick-start\config\framework\const.rs

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
pub const SERVER_LINGER: Option<Duration> = None;
pub const SERVER_TTI: u32 = 128;
pub const SERVER_PID_FILE_PATH: &str = "./tmp/process/hyperlane.pid";

```

# Path: hyperlane-quick-start\config\framework\mod.rs

```rust
mod r#const;

pub use r#const::*;

use super::*;

use std::time::Duration;

```

# Path: hyperlane-quick-start\init\lib.rs

```rust
pub mod application;
pub mod framework;

use hyperlane::*;
use hyperlane_utils::*;

```

# Path: hyperlane-quick-start\init\framework\mod.rs

```rust
pub mod shutdown;
pub mod wait;

use super::*;

```

# Path: hyperlane-quick-start\init\framework\shutdown\fn.rs

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

# Path: hyperlane-quick-start\init\framework\shutdown\mod.rs

```rust
mod r#fn;
mod r#static;

pub use r#fn::*;

use super::*;
use r#static::*;

use std::sync::{Arc, OnceLock};

```

# Path: hyperlane-quick-start\init\framework\shutdown\static.rs

```rust
use super::*;

```

# Path: hyperlane-quick-start\init\framework\wait\fn.rs

```rust
use super::*;

#[hyperlane(config: ServerConfig)]
async fn init_config(server: &Server) {
    config.host(SERVER_HOST).await;
    config.port(SERVER_PORT).await;
    config.ttl(SERVER_TTI).await;
    config.linger(SERVER_LINGER).await;
    config.nodelay(SERVER_NODELAY).await;
    config.request_config(RequestConfig::default()).await;
    server.config(config).await;
}

async fn print_route_matcher(server: &Server) {
    let route_matcher: RouteMatcher = server.get_route_matcher().await;
    for key in route_matcher.get_static_route().keys() {
        println_success!("Static route: {key}");
    }
    for value in route_matcher.get_dynamic_route().values() {
        for (route_pattern, _) in value {
            println_success!("Dynamic route: {route_pattern}");
        }
    }
    for value in route_matcher.get_regex_route().values() {
        for (route_pattern, _) in value {
            println_success!("Regex route: {route_pattern}");
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
    init_config(&server).await;
    println_success!("Server initialization successful");
    let server_result: Result<ServerControlHook, ServerError> = server.run().await;
    match server_result {
        Ok(server_hook) => {
            let host_port: String = format!("{SERVER_HOST}:{SERVER_PORT}");
            print_route_matcher(&server).await;
            println_success!("Server listen in: {host_port}");
            let shutdown: SharedAsyncTaskFactory<()> = server_hook.get_shutdown_hook().clone();
            set_shutdown(shutdown);
            server_hook.wait().await;
        }
        Err(server_error) => println_error!("Server run error: {server_error}"),
    }
}

pub fn run() {
    runtime().block_on(create(create_server));
}

```

# Path: hyperlane-quick-start\init\framework\wait\mod.rs

```rust
mod r#fn;

pub use r#fn::*;

use super::{shutdown::*, *};
#[allow(unused_imports)]
use hyperlane_app::*;
use hyperlane_config::framework::*;
use hyperlane_plugin::process::*;

use tokio::runtime::{Builder, Runtime};

```

# Path: hyperlane-quick-start\plugin\lib.rs

```rust
pub mod log;
pub mod process;

use hyperlane_utils::*;

```

# Path: hyperlane-quick-start\plugin\log\fn.rs

```rust
use super::*;

pub async fn log_info<T>(data: T)
where
    T: AsRef<str>,
{
    println_warning!("{}", data.as_ref());
    LOG.async_info(data, log_handler).await;
}

pub async fn log_debug<T>(data: T)
where
    T: AsRef<str>,
{
    println_warning!("{}", data.as_ref());
    LOG.async_debug(data, log_handler).await;
}

pub async fn log_error<T>(data: T)
where
    T: AsRef<str>,
{
    println_error!("{}", data.as_ref());
    LOG.async_error(data, log_handler).await;
}

```

# Path: hyperlane-quick-start\plugin\log\mod.rs

```rust
mod r#fn;
mod r#static;

pub use r#fn::*;
pub use r#static::*;

use super::*;
use hyperlane_config::framework::*;
use hyperlane_utils::once_cell::sync::Lazy;

```

# Path: hyperlane-quick-start\plugin\log\static.rs

```rust
use super::*;

pub static LOG: Lazy<Log> = Lazy::new(|| {
    let mut log: Log = Log::default();
    log.path(SERVER_LOG_DIR);
    log.limit_file_size(SERVER_LOG_SIZE);
    log
});

```

# Path: hyperlane-quick-start\plugin\process\fn.rs

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
    let is_daemon: bool = args.len() >= 3 && args[2].to_lowercase() == "-d";
    let start_server = || async {
        if is_daemon {
            match manager.start_daemon().await {
                Ok(_) => println_success!("Server started in background successfully"),
                Err(error) => {
                    println_error!("Error starting server in background: {error}")
                }
            };
        } else {
            println_success!("Server started successfully");
            manager.start().await;
        }
    };
    let stop_server = || async {
        match manager.stop().await {
            Ok(_) => println_success!("Server stopped successfully"),
            Err(error) => println_error!("Error stopping server: {error}"),
        };
    };
    let hot_restart_server = || async {
        match manager
            .watch_detached(&["--clear", "--skip-local-deps", "-q", "-x", "run"])
            .await
        {
            Ok(_) => println_success!("Server started successfully"),
            Err(error) => println_error!("Error starting server in background: {error}"),
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
        "start" => start_server().await,
        "stop" => stop_server().await,
        "restart" => restart_server().await,
        "hot-restart" => hot_restart_server().await,
        _ => {
            println_error!("Invalid command: {command}");
        }
    }
}

```

# Path: hyperlane-quick-start\plugin\process\mod.rs

```rust
mod r#fn;

pub use r#fn::*;

use super::*;
use hyperlane_config::framework::*;

use std::{env::args, future::Future};

```

# Path: hyperlane-quick-start\resources\static\not_found\index.html

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

# Path: hyperlane-quick-start\resources\templates\index\index.html

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

# Path: hyperlane-quick-start\src\main.rs

```rust
fn main() {
    hyperlane_init::framework::wait::run();
}

```

# Path: hyperlane-time\README.md


## hyperlane-time

[Official Documentation](https://docs.ltpp.vip/hyperlane-time/)

[Api Docs](https://docs.rs/hyperlane-time/latest/hyperlane_time/)

> A library for fetching the current time based on the system's locale settings.

## Installation

To use this crate, you can run cmd:

```shell
cargo add hyperlane-time
```

## Use

```rust
use hyperlane_time::*;

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
```

## Contact


# Path: hyperlane-time\src\lib.rs

```rust
//! hyperlane-time
//!
//! A library for fetching the current time based on the system's locale settings.

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

# Path: hyperlane-time\src\time\cfg.rs

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

# Path: hyperlane-time\src\time\enum.rs

```rust
/// Represents supported languages.
///
/// Each variant corresponds to a specific language and locale combination.
#[derive(Debug, Default, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum Lang {
    /// English (United States).
    EnUsUtf8,
    /// Chinese (China).
    #[default]
    ZhCnUtf8,
    /// French (France).
    FrFrUtf8,
    /// German (Germany).
    DeDeUtf8,
    /// Spanish (Spain).
    EsEsUtf8,
    /// Italian (Italy).
    ItItUtf8,
    /// Japanese (Japan).
    JaJpUtf8,
    /// Korean (South Korea).
    KoKrUtf8,
    /// Portuguese (Portugal).
    PtPtUtf8,
    /// Russian (Russia).
    RuRuUtf8,
    /// Arabic (Saudi Arabia).
    ArSaUtf8,
    /// Hindi (India).
    HiInUtf8,
    /// Thai (Thailand).
    ThThUtf8,
    /// Vietnamese (Vietnam).
    ViVnUtf8,
    /// Dutch (Netherlands).
    NlNlUtf8,
    /// Swedish (Sweden).
    SvSeUtf8,
    /// Finnish (Finland).
    FiFiUtf8,
}

```

# Path: hyperlane-time\src\time\fn.rs

```rust
use crate::*;

/// Leap Year
pub const LEAP_YEAR: [u64; 12] = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

/// Common Year
pub const COMMON_YEAR: [u64; 12] = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

/// Days
pub const DAYS: [&str; 7] = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

/// Months
pub const MONTHS: [&str; 12] = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

/// Gets the time zone offset from the system environment variable.
///
/// This function retrieves the `LANG` environment variable and attempts to
/// parse it into a `Lang` value. If the variable is not set or cannot be
/// parsed, it defaults to `Lang::EnUsUtf8`.
///
/// # Returns
///
/// - `Lang` - The corresponding `Lang` value based on the `LANG` environment variable.
pub fn from_env_var() -> Lang {
    let lang: Lang = env::var("LANG")
        .unwrap_or_default()
        .parse::<Lang>()
        .unwrap_or_default();
    lang
}

/// Determines if a year is a leap year.
///
/// # Arguments
///
/// - `u64` - The year to check.
///
/// # Returns
///
/// - `bool` - Whether the year is a leap year.
#[inline(always)]
pub fn is_leap_year(year: u64) -> bool {
    (year.is_multiple_of(4) && !year.is_multiple_of(100)) || year.is_multiple_of(400)
}

/// Gets the current time, including the date and time.
///
/// # Returns
///
/// - `String` - The formatted time as "YYYY-MM-DD HH:MM:SS"
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

/// Gets the current day, without the time.
///
/// # Returns
///
/// - `String` - The formatted date as "YYYY-MM-DD"
pub fn date() -> String {
    let (year, month, day, _, _, _, _, _) = calculate_time();
    let mut date_time: String = String::new();
    write!(&mut date_time, "{year:04}-{month:02}-{day:02}").unwrap_or_default();
    date_time
}

/// Computes the year, month, and day from days since Unix epoch (1970-01-01).
///
/// # Arguments
///
/// - `u64` - Number of days since Unix epoch.
///
/// # Returns
///
/// - `(u64, u64, u64)` - Tuple containing year, month and day.
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

/// Gets the current date and time in GMT format.
///
/// # Returns
///
/// - `String` - The current date and time in GMT format.
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

/// Gets the current year.
///
/// # Returns
///
/// - `u64` - The current year
pub fn year() -> u64 {
    calculate_time().0
}

/// Gets the current month.
///
/// # Returns
///
/// - `u64` - The current month (1-12)
pub fn month() -> u64 {
    calculate_time().1
}

/// Gets the current day.
///
/// # Returns
///
/// - `u64` - The current day of the month
pub fn day() -> u64 {
    calculate_time().2
}

/// Gets the current hour.
///
/// # Returns
///
/// - `u64` - The current hour (0-23)
pub fn hour() -> u64 {
    calculate_time().3
}

/// Gets the current minute.
///
/// # Returns
///
/// - `u64` - The current minute (0-59)
pub fn minute() -> u64 {
    calculate_time().4
}

/// Gets the current second.
///
/// # Returns
///
/// - `u64` - The current second (0-59)
pub fn second() -> u64 {
    calculate_time().5
}

/// Gets the current timestamp in milliseconds.
///
/// # Returns
///
/// - `u64` - The current timestamp in milliseconds since Unix epoch
pub fn millis() -> u64 {
    calculate_time().6
}

/// Gets the current timestamp in microseconds.
///
/// # Returns
///
/// - `u64` - The current timestamp in microseconds since Unix epoch
pub fn micros() -> u64 {
    calculate_time().7
}

/// Calculates the current year, month, day, hour, minute, second, millisecond and microsecond.
///
/// # Returns
///
/// - `(u64, u64, u64, u64, u64, u64, u64, u64)` - Tuple containing:
///   - Year
///   - Month
///   - Day
///   - Hour (0-23)
///   - Minute (0-59)
///   - Second (0-59)
///   - Milliseconds in current second
///   - Microseconds in current second
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

/// Gets the current time with milliseconds, including the date and time.
///
/// # Returns
///
/// - `String` - The formatted time as "YYYY-MM-DD HH:MM:SS.sss"
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

/// Gets the current time with microseconds, including the date and time.
///
/// # Returns
///
/// - `String` - The formatted time as "YYYY-MM-DD HH:MM:SS.ssssss"
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

/// Gets the current timestamp in seconds since Unix epoch.
///
/// # Returns
///
/// - `u64` - The current timestamp in seconds
pub fn timestamp() -> u64 {
    let timezone_offset: u64 = from_env_var().value();
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_secs()
        .saturating_add(timezone_offset)
}

/// Gets the current timestamp in milliseconds since Unix epoch.
///
/// # Returns
///
/// - `u64` - The current timestamp in milliseconds
pub fn timestamp_millis() -> u64 {
    let timezone_offset: u64 = from_env_var().value();
    let duration: Duration = SystemTime::now().duration_since(UNIX_EPOCH).unwrap();
    (duration.as_secs().saturating_add(timezone_offset)) * 1000 + duration.subsec_millis() as u64
}

/// Gets the current timestamp in microseconds since Unix epoch.
///
/// # Returns
///
/// - `u64` - The current timestamp in microseconds
pub fn timestamp_micros() -> u64 {
    let timezone_offset: u64 = from_env_var().value();
    let duration: Duration = SystemTime::now().duration_since(UNIX_EPOCH).unwrap();
    (duration.as_secs().saturating_add(timezone_offset)) * 1_000_000
        + duration.subsec_micros() as u64
}

```

# Path: hyperlane-time\src\time\impl.rs

```rust
use crate::*;

/// Implementation of Display trait for Lang.
///
/// Provides a human-readable string representation for each language variant.
impl fmt::Display for Lang {
    /// Formats the language for display.
    ///
    /// # Arguments
    ///
    /// - `&mut fmt::Formatter` - The formatter to write to.
    ///
    /// # Returns
    ///
    /// - `fmt::Result` - The result of the formatting operation.
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
    /// Returns the UTC offset in seconds for the corresponding language.
    ///
    /// Each language is associated with a specific UTC offset,
    /// indicating the difference from Coordinated Universal Time (UTC).
    ///
    /// # Returns
    ///
    /// - `u64` - The UTC offset in seconds.
    pub fn value(&self) -> u64 {
        match self {
            Lang::EnUsUtf8 => 0,     // UTC
            Lang::ZhCnUtf8 => 28800, // UTC+8
            Lang::FrFrUtf8 => 3600,  // UTC+1
            Lang::DeDeUtf8 => 3600,  // UTC+1
            Lang::EsEsUtf8 => 3600,  // UTC+1
            Lang::ItItUtf8 => 3600,  // UTC+1
            Lang::JaJpUtf8 => 32400, // UTC+9
            Lang::KoKrUtf8 => 32400, // UTC+9
            Lang::PtPtUtf8 => 3600,  // UTC+1
            Lang::RuRuUtf8 => 10800, // UTC+3
            Lang::ArSaUtf8 => 10800, // UTC+3
            Lang::HiInUtf8 => 19800, // UTC+5:30
            Lang::ThThUtf8 => 25200, // UTC+7
            Lang::ViVnUtf8 => 25200, // UTC+7
            Lang::NlNlUtf8 => 3600,  // UTC+1
            Lang::SvSeUtf8 => 3600,  // UTC+1
            Lang::FiFiUtf8 => 3600,  // UTC+1
        }
    }
}

/// Implementation of FromStr trait for Lang.
///
/// Allows parsing a string into a Lang variant.
impl FromStr for Lang {
    /// The error type for parsing operations.
    type Err = ();

    /// Parses a string into a Lang variant.
    ///
    /// # Arguments
    ///
    /// - `&str` - The string to parse.
    ///
    /// # Returns
    ///
    /// - `Result<Self, Self::Err>` - The parsed Lang variant or an error.
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

# Path: hyperlane-time\src\time\mod.rs

```rust
pub(crate) mod cfg;
pub(crate) mod r#enum;
pub(crate) mod r#fn;
pub(crate) mod r#impl;

```

# Path: hyperlane-utils\README.md


## hyperlane-utils

[Official Documentation](https://docs.ltpp.vip/hyperlane-utils/)

[Api Docs](https://docs.rs/hyperlane-utils/latest/hyperlane_utils/)

> A library providing utils for hyperlane.

## Installation

To use this crate, you can run cmd:

```shell
cargo add hyperlane-utils
```

## Use

```rust
use hyperlane_utils::*;
```

## Contact


# Path: hyperlane-utils\src\lib.rs

```rust
//! hyperlane-utils
//!
//! A library providing utils for hyperlane.

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

# Path: ltpp-docs\src\appreciate.md


<Appreciate />

<CratesDownloads />

<GitHubMetrics />


# Path: ltpp-docs\src\catalog.md


> `Eastspire` 文档目录

<Catalog :level=2 />


# Path: ltpp-docs\src\hyperlane\README.md


[GITHUB 地址](https://github.com/hyperlane-dev/hyperlane)

[API 文档](https://docs.rs/hyperlane/latest/hyperlane/)

> 一个轻量级、高性能、跨平台的 Rust HTTP 服务器库，构建于 Tokio 之上，旨在简化现代 Web 服务开发。它内建对中间件、WebSocket、服务器发送事件（SSE）以及原始 TCP 通信的支持，同时在 Windows、Linux 和 macOS 平台上提供统一且符合人体工学的 API，使开发者能够以最小的开销和最大的灵活性构建健壮、可扩展、事件驱动的网络应用程序。

## 安装

要使用此 crate，可以运行以下命令：

```shell
cargo add hyperlane
```

## 快速开始

- [hyperlane-quick-start git](https://github.com/hyperlane-dev/hyperlane-quick-start)
- [hyperlane-quick-start docs](https://docs.ltpp.vip/hyperlane/quick-start/)

```sh
git clone https://github.com/hyperlane-dev/hyperlane-quick-start.git
```

## 使用示例

```rust
use hyperlane::*;

async fn send_body_hook(ctx: Context) {
    let body: ResponseBody = ctx.get_response_body().await;
    if ctx.get_request().await.is_ws() {
        let frame_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(&body);
        ctx.send_body_list_with_data(&frame_list).await.unwrap();
    } else {
        ctx.send_body().await.unwrap();
    }
}

async fn request_middleware(ctx: Context) {
    ctx.set_send_body_hook(send_body_hook).await;
    let socket_addr: String = ctx.get_socket_addr_string().await;
    ctx.set_response_version(HttpVersion::HTTP1_1)
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
        .set_response_header("SocketAddr", &socket_addr)
        .await;
}

async fn upgrade_hook(ctx: Context) {
    if !ctx.get_request().await.is_ws() {
        return;
    }
    if let Some(key) = &ctx.try_get_request_header_back(SEC_WEBSOCKET_KEY).await {
        let accept_key: String = WebSocketFrame::generate_accept_key(key);
        ctx.set_response_status_code(101)
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
            .await
            .unwrap();
    }
}

async fn response_middleware(ctx: Context) {
    if ctx.get_request().await.is_ws() {
        return;
    }
    let _ = ctx.send().await;
}

async fn root_route(ctx: Context) {
    let path: RequestPath = ctx.get_request_path().await;
    let response_body: String = format!("Hello hyperlane => {}", path);
    let cookie1: String = CookieBuilder::new("key1", "value1").http_only().build();
    let cookie2: String = CookieBuilder::new("key2", "value2").http_only().build();
    ctx.add_response_header(SET_COOKIE, &cookie1)
        .await
        .add_response_header(SET_COOKIE, &cookie2)
        .await
        .set_response_body(&response_body)
        .await;
}

async fn ws_route(ctx: Context) {
    if let Some(send_body_hook) = ctx.try_get_send_body_hook().await {
        while ctx.ws_from_stream(4096).await.is_ok() {
            let request_body: Vec<u8> = ctx.get_request_body().await;
            ctx.set_response_body(&request_body).await;
            send_body_hook(ctx.clone()).await;
        }
    }
}

async fn sse_route(ctx: Context) {
    let _ = ctx
        .set_response_header(CONTENT_TYPE, TEXT_EVENT_STREAM)
        .await
        .send()
        .await;
    for i in 0..10 {
        let _ = ctx
            .set_response_body(&format!("data:{}{}", i, HTTP_DOUBLE_BR))
            .await
            .send_body()
            .await;
    }
    let _ = ctx.closed().await;
}

async fn dynamic_route(ctx: Context) {
    let param: RouteParams = ctx.get_route_params().await;
    panic!("Test panic {:?}", param);
}

async fn panic_hook(ctx: Context) {
    let error: Panic = ctx.try_get_panic().await.unwrap_or_default();
    let response_body: String = error.to_string();
    let content_type: String = ContentType::format_content_type_with_charset(TEXT_PLAIN, UTF8);
    let _ = ctx
        .set_response_status_code(500)
        .await
        .clear_response_headers()
        .await
        .set_response_header(SERVER, HYPERLANE)
        .await
        .set_response_header(CONTENT_TYPE, &content_type)
        .await
        .set_response_body(&response_body)
        .await
        .send()
        .await;
}

#[tokio::main]
async fn main() {
    let config: ServerConfig = ServerConfig::new().await;
    config.host("0.0.0.0").await;
    config.port(60000).await;
    config.buffer(4096).await;
    config.disable_linger().await;
    config.disable_nodelay().await;
    let server: Server = Server::from(config).await;
    server.panic_hook(panic_hook).await;
    server.request_middleware(request_middleware).await;
    server.request_middleware(upgrade_hook).await;
    server.response_middleware(response_middleware).await;
    server.route("/", root_route).await;
    server.route("/ws", ws_route).await;
    server.route("/sse", sse_route).await;
    server.route("/dynamic/{routing}", dynamic_route).await;
    server.route("/regex/{file:^.*$}", dynamic_route).await;
    let server_hook: ServerHook = server.run().await.unwrap_or_default();
    server_hook.wait().await;
}
```


# Path: ltpp-docs\src\hyperlane\config\config.md


### 设置 `host`

> `hyperlane` 框架绑定 `host` 方式如下：

```rust
let config: ServerConfig = ServerConfig::new().await;
config.host("0.0.0.0").await;
```

### 设置 `port`

> `hyperlane` 框架绑定端口方式如下：

```rust
let config: ServerConfig = ServerConfig::new().await;
config.port(60000).await;
```

### 设置 `http_buffer`

> `hyperlane` 框架设置 `HTTP` 缓冲区大小方式如下（不设置或者设置为 `0` 则默认是 `4096` 字节）：

```rust
let config: ServerConfig = ServerConfig::new().await;
config.http_buffer(4096).await;
```

### 设置 `ws_buffer`

> `hyperlane` 框架设置 `websocket` 缓冲区大小方式如下：
> 不设置或者设置为 `0` 则默认是 `4096` 字节。

```rust
server.ws_buffer(4096).await;
```

### 设置 `linger`

> `hyperlane` 框架支持配置 `linger`，该选项基于 `Tokio` 的 `TcpStream::set_linger`，用于控制 `SO_LINGER` 选项，以决定连接关闭时未发送数据的处理方式，从而影响连接终止时的行为。

### 设置 `linger`

```rust
let config: ServerConfig = ServerConfig::new().await;
config.linger(Some(Duration::from_millis(10))).await;
```

### 开启 `linger`

```rust
let config: ServerConfig = ServerConfig::new().await;
config.enable_linger(Duration::from_millis(10)).await;
```

### 关闭 `linger`

```rust
let config: ServerConfig = ServerConfig::new().await;
config.disable_linger().await;
```

### 设置 `nodelay`

> `hyperlane` 框架支持配置 `nodelay`，该选项基于 `Tokio` 的 `TcpStream::set_nodelay`，用于控制 `TCP_NODELAY` 选项，以减少 `Nagle` 算法的影响，提高低延迟场景下的数据传输效率。

### 启用 `nodelay`

```rust
let config: ServerConfig = ServerConfig::new().await;
config.enable_nodelay().await;
```

```rust
let config: ServerConfig = ServerConfig::new().await;
config.nodelay(true).await;
```

### 禁用 `nodelay`

```rust
let config: ServerConfig = ServerConfig::new().await;
config.disable_nodelay().await;
```

```rust
let config: ServerConfig = ServerConfig::new().await;
config.nodelay(false).await;
```

### 设置 `ttl`

> `hyperlane` 框架支持配置 `ttl`，该选项基于 `Tokio` 的 `TcpStream::set_ttl`，用于控制 `IP_TTL` 选项，以设置传输数据包的生存时间（`Time To Live`），从而影响数据包在网络中的跳数限制。

```rust
let config: ServerConfig = ServerConfig::new().await;
config.ttl(128).await;
```

### 设置 `config_str`

> `hyperlane` 框架支持直接传入配置字符串。

```rust
let config_str: &'static str = r#"
    {
        "host": "0.0.0.0",
        "port": 80,
        "ws_buffer": 4096,
        "http_buffer": 4096,
        "nodelay": true,
        "linger": { "secs": 64, "nanos": 0 },
        "ttl": 64
    }
"#;
server.config_str(config_str).await;
```

### 设置 `config`

```rust
let config_str: &'static str = r#"
    {
        "host": "0.0.0.0",
        "port": 80,
        "ws_buffer": 4096,
        "http_buffer": 4096,
        "nodelay": true,
        "linger": { "secs": 64, "nanos": 0 },
        "ttl": 64
    }
"#;
let config: ServerConfig = ServerConfig::from_str(config_str).unwrap();
server.config(config).await;
```


# Path: ltpp-docs\src\hyperlane\config\middleware.md


> `hyperlane` 框架支持请求中间件和响应中间件，
> 支持多次注册，会按照注册顺序进行执行，如果任何阶段设置了 `aborted`，则后续注册的逻辑将不会执行。

### 请求中间件

#### 注册请求中间件

```rust
// 省略 server 创建
server.request_middleware(|ctx: Context| async move {
    // code
}).await;
```

#### 注册多个请求中间件

```rust
// 省略 server 创建
server.request_middleware(|ctx: Context| async move {
    // 1
}).await;
server.request_middleware(|ctx: Context| async move {
    // 2
}).await;
server.request_middleware(|ctx: Context| async move {
    // 3
}).await;
server.request_middleware(|ctx: Context| async move {
    // 4
}).await;
```

### 设置响应中间件

#### 注册响应中间件

```rust
// 省略 server 创建
server.response_middleware(|ctx: Context| async move {
    // code
}).await;
```

#### 注册多个响应中间件

```rust
// 省略 server 创建
server.response_middleware(|ctx: Context| async move {
    // 1
}).await;
server.response_middleware(|ctx: Context| async move {
    // 2
}).await;
server.response_middleware(|ctx: Context| async move {
    // 3
}).await;
server.response_middleware(|ctx: Context| async move {
    // 4
}).await;
```


# Path: ltpp-docs\src\hyperlane\config\panic-hook.md


> `hyperlane` 框架内部会对 `panic` 进行捕获，用户可通过钩子进行设置（不设置，框架默认不处理），
> 需要注意的是，触发 `panic` 后在执行 `panic_hook` 之前，框架会重置 `aborted` 状态，
> 支持多次注册，触发 `panic` 会按照注册顺序进行执行，如果任何阶段设置了 `aborted`，则后续注册的 `panic_hook` 将不会执行。

```rust
server.panic_hook(|cxt: Context| {
    let error: Panic = ctx.get_panic().await.unwrap_or_default();
    // do something
}).await;
```


# Path: ltpp-docs\src\hyperlane\config\route.md


> `hyperlane` 框架使用 `route` 接口进行路由注册，第一个参数是路由名称，第二个参数是路由处理函数，
> 框架支持动态路由，更多路由详细使用请参考[官方文档](../usage-introduction/route.md)，
> 路由处理函数参数类型参考 [controller-data 文档](../type/controller-data.md)。

### 注册路由

```rust
// 省略 server 创建
server.route("路由名称", |ctx: Context| async move {
    // code
}).await;
```


# Path: ltpp-docs\src\hyperlane\config\runtime.md


> `hyperlane` 框架基于 `tokio`，可以参考 `tokio` [官方文档](https://docs.rs/tokio/latest/tokio/) 进行配置。

### 快速配置

```rust
#[tokio::main]
async fn main() {}
```

### 精细化配置

```rust
fn main() {
    let thread_count: usize = get_thread_count();
    let runtime: tokio::runtime::Runtime = tokio::runtime::Builder::new_multi_thread()
        .worker_threads(thread_count)
        .thread_stack_size(2097152)
        .max_blocking_threads(5120)
        .max_io_events_per_tick(5120)
        .enable_all()
        .build()
        .unwrap();
    runtime().block_on(async move {}).unwrap();
}
```


# Path: ltpp-docs\src\hyperlane\config\server.md


> `hyperlane` 框架创建服务方式如下，需要调用 `run` 方法，服务才会正常运行。
> `ServerHook` 提供了等待框架运行完成和框架停止运行的 `hook`
> - `wait`: `server.run().await.unwrap_or_default().wait()` 实现等待框架运行完成
> - `shutdown`: `server.run().await.unwrap_or_default().shutdown()` 实现框架停止运行

## Server::new

```rust
let server: Server = Server::new().await;
let result: ServerResult<ServerHook> = server.run().await;
println!("Server result: {:?}", result);
let _ = std::io::Write::flush(&mut std::io::stderr());
```

## Server::from

```rust
let config: ServerConfig = ServerConfig::new().await;
let server: Server = Server::from(config).await;
let result: ServerResult<ServerHook> = server.run().await;
println!("Server result: {:?}", result);
let _ = std::io::Write::flush(&mut std::io::stderr());
```


# Path: ltpp-docs\src\hyperlane\help\async.md


### 异步

> 由于 `hyperlane` 框架本身涉及到锁的数据均采取 `tokio`中的读写锁实现，所以涉及到锁的方法调用均需要 `await`。


# Path: ltpp-docs\src\hyperlane\help\build.md


### 构建

```sh
cargo build --release
```

### 使用 `docker` 进行静态链接

#### Linux / MacOS

```sh
docker run --rm -v "$(pwd):/tmp/cargo_build" ccr.ccs.tencentyun.com/linux_environment/cargo:1.0.0 /bin/bash -c "source ~/.bashrc && cd /tmp/cargo_build && RUSTFLAGS='-C target-feature=-crt-static' cargo build --release --target x86_64-unknown-linux-gnu"
```

#### Windows

```sh
docker run --rm -v "${pwd}:/tmp/cargo_build" ccr.ccs.tencentyun.com/linux_environment/cargo:1.0.0 /bin/bash -c "source ~/.bashrc && cd /tmp/cargo_build && RUSTFLAGS='-C target-feature=-crt-static' cargo build --release --target x86_64-unknown-linux-gnu"
```


# Path: ltpp-docs\src\hyperlane\help\explain.md


### 框架说明

> `hyperlane` 仅提供最核心的功能(路由、中间件、异常处理、请求处理等基础核心的功能)。其余功能支持全部复用 `crate.io` 生态，这意味着你可以在 `hyperlane` 里使用 `crate.io` 里的第三方库，在 `hyperlane` 里集成他们是非常容易的事情。

### 推荐阅读

> 推荐阅读 [点击阅读](../../hyperlane-utils/README.md) 。


# Path: ltpp-docs\src\hyperlane\help\flamegraph.md


> `hyperlane` 框架使用 `flamegraph`，使用前提是需要有 `perf` 环境，生成火焰图步骤如下：

### 安装

```sh
cargo install flamegraph
```

### 使用

```sh
CARGO_PROFILE_RELEASE_DEBUG=true cargo flamegraph --release
```


# Path: ltpp-docs\src\hyperlane\help\install.md


### 安装

> 如果不使用 `Cargo.lock` 提交到 `git`，请在 `Cargo.toml` 文件的版本号前加 `=` 来锁定版本。

#### 命令

```shell
cargo add hyperlane;
```


# Path: ltpp-docs\src\hyperlane\middleware\auth.md


### 身份校验中间件

```rs
use hyperlane::*;

async fn http_version_middleware(ctx: Context) {
    ctx.set_response_version(HttpVersion::HTTP1_1).await;
}

async fn auth(ctx: Context) {
    let auth_str: String = ctx
        .get_request_header_back(AUTHORIZATION)
        .await
        .unwrap_or_default();
    if auth_str.is_empty() {
        ctx.set_response_status_code(401)
            .await
            .set_response_body("Unauthorized")
            .await
            .send()
            .await
            .unwrap();
        ctx.aborted().await;
    }
}

async fn index(ctx: Context) {
    ctx.set_response_status_code(200)
        .await
        .set_response_body("Hello, world!")
        .await;
}

async fn response_middleware(ctx: Context) {
    ctx.send().await.unwrap();
}

#[tokio::main]
async fn main() {
    Server::new()
        .request_middleware(http_version_middleware)
        .await
        .request_middleware(auth)
        .await
        .response_middleware(response_middleware)
        .await
        .route("/", index)
        .await
        .run()
        .await
        .unwrap()
        .wait()
        .await
}
```


# Path: ltpp-docs\src\hyperlane\middleware\cross.md


### 跨域中间件

```rust
pub async fn cross_middleware(ctx: Context) {
    ctx.set_response_version(HttpVersion::HTTP1_1)
        .await
        .set_response_header(ACCESS_CONTROL_ALLOW_ORIGIN, ANY)
        .await
        .set_response_header(ACCESS_CONTROL_ALLOW_METHODS, ALL_METHODS)
        .await
        .set_response_header(ACCESS_CONTROL_ALLOW_HEADERS, ANY)
        .await;
}

async fn index(ctx: Context) {
    ctx.set_response_status_code(200)
        .await
        .set_response_body("Hello, world!")
        .await;
}

async fn response_middleware(ctx: Context) {
    ctx.send().await.unwrap();
}

#[tokio::main]
async fn main() {
    Server::new()
        .request_middleware(cross_middleware)
        .await
        .response_middleware(response_middleware)
        .await
        .route("/", index)
        .await
        .run()
        .await
        .unwrap()
        .wait()
        .await
}
```


# Path: ltpp-docs\src\hyperlane\middleware\static-file.md


### 静态资源中间件

```rs
use hyperlane::*;

async fn middleware(ctx: Context) {
    ctx.set_response_version(HttpVersion::HTTP1_1)
        .await
        .set_attribute("static_dir_path", "./")
        .await;
}

async fn static_middleware(ctx: Context) {
    let static_path_opt: Option<&str> = ctx.try_get_attribute("static_dir_path").await;
    let static_path: &str = static_path_opt.expect("attribute static_dir_path not found");
    let path: String = ctx.get_request_path().await;
    let file_path: String = format!("{static_path}{path}");
    let file_extension: String = FileExtension::get_extension_name(&file_path);
    let content_type: &'static str = FileExtension::parse(&file_extension).get_content_type();
    let content_type: String = ContentType::format_content_type_with_charset(content_type, UTF8);
    ctx.set_response_header(CONTENT_TYPE, content_type).await;
    let file_data_opt: Option<String> = tokio::fs::read_to_string(&file_path).await.ok();
    ctx.set_attribute("static_file_data", file_data_opt).await;
}

async fn response_middleware(ctx: Context) {
    let static_file_data_opt: Option<String> = ctx
        .try_get_attribute("static_file_data")
        .await
        .expect("attribute static_file_data not found");
    let _ = ctx
        .set_response_body(static_file_data_opt.unwrap_or_default())
        .await
        .send()
        .await;
}

#[tokio::main]
async fn main() {
    Server::new()
        .await
        .request_middleware(middleware)
        .await
        .request_middleware(static_middleware)
        .await
        .response_middleware(response_middleware)
        .await
        .run()
        .await
        .unwrap()
        .wait()
        .await
}
```


# Path: ltpp-docs\src\hyperlane\middleware\timeout.md


### 超时中间件

```rust
use hyperlane::{
    tokio::{
        spawn,
        time::{sleep, timeout},
    },
    *,
};
use std::time::Duration;

async fn http_version_middleware(ctx: Context) {
    ctx.set_response_version(HttpVersion::HTTP1_1).await;
}

async fn timeout_middleware(ctx: Context) {
    spawn(async move {
        timeout(Duration::from_millis(100), async move {
            ctx.set_response_status_code(504)
                .await
                .set_response_body("timeout")
                .await
                .send()
                .await
                .unwrap();
            ctx.aborted().await;
        })
        .await
        .unwrap();
    });
}

async fn index(ctx: Context) {
    sleep(Duration::from_secs(1)).await;
    ctx.set_response_status_code(200)
        .await
        .set_response_body("Hello, world!")
        .await;
}

async fn response_middleware(ctx: Context) {
    ctx.send().await.unwrap();
}

#[tokio::main]
async fn main() {
    Server::new()
        .request_middleware(http_version_middleware)
        .await
        .request_middleware(timeout_middleware)
        .await
        .response_middleware(response_middleware)
        .await
        .route("/", index)
        .await
        .run()
        .await
        .unwrap()
        .wait()
        .await
}
```


# Path: ltpp-docs\src\hyperlane\quick-start\directory.md


> 基于 `hyperlane` 设计的目录结构，配置和业务分离，扩展以插件形式存在，便于开发和维护。

```txt
├── app                      # app目录
│   ├── aspect               # 切面编程层
│   ├── controller           # 接口控制层
│   ├── exception            # 异常处理层
│   ├── filter               # 过滤器层
│   ├── mapper               # 数据访问层
│   ├── middleware           # 中间件层
│   ├── model                # 数据模型层
│      ├── application       # 应用对象
│      ├── bean              # 实体对象
│      ├── business          # 业务对象
│      ├── data              # 数据对象
│      ├── data_access       # 数据访问对象
│      ├── data_transfer     # 数据传输对象
│      ├── domain            # 领域对象
│      ├── param             # 参数对象
│      ├── persistent        # 持久化对象
│      ├── view              # 视图对象
│   ├── service              # 业务逻辑层
│   ├── utils                # 工具层
│   ├── view                 # 视图层
├── config                   # 配置目录
│   ├── business             # 业务配置
│   ├── framework            # 框架配置
│   ├── server_manager       # 服务管理配置
├── init                     # 初始化目录
│   ├── business             # 业务初始化
│   ├── framework            # 框架始化
├── plugin                   # 插件目录
│   ├── log                  # 日志插件
│   ├── server_manager       # 服务进程管理插件
├── resources                # 资源目录
│   ├── static               # 静态资源目录
│      ├── html              # HTML静态资源
│      ├── img               # 图片静态资源
│   ├── templates            # 模板目录
│      ├── html              # HTML模板
```

## 🗂 各层级调用关系详解

### `app/controller`（接口控制层）

- 调用：

  - `service`：处理业务逻辑。
  - `model/param`：接收请求参数。
  - `model/view`：返回视图对象。
  - `model/data_transfer`：构建 DTO 返回。
  - `utils`：使用工具函数处理请求数据。
  - `exception`：统一异常抛出。
  - `filter` / `middleware`：作为请求链的入口或出口。
  - `aspect`：被 AOP 织入切面逻辑。
  - `view`：视图渲染。
  - `resources/templates`：页面模板渲染。
  - `resources/static`：静态资源引用。
  - `plugin/*`：调用日志记录、服务管理等插件。

### `app/service`（业务逻辑层）

- 调用：

  - `mapper`：访问数据库。
  - `model/business`：封装业务对象。
  - `model/domain`：应用领域建模。
  - `model/data_transfer`：服务返回值封装。
  - `exception`：业务异常处理。
  - `utils`：辅助计算、验证、转换等。
  - `plugin/*`：调用插件完成增强能力。

- 被调用：

  - `controller`

### `app/mapper`（数据访问层）

- 调用：

  - `model/data_access`：数据库表映射。
  - `model/persistent`：持久化结构体。
  - `utils`：SQL 构建等辅助操作。

- 被调用：

  - `service`

### `app/model/*`（数据模型层）

> 被多个模块依赖和使用，不主动调用其他层。

#### 常用子模块说明：

| 子模块          | 使用场景                                           |
| --------------- | -------------------------------------------------- |
| `application`   | 应用级上下文对象，用于 service/mapper 层组合数据。 |
| `bean`          | 通用实体定义，如 User、Order 等。                  |
| `business`      | 业务组合对象，如 OrderDetail + PaymentInfo。       |
| `data`          | 中间数据对象，在服务流程中传递状态。               |
| `data_access`   | 映射 DAO/ORM 结构，数据库字段。                    |
| `data_transfer` | DTO 层，controller → client 层数据输出。           |
| `domain`        | 领域建模，对应 DDD 的 Aggregate/Entity/VO。        |
| `param`         | controller 接收参数封装。                          |
| `persistent`    | 映射数据库存储模型。                               |
| `view`          | 用于最终渲染视图页面的模型。                       |

**Model 详细介绍**

| 目录名          | 中文名       | 典型职责                                             | 使用场景举例                                        | 与其它层关系                               |
| --------------- | ------------ | ---------------------------------------------------- | --------------------------------------------------- | ------------------------------------------ |
| `application`   | 应用对象     | 编排多个业务对象，处理用户用例                       | 服务层 `UserService` 聚合多个 `UserBO` 处理注册流程 | 调用 `business`，传递 `param`、返回 `view` |
| `bean`          | 实体对象     | 数据实体，表现为 Struct 或 ORM 实体                  | `UserEntity`、`ArticleEntity`，保存于数据库         | 被 `persistent` 持久化，供 `domain` 使用   |
| `business`      | 业务对象     | 封装核心业务逻辑（BO）                               | `UserBO::register` 内部逻辑完整，不依赖框架         | 被 `application` 调用                      |
| `data`          | 数据对象     | 数据结构本身，不带行为（值对象、常量等）             | `GenderEnum`、`IdVO`、`DateRange`                   | 被 `domain` 和 `dto` 等层使用              |
| `data_access`   | 数据访问对象 | 封装数据库交互（DAO、Repository）                    | `UserRepository::find_by_email()`                   | 操作 `bean` 或 `persistent`                |
| `data_transfer` | 数据传输对象 | 接口中传输的数据载体，常用于请求响应、分页、统一结构 | `ApiResponse<T>`、`Page<T>`、`UserDto`              | 被 controller、OpenAPI 文档广泛使用        |
| `param`         | 参数对象     | 接口入参、查询条件、分页等                           | `LoginParam`、`SearchQueryParam`                    | 传入 `application` 层                      |
| `persistent`    | 持久化对象   | ORM 映射专用结构体，有时带属性注解                   | `UserPersistent` 映射数据库字段                     | 与 `bean` 相似，偏向实现层                 |
| `domain`        | 领域对象     | 领域模型（实体和值对象），封装行为                   | `OrderAggregate`，可带行为如 `Order::cancel()`      | 被 `business` 聚合使用                     |
| `view`          | 视图对象     | 接口输出结果的表现结构，适配前端需求                 | `UserProfileView`、`ArticleDetailView`              | 从 `dto` 或 `bean` 转换而来                |

### `app/exception`（异常处理层）

- 被调用：

  - `controller`
  - `service`
  - `mapper`

### `app/filter`（过滤器层）

- 被调用：

  - `controller` 请求前过滤。

### `app/middleware`（中间件层）

- 被调用：

  - `controller` 请求或响应阶段增强，如权限校验、Header 注入等。

### `app/aspect`（切面编程层）

- 被调用：

  - 自动织入 `controller`、`service` 等层处理日志、安全等横切关注点。

### `app/utils`（工具层）

- 被调用：

  - `controller`
  - `service`
  - `mapper`
  - `model`（可选）

### `app/view`（视图层）

- 被调用：

  - `controller` 用于模板渲染（结合 `resources/templates`）

### `resources`（资源目录）

- 子目录说明：

  - `static/html`、`img`：被 `view` 层或浏览器直接访问。
  - `templates/html`：被 `controller` 或 `view` 用于渲染页面。


# Path: ltpp-docs\src\hyperlane\quick-start\README.md


## 快速开始

> 这是基于 `hyperlane` 封装的项目（[hyperlane-quick-start](https://github.com/hyperlane-dev/hyperlane-quick-start)），旨在简化使用和规范项目代码结构。

### 克隆项目

```sh
git clone https://github.com/hyperlane-dev/hyperlane-quick-start.git
```

### 进入项目

```sh
cd hyperlane-quick-start
```

### 运行

> 此项目使用 `server-manager` 进行服务管理。
> 使用参考 [官方文档](../../server-manager/README.md)。

#### 运行

```sh
cargo run
```

#### 在后台运行

```sh
cargo run -d
```

#### 停止

```sh
cargo run stop
```

#### 重启

```sh
cargo run restart
```

#### 重启在后台运行

```sh
cargo run restart -d
```

#### 热重启

```sh
cargo run hot
```


# Path: ltpp-docs\src\hyperlane\speed\close-keep-alive.md


[GITHUB 地址](https://github.com/hyperlane-dev/web-server-pressure-measurement/tree/master/close-keep-alive)

### wrk

#### 压测命令

```sh
wrk -c360 -d60s -H "Connection: close" http://127.0.0.1:60000/
```

#### 压测结果

> 测试 `360` 并发，持续 `60s` 请求。`QPS` 结果如下：
> - 1 `Hyperlane框架` ：51031.27
> - 2 `Tokio` ：49555.87
> - 3 `Rocket框架` ：49345.76
> - 4 `Gin框架` ：40149.75
> - 5 `Go标准库` ：38364.06
> - 6 `Rust标准库` ：30142.55
> - 7 `Node标准库` ：28286.96

#### hyperlane 框架

```sh
#### Rust 标准库

```sh
#### Tokio 框架

```sh
#### Rocket 框架

```sh
#### Gin 框架

```sh
#### Go 标准库

```sh
#### Node 标准库

```sh
### ab

#### 压测命令

```sh
ab -n 1000000 -c 1000 -r http://127.0.0.1:60000/
```

#### 压测结果

> 测试 `1000` 并发，一共 `100w` 请求。`QPS` 结果如下：
> - 1 `Tokio` ：51825.13
> - 2 `Hyperlane框架` ：51554.47
> - 3 `Rocket框架` ：49621.02
> - 4 `Go标准库` ：47915.20
> - 5 `Gin框架` ：47081.05
> - 6 `Node标准库` ：44763.11
> - 7 `Rust标准库` ：31511.00

#### hyperlane 框架

```sh
Server Hostname:        127.0.0.1
Server Port:            60000

Document Path:          /
Document Length:        5 bytes

Concurrency Level:      1000
Time taken for tests:   19.397 seconds
Complete requests:      1000000
Failed requests:        0
Total transferred:      107000000 bytes
HTML transferred:       5000000 bytes
Requests per second:    51554.47 [#/sec] (mean)
Time per request:       19.397 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)
Transfer rate:          5387.04 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    9   9.1      8    1069
Processing:     0   10   4.7     10     289
Waiting:        0    9   4.5      9     286
Total:          1   19  11.1     19    1085

Percentage of the requests served within a certain time (ms)
  50%     19
  66%     22
  75%     24
  80%     25
  90%     29
  95%     33
  98%     37
  99%     41
 100%   1085 (longest request)
```

#### Rust 标准库

```sh
Server Hostname:        127.0.0.1
Server Port:            60000

Document Path:          /
Document Length:        5 bytes

Concurrency Level:      1000
Time taken for tests:   31.735 seconds
Complete requests:      1000000
Failed requests:        0
Total transferred:      88000000 bytes
HTML transferred:       5000000 bytes
Requests per second:    31511.00 [#/sec] (mean)
Time per request:       31.735 [ms] (mean)
Time per request:       0.032 [ms] (mean, across all concurrent requests)
Transfer rate:          2707.98 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0   22 167.7      0    7232
Processing:     0    9  45.2      4    5771
Waiting:        0    9  45.2      4    5771
Total:          0   31 178.6      4    7441

Percentage of the requests served within a certain time (ms)
  50%      4
  66%      5
  75%      5
  80%      6
  90%      7
  95%      8
  98%    426
  99%   1050
 100%   7441 (longest request)
```

#### Tokio 框架

```sh
Server Hostname:        127.0.0.1
Server Port:            60000

Document Path:          /
Document Length:        5 bytes

Concurrency Level:      1000
Time taken for tests:   19.296 seconds
Complete requests:      1000000
Failed requests:        0
Total transferred:      88000000 bytes
HTML transferred:       5000000 bytes
Requests per second:    51825.13 [#/sec] (mean)
Time per request:       19.296 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)
Transfer rate:          4453.72 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    9  19.4      8    1091
Processing:     0   10   5.4      9     284
Waiting:        0    9   5.2      8     284
Total:          0   19  20.6     18    1107

Percentage of the requests served within a certain time (ms)
  50%     18
  66%     21
  75%     23
  80%     25
  90%     29
  95%     33
  98%     38
  99%     42
 100%   1107 (longest request)
```

#### Rocket 框架

```sh
Server Software:        Rocket
Server Hostname:        127.0.0.1
Server Port:            60000

Document Path:          /
Document Length:        13 bytes

Concurrency Level:      1000
Time taken for tests:   20.153 seconds
Complete requests:      1000000
Failed requests:        0
Total transferred:      247000000 bytes
HTML transferred:       13000000 bytes
Requests per second:    49621.02 [#/sec] (mean)
Time per request:       20.153 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)
Transfer rate:          11969.13 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    9  11.2      9    1094
Processing:     0   11   5.4     10     305
Waiting:        0   10   5.2      9     305
Total:          0   20  13.3     19    1107

Percentage of the requests served within a certain time (ms)
  50%     19
  66%     22
  75%     25
  80%     26
  90%     30
  95%     34
  98%     39
  99%     43
 100%   1107 (longest request)
```

#### Gin 框架

```sh
Server Hostname:        127.0.0.1
Server Port:            60000

Document Path:          /
Document Length:        5 bytes

Concurrency Level:      1000
Time taken for tests:   21.240 seconds
Complete requests:      1000000
Failed requests:        0
Total transferred:      140000000 bytes
HTML transferred:       5000000 bytes
Requests per second:    47081.05 [#/sec] (mean)
Time per request:       21.240 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)
Transfer rate:          6436.86 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0   10  13.0      9    1095
Processing:     0   12   6.0     11     288
Waiting:        0   11   5.8     10     286
Total:          1   21  15.1     20    1114

Percentage of the requests served within a certain time (ms)
  50%     20
  66%     23
  75%     26
  80%     27
  90%     32
  95%     35
  98%     40
  99%     44
 100%   1114 (longest request)
```

#### Go 标准库

```sh
Server Hostname:        127.0.0.1
Server Port:            60000

Document Path:          /
Document Length:        13 bytes

Concurrency Level:      1000
Time taken for tests:   20.870 seconds
Complete requests:      1000000
Failed requests:        0
Total transferred:      149000000 bytes
HTML transferred:       13000000 bytes
Requests per second:    47915.20 [#/sec] (mean)
Time per request:       20.870 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)
Transfer rate:          6972.04 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    9  21.1      8    1103
Processing:     0   11   6.5     11     323
Waiting:        0   10   6.3     10     322
Total:          1   21  22.6     19    1120

Percentage of the requests served within a certain time (ms)
  50%     19
  66%     23
  75%     25
  80%     27
  90%     31
  95%     35
  98%     41
  99%     46
 100%   1120 (longest request)
```

#### Node 标准库

```sh
Server Hostname:        127.0.0.1
Server Port:            60000

Document Path:          /
Document Length:        13 bytes

Concurrency Level:      1000
Time taken for tests:   22.340 seconds
Complete requests:      1000000
Failed requests:        0
Total transferred:      114000000 bytes
HTML transferred:       13000000 bytes
Requests per second:    44763.11 [#/sec] (mean)
Time per request:       22.340 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
Transfer rate:          4983.39 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    6  42.1      4    1086
Processing:     0   16  11.7     15     453
Waiting:        0   13  11.2     12     452
Total:          1   22  43.7     20    1108

Percentage of the requests served within a certain time (ms)
  50%     20
  66%     22
  75%     23
  80%     24
  90%     27
  95%     29
  98%     33
  99%     37
 100%   1108 (longest request)
```


# Path: ltpp-docs\src\hyperlane\speed\env.md


[GITHUB 地址](https://github.com/hyperlane-dev/web-server-pressure-measurement)

### 环境信息

- 系统: `Ubuntu20.04.6 LTS`
- CPU: `i9-14900KF`
- 内存: `192GB 6400MT/S（实际运行 4000MT/S）`
- 硬盘: `SKC3000D2048G * 2`
- GPU: `AMD Radeon RX 6750 GRE 10GB`

### 调优

#### Linux 内核调优

> 打开文件 `/etc/sysctl.conf`，增加以下设置。

```sh
#该参数设置系统的TIME_WAIT的数量，如果超过默认值则会被立即清除
net.ipv4.tcp_max_tw_buckets = 20000
#定义了系统中每一个端口最大的监听队列的长度，这是个全局的参数
net.core.somaxconn = 65535
#对于还未获得对方确认的连接请求，可保存在队列中的最大数目
net.ipv4.tcp_max_syn_backlog = 262144
#在每个网络接口接收数据包的速率比内核处理这些包的速率快时，允许送到队列的数据包的最大数目
net.core.netdev_max_backlog = 30000
#此选项会导致处于NAT网络的客户端超时，建议为0。Linux从4.12内核开始移除了 tcp_tw_recycle 配置，如果报错"No such file or directory"请忽略
net.ipv4.tcp_tw_recycle = 0
#系统所有进程一共可以打开的文件数量
fs.file-max = 6815744
#防火墙跟踪表的大小。注意：如果防火墙没开则会提示error: "net.netfilter.nf_conntrack_max" is an unknown key，忽略即可
net.netfilter.nf_conntrack_max = 2621440
net.ipv4.ip_local_port_range = 10240 65000
```

#### 控制台执行 `ulimit`

```sh
ulimit -n 1024000
```

#### 打开文件数

> 修改 `open files` 的数值重启后永久生效，修改配置文件：`/etc/security/limits.conf`。在这个文件后加上

```sh
* soft nofile 1024000
* hard nofile 1024000
root soft nofile 1024000
root hard nofile 1024000
```

#### 运行命令

```sh
RUSTFLAGS="-C target-cpu=native -C link-arg=-fuse-ld=lld" cargo run --release
```


# Path: ltpp-docs\src\hyperlane\speed\flamegraph.md


## plaintext


# Path: ltpp-docs\src\hyperlane\speed\open-keep-alive.md


[GITHUB 地址](https://github.com/hyperlane-dev/web-server-pressure-measurement/tree/master/open-keep-alive)

### wrk

#### 压测命令

```sh
wrk -c360 -d60s http://127.0.0.1:60000/
```

#### 压测结果

> 测试 `360` 并发，持续 `60s` 请求。`QPS` 结果如下：
> - 1 `Tokio` ：340130.92
> - 2 `Hyperlane框架` ：324323.71
> - 3 `Rocket框架` ：298945.31
> - 4 `Rust标准库` ：291218.96
> - 5 `Gin框架` ：242570.16
> - 6 `Go标准库` ：234178.93
> - 7 `Node标准库` ：139412.13

#### hyperlane 框架

```sh
#### Rust 标准库

```sh
#### Tokio 框架

```sh
#### Rocket 框架

```sh
#### Gin 框架

```sh
#### Go 标准库

```sh
#### Node 标准库

```sh
### ab

#### 压测命令

```sh
ab -n 1000000 -c 1000 -r -k http://127.0.0.1:60000/
```

#### 压测结果

> 测试 `1000` 并发，一共 `100w` 请求。`QPS` 结果如下：
> - 1 `Tokio` ：308596.26
> - 2 `Hyperlane框架` ：307568.90
> - 3 `Rocket框架` ：267931.52
> - 4 `Rust标准库` ：260514.56
> - 5 `Go标准库` ：226550.34
> - 6 `Gin框架` ：224296.16
> - 7 `Node标准库` ：85357.18

#### hyperlane 框架

```sh
Server Hostname:        127.0.0.1
Server Port:            60000

Document Path:          /
Document Length:        5 bytes

Concurrency Level:      1000
Time taken for tests:   3.251 seconds
Complete requests:      1000000
Failed requests:        0
Keep-Alive requests:    1000000
Total transferred:      107000000 bytes
HTML transferred:       5000000 bytes
Requests per second:    307568.90 [#/sec] (mean)
Time per request:       3.251 [ms] (mean)
Time per request:       0.003 [ms] (mean, across all concurrent requests)
Transfer rate:          32138.55 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.3      0      11
Processing:     0    3   1.4      3      13
Waiting:        0    3   1.4      3      13
Total:          0    3   1.4      3      16

Percentage of the requests served within a certain time (ms)
  50%      3
  66%      4
  75%      4
  80%      4
  90%      5
  95%      6
  98%      7
  99%      7
 100%     16 (longest request)
```

#### Rust 标准库

```sh
Server Hostname:        127.0.0.1
Server Port:            60000

Document Path:          /
Document Length:        5 bytes

Concurrency Level:      1000
Time taken for tests:   3.839 seconds
Complete requests:      1000000
Failed requests:        0
Keep-Alive requests:    1000000
Total transferred:      93000000 bytes
HTML transferred:       5000000 bytes
Requests per second:    260514.56 [#/sec] (mean)
Time per request:       3.839 [ms] (mean)
Time per request:       0.004 [ms] (mean, across all concurrent requests)
Transfer rate:          23660.01 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0  21.2      0    1069
Processing:     0    3   5.5      3     419
Waiting:        0    3   5.5      3     419
Total:          0    4  23.4      3    1286

Percentage of the requests served within a certain time (ms)
  50%      3
  66%      4
  75%      4
  80%      4
  90%      5
  95%      6
  98%      8
  99%      8
 100%   1286 (longest request)
```

#### Tokio 框架

```sh
Server Hostname:        127.0.0.1
Server Port:            60000

Document Path:          /
Document Length:        5 bytes

Concurrency Level:      1000
Time taken for tests:   3.240 seconds
Complete requests:      1000000
Failed requests:        0
Keep-Alive requests:    1000000
Total transferred:      93000000 bytes
HTML transferred:       5000000 bytes
Requests per second:    308596.26 [#/sec] (mean)
Time per request:       3.240 [ms] (mean)
Time per request:       0.003 [ms] (mean, across all concurrent requests)
Transfer rate:          28026.81 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.3      0      11
Processing:     0    3   1.3      3      16
Waiting:        0    3   1.3      3      16
Total:          0    3   1.4      3      16

Percentage of the requests served within a certain time (ms)
  50%      3
  66%      4
  75%      4
  80%      4
  90%      5
  95%      6
  98%      7
  99%      7
 100%     16 (longest request)
```

#### Rocket 框架

```sh
Server Software:        Rocket
Server Hostname:        127.0.0.1
Server Port:            60000

Document Path:          /
Document Length:        13 bytes

Concurrency Level:      1000
Time taken for tests:   3.732 seconds
Complete requests:      1000000
Failed requests:        0
Keep-Alive requests:    1000000
Total transferred:      271000000 bytes
HTML transferred:       13000000 bytes
Requests per second:    267931.52 [#/sec] (mean)
Time per request:       3.732 [ms] (mean)
Time per request:       0.004 [ms] (mean, across all concurrent requests)
Transfer rate:          70907.66 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.2      0      14
Processing:     0    4   1.4      4      17
Waiting:        0    4   1.4      4      17
Total:          0    4   1.4      4      21

Percentage of the requests served within a certain time (ms)
  50%      4
  66%      4
  75%      5
  80%      5
  90%      6
  95%      6
  98%      7
  99%      8
 100%     21 (longest request)
```

#### Gin 框架

```sh
Server Hostname:        127.0.0.1
Server Port:            60000

Document Path:          /
Document Length:        5 bytes

Concurrency Level:      1000
Time taken for tests:   4.458 seconds
Complete requests:      1000000
Failed requests:        0
Keep-Alive requests:    1000000
Total transferred:      145000000 bytes
HTML transferred:       5000000 bytes
Requests per second:    224296.16 [#/sec] (mean)
Time per request:       4.458 [ms] (mean)
Time per request:       0.004 [ms] (mean, across all concurrent requests)
Transfer rate:          31760.69 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.2      0       7
Processing:     0    4   4.7      4     181
Waiting:        0    4   4.7      4     181
Total:          0    4   4.8      4     184

Percentage of the requests served within a certain time (ms)
  50%      4
  66%      5
  75%      5
  80%      6
  90%      8
  95%     10
  98%     12
  99%     13
 100%    184 (longest request)
```

#### Go 标准库

```sh
Server Hostname:        127.0.0.1
Server Port:            60000

Document Path:          /
Document Length:        13 bytes

Concurrency Level:      1000
Time taken for tests:   4.414 seconds
Complete requests:      1000000
Failed requests:        0
Keep-Alive requests:    1000000
Total transferred:      154000000 bytes
HTML transferred:       13000000 bytes
Requests per second:    226550.34 [#/sec] (mean)
Time per request:       4.414 [ms] (mean)
Time per request:       0.004 [ms] (mean, across all concurrent requests)
Transfer rate:          34071.05 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.2      0       7
Processing:     0    4   3.9      4     172
Waiting:        0    4   3.9      4     172
Total:          0    4   4.0      4     176

Percentage of the requests served within a certain time (ms)
  50%      4
  66%      4
  75%      5
  80%      5
  90%      7
  95%      8
  98%      8
  99%      9
 100%    176 (longest request)
```

#### Node 标准库

```sh
Server Hostname:        127.0.0.1
Server Port:            60000

Document Path:          /
Document Length:        13 bytes

Concurrency Level:      1000
Time taken for tests:   11.715 seconds
Complete requests:      1000000
Failed requests:        811908
   (Connect: 0, Receive: 14737, Length: 499810, Exceptions: 297361)
Keep-Alive requests:    500200
Total transferred:      59523800 bytes
HTML transferred:       6502600 bytes
Requests per second:    85357.18 [#/sec] (mean)
Time per request:       11.715 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
Transfer rate:          4961.70 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    3  33.5      0    1082
Processing:     0    8   9.6      7     247
Waiting:        0    7  10.5      3     247
Total:          0   12  35.3      9    1102

Percentage of the requests served within a certain time (ms)
  50%      9
  66%     15
  75%     17
  80%     18
  90%     21
  95%     23
  98%     27
  99%     30
 100%   1102 (longest request)
```


# Path: ltpp-docs\src\hyperlane\speed\request-time.md


[GITHUB 地址](https://github.com/hyperlane-dev/test-request)

> 测试累计请求 `1w` 次

| 场景      | http-request 平均耗时 | hyper 平均耗时 |
| --------- | --------------------- | -------------- |
| TCP 失败  | 39us                  | 78us           |
| hyperlane | 100us                 | 150us          |
| 阿帕奇    | 300us                 | 2500us         |


# Path: ltpp-docs\src\hyperlane\usage-introduction\addr.md


> `hyperlane` 框架封装了获取客户端地址的方法

### 使用

#### 获取 `SocketAddr`

```rust
ctx.try_get_socket_addr().await;
```

#### 获取 `SocketAddr` 如果失败使用默认值

```rust
ctx.get_socket_addr().await;
```

#### 获取 `SocketAddr` 字符串

```rust
ctx.try_get_socket_addr_string().await;
```

#### 获取 `SocketAddr` 字符串，如果失败使用默认值

```rust
ctx.get_socket_addr_string().await;
```

#### 获取 `SocketHost`

```rust
ctx.try_get_socket_host().await;
```

#### 获取 `SocketPort`

```rust
ctx.try_get_socket_port().await;
```


# Path: ltpp-docs\src\hyperlane\usage-introduction\async.md


> `hyperlane` 框架在 `v3.0.0` 之前不对异步做任何处理，如果需要异步操作，可以引入第三方库
> `hyperlane` 框架在 `v3.0.0` 之后内置异步机制

> `hyperlane` 框架在 `v4.0.0` 之前支持同步和异步中间件/路由共存。
> `hyperlane` 框架在 `v4.0.0` 之后为了性能移除了同步中间件和路由（ `all in async` ），在开启 `keep-alive` 情况下带来了效果 `QPS 10w+`的提升

### 框架本身异步使用

```rust
server.route("/", move |_| async move {
    println!("hello");
}).await;
```

### 下面是使用 `tokio` 库的异步运行时示例代码

#### v4.0.0 之后版本的示例代码

```rust
use hyperlane::*;
use runtime::Runtime;

async fn some_async_task() -> i32 {
    println!("Starting the task...");
    // 模拟异步操作
    tokio::time::sleep(std::time::Duration::from_secs(2)).await;
    println!("Task completed!");
    0
}

#[tokio::main]
async fn main() {
    let server: Server = Server::new().await;
    server.route("/", move |ctx: Context| {
        some_async_task().await;
    });
    server.listen();
}
```

### 异步闭包捕获外部变量

#### 使用 async move

```rust
let test_string: String = "test".to_owned();
server.route("/test/async", move |_| {
    let tmp_test_string = test_string.clone();
    async move {
        println!("{:?}", tmp_test_string);
    }
}).await;
```

#### 使用 future_fn!

```rust
let test_string: String = "test".to_owned();
let func = future_fn!(test_string, |_| {
    println!("async_move => {:?}", test_string);
});
server.route("/test/async", func).await;
```


# Path: ltpp-docs\src\hyperlane\usage-introduction\attribute.md


> `hyperlane` 框架支持临时上下文属性以 `key-value` 形式存储，生命周期贯穿一个完整的请求和响应。
> 存储的 `value` 支持实现了`Any + Send + Sync + Clone` 的 `trait` 的类型。

### 设置某个临时上下文属性

```rust
ctx.set_attribute("key", &"value").await;
```

### 获取某个临时上下文属性

```rust
let value: Option<String> = ctx.try_get_attribute::<String>("key").await;
```

### 移除某个临时上下文属性

```rust
ctx.remove_attribute("key").await;
```

### 清空临时上下文属性

```rust
ctx.clear_attribute().await;
```

### 额外示例

#### 设置闭包

> 闭包需要实现 `Send + Sync` 的 `trait`，否则无法跨线程调用。
> 不推荐 `value` 存储函数，这里只是提供一个示例

```rust
let func: &(dyn Fn(&str) + Send + Sync) = &|msg: &str| {
    println_success!("hyperlane: ", msg);
};
ctx.set_attribute("println_hyperlane", func).await;
let println_hyperlane = ctx
    .get_attribute::<&(dyn Fn(&str) + Send + Sync)>("println_hyperlane")
    .await
    .unwrap();
println_hyperlane("test");
```


# Path: ltpp-docs\src\hyperlane\usage-introduction\connection.md


> `hyperlane` 框架提供了完整的连接状态管理功能，包括连接的中止、关闭状态控制，以及 `Keep-Alive` 连接支持。

## 连接状态管理

### 获取连接状态

```rust
// 是否中止生命周期中的后续流程
let is_aborted: bool = ctx.get_aborted().await;
// 连接是否断开
let is_closed: bool = ctx.get_closed().await;
// 是否停止（等价于is_aborted || is_closed）
let is_terminated: bool = ctx.is_terminated().await;
```

### 设置连接状态

```rust
ctx.set_aborted(true).await;
ctx.set_closed(true).await;
```

### 快捷方法

```rust
// 中止连接
ctx.aborted().await;
// 关闭连接
ctx.closed().await;
// 取消中止
ctx.cancel_aborted().await;
// 取消关闭
ctx.cancel_closed().await;
```

## Keep-Alive 连接

### 检查是否启用 Keep-Alive

```rust
let keep_alive: bool = ctx.is_enable_keep_alive().await;
```

## 基本使用示例

### 连接状态检查

```rust
if ctx.get_closed().await {
    return;
}
```

### 长连接处理

```rust
while !ctx.get_closed().await && !ctx.get_aborted().await {
    let _ = ctx.http_from_stream(8192).await;
    if !ctx.is_enable_keep_alive().await {
        ctx.closed().await;
        break;
    }
}
```


# Path: ltpp-docs\src\hyperlane\usage-introduction\cookie.md


> `hyperlane` 框架提供了完整的 `Cookie` 处理功能，支持请求和响应中的 `Cookie` 操作。

## 请求 Cookie 操作

### 获取所有请求 Cookie

```rust
let cookies: Cookies = ctx.get_request_cookies().await;
```

### 获取特定请求 Cookie

```rust
let cookie_value: OptionCookiesValue = ctx.try_get_request_cookie("session_id").await;
```

> `Cookie` 名称通常是自定义的，所以使用字符串字面量。但对于标准的请求头操作，建议使用框架常量。

## 响应 Cookie 操作

### 获取所有响应 Cookie

```rust
let cookies: Cookies = ctx.get_response_cookies().await;
```

### 获取特定响应 Cookie

```rust
let cookie_value: OptionCookiesValue = ctx.try_get_response_cookie("user_token").await;
```

### 设置响应 Cookie

#### 使用字符串直接设置

```rust
ctx.set_response_header(SET_COOKIE, "session_id=abc123; Path=/; HttpOnly").await;
```

#### 使用 CookieBuilder 构建

```rust
let cookie_value: String = CookieBuilder::new("session_id", "abc123")
    .path("/")
    .http_only()
    .build();
ctx.set_response_header(SET_COOKIE, cookie_value).await;
```

### 设置多个 Cookie

```rust
let session_cookie: String = CookieBuilder::new("session_id", "abc123")
    .path("/")
    .http_only()
    .secure()
    .max_age(3600)
    .build();

let pref_cookie: String = CookieBuilder::new("user_pref", "dark_mode")
    .path("/")
    .max_age(86400)
    .build();

ctx.set_response_header(SET_COOKIE, session_cookie).await
   .set_response_header(SET_COOKIE, pref_cookie).await;
```

## CookieBuilder 方法

### 基本构建

```rust
let cookie: String = CookieBuilder::new("name", "value").build();
```

### 设置属性

```rust
let cookie: String = CookieBuilder::new("session", "token123")
    .expires("Wed, 21 Oct 2025 07:28:00 GMT")
    .max_age(3600)
    .domain("example.com")
    .path("/")
    .secure()
    .http_only()
    .same_site("Strict")
    .build();
```

### 解析现有 Cookie

```rust
let cookie_builder: CookieBuilder = CookieBuilder::parse("name=value; Path=/; HttpOnly");
let rebuilt_cookie: String = cookie_builder.build();
```

## 基本使用示例

### 会话管理

```rust
let session_cookie: String = CookieBuilder::new("session", "token123")
    .http_only()
    .secure()
    .max_age(3600)
    .build();
ctx.set_response_header(SET_COOKIE, session_cookie).await;

if let Some(session) = ctx.get_request_cookie("session").await {}
```

### 清除 Cookie

```rust
let clear_cookie: String = CookieBuilder::new("session", "")
    .max_age(0)
    .build();
ctx.set_response_header(SET_COOKIE, clear_cookie).await;
```


# Path: ltpp-docs\src\hyperlane\usage-introduction\multi-server.md


> `hyperlane` 框架支持多服务模式，仅需创建多个 `server` 实例并进行监听即可

### 多服务

> 启动多个服务，监听多个端口

```rust
let app1 = spawn(async move {
    let config: ServerConfig = ServerConfig::new().await;
    config.host("0.0.0.0").await;
    config.port(80).await;
    let server: Server = Server::from(config).await;
    server.route("/", |ctx: Context| async move {
        let _ = ctx.send_status_body(200, "hello world").await;
    }).await;
    let _ = server.listen().await;
});
let app2 = spawn(async move {
    let config: ServerConfig = ServerConfig::new().await;
    config.host("0.0.0.0").await;
    config.port(81).await;
    let server: Server = Server::from(config).await;
    server.route("/", |ctx: Context| async move {
        let _ = ctx.send_status_body(200, "hello world").await;
    }).await;
    let _ = server.listen().await;
});
let _ = tokio::join!(app1, app2);
```


# Path: ltpp-docs\src\hyperlane\usage-introduction\panic.md


> `hyperlane` 框架对于用户线程 `panic` 会进行捕获并写入错误日志，`hook` 支持发送响应
> 需注意对于一个请求如果在任一中间件环节触发 `panic` 当前请求的后续注册的路由处理函数将不会执行。

### 代码示例

```rust
async fn default_panic_hook(ctx: Context) {
    let error: Panic = ctx.try_get_panic().await.unwrap_or_default();
    let response_body: String = error.to_string();
    let content_type: String = ContentType::format_content_type_with_charset(TEXT_PLAIN, UTF8);
    let _ = ctx
        .set_response_status_code(500)
        .await
        .clear_response_headers()
        .await
        .set_response_header(SERVER, HYPERLANE)
        .await
        .set_response_header(CONTENT_TYPE, content_type)
        .await
        .set_response_body(response_body)
        .await
        .send()
        .await;
}

// 省略 server 创建
server.panic_hook(default_panic_hook);
```


# Path: ltpp-docs\src\hyperlane\usage-introduction\request.md


> `hyperlane` 框架对 `ctx` 额外封装了子字段的方法，可以直接调用大部分子字段的 `get` 和 `set` 方法名称。
> 例如：调用 `request` 上的 `get_method` 方法，
> 一般需要从 `ctx` 解出 `request`，再调用`request.get_method()`，
> 可以简化成直接调用 `ctx.get_request_method().await`。
> **调用规律**
> - `request` 仅支持`get`，不支持`set`，框架保证请求信息不会被意外修改。
> - 原 `request` 的 `get` 方法的 `get` 名称后加 `request` 名称，中间使用\_拼接。

## 获取请求信息

#### 获取 `request`

```rust
let request: Request = ctx.get_request().await;
```

#### 获取 `method`

```rust
let method: RequestMethod = ctx.get_request_method().await;
```

#### 获取 `host`

```rust
let host: RequestHost = ctx.get_request_host().await;
```

#### 获取 `path`

```rust
let path: RequestPath = ctx.get_request_path().await;
```

#### 获取 `version`

```rust
let version: RequestVersion = ctx.get_request_version().await;
```

#### 获取 `querys`

```rust
let querys: RequestQuerys = ctx.get_request_querys().await;
```

#### 获取特定查询参数

```rust
let query_value: OptionRequestQuerysValue = ctx.try_get_request_query("key").await;
```

#### 获取 `header`

> `hyperlane` 框架请求头的 `key` 是经过全小写处理，建议使用框架定义的常量。

```rust
let header: OptionRequestHeadersValue = ctx.try_get_request_header(CONTENT_TYPE).await;
```

#### 获取 `headers`

```rust
let headers: RequestHeaders = ctx.get_request_headers().await;
```

#### 获取请求头的第一个值

```rust
let header_value: OptionRequestHeadersValueItem = ctx.try_get_request_header_front(CONTENT_TYPE).await;
```

#### 获取请求头的最后一个值

```rust
let header_value: OptionRequestHeadersValueItem = ctx.try_get_request_header_back(ACCEPT).await;
```

#### 获取请求头值的数量

```rust
let header_count: usize = ctx.get_request_header_len(ACCEPT_ENCODING).await;
```

#### 获取所有请求头值的总数量

```rust
let total_values: usize = ctx.get_request_headers_values_length().await;
```

#### 获取请求头的数量

```rust
let headers_count: usize = ctx.get_request_headers_length().await;
```

#### 检查是否存在特定请求头

```rust
let has_header: bool = ctx.has_request_header(CONTENT_TYPE).await;
```

#### 检查请求头是否包含特定值

```rust
let has_value: bool = ctx.has_request_header_value(CONTENT_TYPE, APPLICATION_JSON).await;
```

#### 获取请求体

```rust
let body: RequestBody = ctx.get_request_body().await;
```

#### 获取 `string` 格式的请求体

```rust
let body: String = ctx.get_request_body_string().await;
```

#### 获取 `json` 格式的请求体

```rust
let body: T = ctx.get_request_body_json::<T>().await;
```

#### 获取请求升级类型

```rust
let upgrade_type: UpgradeType = ctx.get_request_upgrade_type().await;
```

## 执行闭包操作

#### 使用请求执行异步闭包

```rust
let result = ctx.with_request(|request| async move {
    request.get_method()
}).await;
```

## 转字符串

#### 通过 `to_string`

> 将获得完整的原始结构体字符串结构。

```rust
ctx.get_request().await.to_string();
```

#### 通过 `get_string`

> 将获得简化的结构体字符串结构。

```rust
ctx.get_request().await.get_string();
```

#### 通过 `ctx.get_request_string`

```rust
let request_string: String = ctx.get_request_string().await;
```


# Path: ltpp-docs\src\hyperlane\usage-introduction\response.md


> `hyperlane` 框架没有发送响应前通过 `ctx` 中 `get_response` 获取的只是响应的初始化实例，里面其实没有数据，
> 只有当用户发送响应时才会构建出完整 `http` 响应，此后再次 `get_response` 才能获取到响应内容。

> `hyperlane` 框架对 `ctx` 额外封装了子字段的方法，可以直接调用大部分子字段的 `get` 和 `set` 方法名称，
> 例如：调用 `response` 上的 `get_status_code` 方法。
> **调用规律**
> - 原 `response` 的 `get` 方法的 `get` 名称后加 `response` 名称，中间使用\_拼接。
> - 原 `response` 的 `set` 方法的 `set` 名称后加 `response` 名称，中间使用\_拼接。

### 获取响应

#### 获取 `response`

```rust
let response: Response = ctx.get_response().await;
```

#### 获取响应版本

```rust
let version: ResponseVersion = ctx.get_response_version().await;
```

#### 获取响应状态码

```rust
let status_code: ResponseStatusCode = ctx.get_response_status_code().await;
```

#### 获取响应原因短语

```rust
let reason_phrase: ResponseReasonPhrase = ctx.get_response_reason_phrase().await;
```

#### 获取完整响应头

```rust
let headers: ResponseHeaders = ctx.get_response_headers().await;
```

#### 获取某个响应头

```rust
let value: OptionResponseHeadersValue = ctx.try_get_response_header(CONTENT_TYPE).await;
```

#### 获取响应头的第一个值

```rust
let header_value: OptionResponseHeadersValueItem = ctx.try_get_response_header_front(CONTENT_TYPE).await;
```

#### 获取响应头的最后一个值

```rust
let header_value: OptionResponseHeadersValueItem = ctx.try_get_response_header_back(CONTENT_TYPE).await;
```

#### 检查是否存在特定响应头

```rust
let has_header: bool = ctx.get_response_has_header(CONTENT_TYPE).await;
```

#### 检查响应头是否包含特定值

```rust
let has_value: bool = ctx.has_response_header_value(CONTENT_TYPE, APPLICATION_JSON).await;
```

#### 获取响应头数量

```rust
let headers_count: usize = ctx.get_response_headers_length().await;
```

#### 获取响应头值的数量

```rust
let header_count: usize = ctx.get_response_header_len(CONTENT_TYPE).await;
```

#### 获取所有响应头值的总数量

```rust
let total_values: usize = ctx.get_response_headers_values_length().await;
```

#### 获取响应体

```rust
let body: ResponseBody = ctx.get_response_body().await;
```

#### 获取 `string` 格式的响应体

```rust
let body: String = ctx.get_response_body_string().await;
```

#### 获取 `json` 格式的响应体

```rust
let body: T = ctx.get_response_body_json::<T>().await;
```

#### 获取响应 Cookie

```rust
let cookies: Cookies = ctx.get_response_cookies().await;
```

#### 获取特定响应 Cookie

```rust
let cookie_value: OptionCookiesValue = ctx.try_get_response_cookie("session_id").await;
```

### 设置响应

#### 设置 `response`

```rust
ctx.set_response(Response::default()).await;
```

#### 设置响应版本

> [!warning]
> 特别注意的是需要设置响应版本，框架默认的版本是空字符串，客户端处理会异常。

```rust
ctx.set_response_version(HttpVersion::HTTP1_1).await;
```

#### 设置响应状态码

```rust
ctx.set_response_status_code(200).await;
```

#### 设置响应原因短语

```rust
ctx.set_response_reason_phrase("OK").await;
```

#### 设置响应体

```rust
ctx.set_response_body("Hello World").await;
```

#### 设置（添加）响应头

> `hyperlane` 框架对响应头的 `key` 是不做大小写处理的，建议使用框架定义的常量。

```rust
ctx.add_response_header(SERVER, "hyperlane").await;
```

#### 设置（替换）响应头

```rust
ctx.set_response_header(CONTENT_TYPE, APPLICATION_JSON).await;
```

#### 移除响应头

```rust
ctx.remove_response_header(CONTENT_TYPE).await;
```

#### 移除响应头的特定值

```rust
ctx.remove_response_header_value(CONTENT_TYPE, APPLICATION_JSON).await;
```

#### 清空所有响应头

```rust
ctx.clear_response_headers().await;
```

### 执行闭包操作

#### 使用响应执行异步闭包

```rust
let result = ctx.with_response(|response| async move {
    response.get_status_code()
}).await;
```

### 转字符串

#### 通过 `to_string`

> 将获得完整的原始结构体字符串结构。

```rust
ctx.get_response().await.to_string();
```

#### 通过 `get_string`

> 将获得简化的结构体字符串结构。

```rust
ctx.get_response().await.get_string();
```

#### 通过 `ctx.get_response_string`

```rust
let response_string: String = ctx.get_response_string().await;
```


# Path: ltpp-docs\src\hyperlane\usage-introduction\route.md


## 静态路由

> `hyperlane` 框架支持静态路由（如果重复注册相同的静态路由，框架会抛出异常，程序退出运行），使用方法如下：

### 注册

```rust
server.route("/test", |ctx: Context| {}).await;
```

## 动态路由

> `hyperlane` 框架支持动态路由（如果重复注册相同模式的动态路由，框架会抛出异常，程序退出运行），具体使用方法如下：

### 注册

> 动态路由使用 `{}` 包裹，有两种写法
> - `{key}`内直接些字符串，则将匹配的 `value` 存入 `key` 对应的 `value` 中。
> - `{key:regex}` 则将正则表达式匹配的 `value` 存入 `key` 对应的 `value` 中，如果路径的最后是正则动态路由，则匹配后续所有路径，例如 `/test/{file:^.*$}` 匹配 `/test/a/b/c/d` 会成功，`file` 的 `value` 为 `a/b/c/d`。如果路径的最后不是正则动态路由，则仅使用正则匹配当前段的路由，例如 `/test/{file:^.*$}/b` 匹配 `/test/a/b` 会成功，`file` 的 `value` 为 `a`。

### 朴素动态路由

```rust
server.route("/test/{text}", |ctx: Context| {}).await;
```

### 正则表达式动态路由

```rust
server.route("/test/{number:\\d+}", |ctx: Context| {}).await;
```

### 获取全部动态路由参数

```rust
ctx.get_route_params().await;
```

### 获取某个动态路由参数

```rust
ctx.get_route_param("text").await;
```


# Path: ltpp-docs\src\hyperlane\usage-introduction\send.md


> `hyperlane` 框架提供了多种响应发送方法，支持完整 HTTP 响应发送、仅响应体发送，以及连接管理。
> - `send_with_data`: 发送完整响应并设置响应体。
> - `send_once_with_data`: 发送完整响应并立即关闭连接。
> - `send_body_with_data`: 仅发送响应体并保留连接。
> - `send_body_once_with_data`: 仅发送响应体并立即关闭连接。
> - `send_body_list_with_data`: 批量发送响应体，适用于 WebSocket 等场景。
> - `send_body_list_once_with_data`: 批量发送响应体并立即关闭连接。

## 发送完整 HTTP 响应

### send 方法

> 发送完整的 HTTP 响应，发送后 TCP 连接保留。

```rust
let send_result: ResponseResult = ctx.send().await;
```

### send_once 方法

> 发送完整的 HTTP 响应，发送后立即关闭 TCP 连接。

```rust
let send_result: ResponseResult = ctx.send_once().await;
```

## 发送响应体

### send_body 方法

> 仅发送响应体内容，发送后 TCP 连接保留。适用于流式响应和 WebSocket。

```rust
let send_result: ResponseResult = ctx.send_body().await;
```

### send_once_body 方法

> 仅发送响应体内容，发送后立即关闭 TCP 连接。

```rust
let send_result: ResponseResult = ctx.send_once_body().await;
```

## 发送带数据的响应

### send_with_data 方法

> 发送完整的 HTTP 响应，并将提供的数据作为响应体，发送后 TCP 连接保留。

```rust
let send_result: ResponseResult = ctx.send_with_data("Hello, World!").await;
```

### send_once_with_data 方法

> 发送完整的 HTTP 响应，并将提供的数据作为响应体，发送后立即关闭 TCP 连接。

```rust
let send_result: ResponseResult = ctx.send_once_with_data("Hello, World!").await;
```

### send_body_with_data 方法

> 仅发送响应体内容，并将提供的数据作为响应体，发送后 TCP 连接保留。

```rust
let send_result: ResponseResult = ctx.send_body_with_data("chunk data").await;
```

### send_body_once_with_data 方法

> 仅发送响应体内容，并将提供的数据作为响应体，发送后立即关闭 TCP 连接。

```rust
let send_result: ResponseResult = ctx.send_body_once_with_data("final chunk").await;
```

### send_body_list_with_data 方法

> 批量发送多个响应体数据，适用于 WebSocket 桢列表等场景，发送后 TCP 连接保留。

```rust
let frame_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(&request_body);
ctx.send_body_list_with_data(&frame_list).await.unwrap();
```

### send_body_list_once_with_data 方法

> 批量发送多个响应体数据，发送后立即关闭 TCP 连接。

```rust
let frame_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(&request_body);
ctx.send_body_list_once_with_data(&frame_list).await.unwrap();
```

## 刷新缓冲区

### flush 方法

> 强制刷新网络缓冲区，确保数据立即发送。

```rust
let flush_result: ResponseResult = ctx.flush().await;
```

## 基本使用示例

### 使用框架常量

```rust
ctx.set_response_header(CONTENT_TYPE, APPLICATION_JSON).await
   .set_response_body(r#"{"status": "ok"}"#).await
   .send().await;
```

### 流式发送

```rust
let _ = ctx
    .set_response_header(CONTENT_TYPE, TEXT_EVENT_STREAM)
    .await
    .send()
    .await;
for i in 1..10 {
    let _ = ctx.set_response_body(format!("chunk {}\n", i)).await.send_body().await;
    ctx.flush().await;
}
```

### WebSocket 发送

```rust
pub async fn handle(ctx: Context) {
    while ctx.ws_from_stream(4096).await.is_ok() {
        let request_body: Vec<u8> = ctx.get_request_body().await;
        ctx.set_response_body(&request_body).await;
        let frame_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(&request_body);
        ctx.send_body_list_with_data(&frame_list).await.unwrap();
    }
}
```


# Path: ltpp-docs\src\hyperlane\usage-introduction\sse.md


[GITHUB 地址](https://github.com/hyperlane-dev/hyperlane-quick-start/tree/sse)

> `hyperlane` 框架支持 `sse`，服务端主动推送，下面是每隔 `1s` 完成一次推送，并在 `10` 次后关闭连接。

> `sse` 规范: 服务器使用 `"content-type: text/event-stream"` 表示响应是一个 `sse` 事件流。
> 接着使用 `"data"` 字段来发送事件数据，每个事件以 `"data:"` 开头，后面跟着事件的内容和一个空行。
> 客户端收到这样的响应后，就可以解析其中的事件数据并进行相应的处理。
> 如果开发者非首次响应尝试调用 `send` 会正常发送响应，但是会包含整个 `http` 协议内容，所以对于 `sse`，
> 非首次响应请统一使用 `send_body` 方法。

### 服务端代码

```rust
use crate::{tokio::time::sleep, *};
use std::time::Duration;

pub async fn root(ctx: Context) {
    let _ = ctx
        .set_response_header(CONTENT_TYPE, TEXT_EVENT_STREAM)
        .await
        .set_response_status_code(200)
        .await
        .send()
        .await
        .set_response_version(HttpVersion::HTTP1_1)
        .await;
    for i in 0..10 {
        let _ = ctx
            .set_response_body(format!("data:{}{}", i, HTTP_DOUBLE_BR))
            .await
            .send_body()
            .await;
        sleep(Duration::from_secs(1)).await;
    }
    let _ = ctx.closed().await;
}
```

### 客户端代码

## 客户端代码

#### 断线重连

```js
const eventSource = new EventSource('http://127.0.0.1:60000');

eventSource.onopen = function (event) {
  console.log('Connection opened.');
};

eventSource.onmessage = function (event) {
  const eventData = JSON.parse(event.data);
  console.log('Received event data:', eventData);
};

eventSource.onerror = function (event) {
  if (event.eventPhase === EventSource.CLOSED) {
    console.log('Connection was closed.');
  } else {
    console.error('Error occurred:', event);
  }
};
```

#### 取消断线重连

```js
const eventSource = new EventSource('http://127.0.0.1:60000');

eventSource.onopen = function (event) {
  console.log('Connection opened.');
};

eventSource.onmessage = function (event) {
  const eventData = JSON.parse(event.data);
  console.log('Received event data:', eventData);
};

eventSource.onerror = function (event) {
  if (event.eventPhase === EventSource.CLOSED) {
    console.log('Connection was closed.');
    // 关闭连接，防止自动重连
    eventSource.close();
  } else {
    console.error('Error occurred:', event);
  }
};
```


# Path: ltpp-docs\src\hyperlane\usage-introduction\stream.md


> `hyperlane` 框架接收请求和发送响应均依赖 `stream`，类型是 [`ArcRwLockStream`](../type/stream.md) 需要注意框架提供的 `stream` 仅可读，使用方式如下：

### 获取 `stream`

```rust
let stream_lock: ArcRwLockStream = ctx.get_stream().await.clone().unwrap();
```

### 获取客户端地址

> 完整接口参阅[官方文档](./addr.md)，此处只介绍通过 `stream` 解析使用。

```rust
let socket_addr: String = ctx
    .get_stream()
    .await
    .unwrap()
    .read()
    .await
    .peer_addr()
    .and_then(|host| Ok(host.to_string()))
    .unwrap_or("Unknown".to_owned());
```

### 关闭连接

> 此方法会关闭 `TCP` 连接，不会终止当前的生命周期（当前声明周期结束不会进入下一次生命周期循环，需要重新建立 `TCP` 连接），当前声明周期内的代码正常执行，但是不会再发送响应。

```rust
ctx.closed().await;
```


# Path: ltpp-docs\src\hyperlane\usage-introduction\websocket.md


> `hyperlane` 框架支持 `websocket` 协议，服务端自动处理协议升级，支持请求中间件，路由处理，响应中间件。

### 服务端代码

> `hyperlane` 框架发送 `websocket` 响应使用`send_body`，与 `sse` 相同。
> 由于 `websocket`协议基于`http`，所以可以像使用 `http` 一样处理请求，
> 但是需要注意响应数据需要通过，`WebSocketFrame::create_frame_list` 进行帧处理。
> 如果开发者尝试调用 `send` 会导致客户端处理错误，
> （服务端发送响应前需要处理成符合`websocket` 规范的响应，客户端才能正确解析）。所以对于 `websocket` 响应，
> 请统一使用 `send_body` 或者 `send_body_list_with_data` 方法。

#### 单点发送

> 完整代码参考 [`发送响应`](./send.md) 里 **WebSocket 发送** 部分 。

#### 广播发送

> 需要阻塞住当前处理函数，将后续所有请求在处理函数中处理。
> 这里使用 `tokio` 的 `select` 来处理多个请求，使用 [`hyperlane-broadcast`](../../hyperlane-broadcast/README.md) 来实现广播。

### 客户端代码

```js
const ws = new WebSocket('ws://localhost:60000/websocket');

ws.onopen = () => {
  console.log('WebSocket opened');
  setInterval(() => {
    ws.send(`Now time: ${new Date().toISOString()}`);
  }, 1000);
};

ws.onmessage = (event) => {
  console.log('Receive: ', event.data);
};

ws.onerror = (error) => {
  console.error('WebSocket error: ', error);
};

ws.onclose = () => {
  console.log('WebSocket closed');
};
```


# Path: ltpp-docs\src\hyperlane\utils\inner-utils.md


## http-constant

> `hyperlane` 框架使用了 `http-constant` 库（框架已内置，无需额外安装和导入），
> 使用参考 [官方文档](../../http-constant/README.md)。

## http-compress

> `hyperlane` 框架使用了 `http-compress` 库（框架已内置，无需额外安装和导入），
> 使用参考 [官方文档](../../http-compress/README.md)。

## http-type

> `hyperlane` 框架使用了 `http-type` 库（框架已内置，无需额外安装和导入），
> 使用参考 [官方文档](../../http-type/README.md)。


# Path: ltpp-docs\src\hyperlane\utils\recommend-utils.md


## hyperlane-utils

> `hyperlane` 框架推荐使用 `hyperlane-utils` 库（需额外安装和导入），
> 使用参考 [官方文档](../../hyperlane-utils/README.md)。

## lombok

> `hyperlane` 框架推荐使用 `lombok` 库（需额外安装和导入），
> 使用参考 [官方文档](../../lombok-macros/README.md)。

## clonelicious

> `hyperlane` 框架推荐使用 `clonelicious` 库，内部提供变量捕获和克隆（需额外安装和导入），
> 使用参考 [官方文档](../../clonelicious/README.md)。

## future-fn

> `hyperlane` 框架推荐使用 `future-fn` 库（需额外安装和导入），
> 使用参考 [官方文档](../../future-fn/README.md)。

## std-macro-extensions

> `hyperlane` 框架推荐使用 `std-macro-extensions` 库（需额外安装和导入），
> 使用参考 [官方文档](../../std-macro-extensions/README.md)。

## color-output

> `hyperlane` 框架推荐使用 `color-output` 库（需额外安装和导入），
> 使用参考 [官方文档](../../color-output/README.md)。

## bin-encode-decode

> `hyperlane` 框架推荐使用 `bin-encode-decode` 库（需额外安装和导入），
> 使用参考 [官方文档](../../bin-encode-decode/README.md)。

## file-operation

> `hyperlane` 框架推荐使用 `file-operation` 库（需额外安装和导入），
> 使用参考 [官方文档](../../file-operation/README.md)。

## compare-version

> `hyperlane` 框架推荐使用 `compare-version` 库（需额外安装和导入），
> 使用参考 [官方文档](../../compare-version/README.md)。

## hyperlane-log

> `hyperlane` 框架使用 `hyperlane-log` 库（需额外安装和导入），
> 使用参考 [官方文档](../../hyperlane-log/README.md)。

## hyperlane-time

> `hyperlane` 框架推荐使用 `hyperlane-time` 库（需额外安装和导入），
> 使用参考 [官方文档](../../hyperlane-time/README.md)。

## recoverable-spawn

> `hyperlane` 框架推荐使用 `recoverable-spawn` 库（需额外安装和导入），
> 使用参考 [官方文档](../../recoverable-spawn/README.md)。

## recoverable-thread-pool

> `hyperlane` 框架推荐使用 `recoverable-thread-pool` 库（需额外安装和导入），
> 使用参考 [官方文档](../../recoverable-thread-pool/README.md)。

## http-request

> `hyperlane` 框架推荐使用 `http-request` 库，支持 `http` 和 `https`（需额外安装和导入），
> 使用参考 [官方文档](../../http-request/README.md)。

## hyperlane-broadcast

> `hyperlane` 框架推荐使用 `hyperlane-broadcast` 库（需额外安装和导入），
> 使用参考 [官方文档](../../hyperlane-broadcast/README.md)。

## hyperlane-plugin-websocket

> `hyperlane` 框架推荐使用 `hyperlane-plugin-websocket` 库（需额外安装和导入），
> 使用参考 [官方文档](../../hyperlane-plugin-websocket/README.md)。

## urlencoding

> `hyperlane` 框架推荐使用 `urlencoding` 库（需额外安装和导入），可以实现 `url` 编解码。

## server-manager

> `hyperlane` 框架推荐使用 `server-manager` 库（需额外安装和导入），
> 使用参考 [官方文档](../../server-manager/README.md)。

## chunkify

> `hyperlane` 框架推荐使用 `chunkify` 库（需额外安装和导入），
> 使用参考 [官方文档](../../chunkify/README.md)。

## china_identification_card

> `hyperlane` 框架推荐使用 `china_identification_card` 库（需额外安装和导入），
> 使用参考 [官方文档](../../china-identification-card/README.md)。

## utoipa

> `hyperlane` 框架推荐使用 `utoipa` 库实现 `openapi`，下面是一段简单的示例代码

```rust
use hyperlane::*;
use serde::Serialize;
use serde_json;
use utoipa::{OpenApi, ToSchema};
use utoipa_rapidoc::RapiDoc;
use utoipa_swagger_ui::SwaggerUi;

#[derive(Serialize, ToSchema)]
struct User {
    name: String,
    age: usize,
}

#[derive(OpenApi)]
#[openapi(
    components(schemas(User)),
    info(title = "Hyperlane", version = "1.0.0"),
    paths(index, user, openapi_json, swagger)
)]
struct ApiDoc;

async fn request_middleware(ctx: Context) {
    ctx.set_response_version(HttpVersion::HTTP1_1)
        .await
        .set_response_status_code(200).await;
}

#[utoipa::path(
    get,
    path = "/openapi.json",
    responses(
        (status = 200, description = "Openapi docs", body = String)
    )
)]
async fn openapi_json(ctx: Context) {
    ctx.set_response_body(ApiDoc::openapi().to_json().unwrap())
        .await
        .send()
        .await
        .unwrap();
}

#[utoipa::path(
    get,
    path = "/{file}",
    responses(
        (status = 200, description = "Openapi json", body = String)
    )
)]
async fn swagger(ctx: Context) {
    SwaggerUi::new("/{file}").url("/openapi.json", ApiDoc::openapi());
    let res: String = RapiDoc::with_openapi("/openapi.json", ApiDoc::openapi()).to_html();
    ctx.set_response_header(CONTENT_TYPE, TEXT_HTML)
        .await
        .set_response_body(res)
        .await
        .send()
        .await
        .unwrap();
}

#[utoipa::path(
    get,
    path = "/",
    responses(
        (status = 302, description = "Redirect to index.html")
    )
)]
async fn index(ctx: Context) {
    ctx.set_response_header(LOCATION, "/index.html")
        .await
        .set_response_body(vec![])
        .await
        .send()
        .await
        .unwrap();
}

#[utoipa::path(
    get,
    path = "/user/{name}",
    responses(
        (status = 200, description = "User", body = User)
    )
)]
async fn user(ctx: Context) {
    let name: String = ctx.get_route_param("name").await.unwrap();
    let user: User = User { name, age: 0 };
    ctx.set_response_body(serde_json::to_vec(&user).unwrap())
        .await
        .send()
        .await
        .unwrap();
}

#[tokio::main]
async fn main() {
    let server: Server = Server::new().await;
    server.request_middleware(request_middleware).await;
    server.route("/", index).await;
    server.route("/user/{name}", user).await;
    server.route("/openapi.json", openapi_json).await;
    server.route("/{file}", swagger).await;
    server.run().await.unwrap();
}
```


# Path: ltpp-docs\src\hyperlane-ai\README.md


[GITHUB 地址](https://github.com/hyperlane-dev/hyperlane-ai)

## 项目概述

该流水线包括以下步骤：

1. 使用 Python 虚拟环境进行环境设置
2. 安装依赖项
3. 数据集生成
4. 使用 LoRA 适配器进行模型微调
5. 将 LoRA 适配器与基础模型合并
6. 将合并后的模型转换为 GGUF 格式
7. 分析训练参数

## 先决条件

- Python 3.8 或更高版本
- pip (Python 包安装器)
- Git

## 设置和使用

### 1. 克隆仓库

```bash
git clone <repository-url>
cd hyperlane-ai-training
```

### 2. 运行训练流水线

执行主脚本来运行完整的流水线：

```bash
./run.sh
```

这将：

- 创建并激活 Python 虚拟环境
- 安装所有必需的依赖项
- 生成数据集
- 微调模型
- 将 LoRA 适配器与基础模型合并
- 将合并后的模型转换为 GGUF 格式
- 分析训练参数

### 3. 开发模式

为了在开发过程中更快地迭代，您可以运行开发模式的流水线，该模式限制训练步数：

```bash
./run.sh dev
```

## 配置

项目可以使用根目录中的 `.env` 文件进行配置。以下环境变量可用：

- `MERGED_MODEL_DIR`: 合并模型的目录 (默认: "merged_model")
- `OUTPUT_DIR`: 输出文件的目录 (默认: "output")

示例 `.env` 文件：

```
MERGED_MODEL_DIR=my_merged_model
OUTPUT_DIR=my_output
```

## 项目结构

- `run.sh`: 主执行脚本
- `generate_markdown.py`: 生成训练数据集的脚本
- `finetune.py`: 模型微调脚本
- `merge_model.py`: 将 LoRA 适配器与基础模型合并的脚本
- `convert_hf_to_gguf.py`: 将模型转换为 GGUF 格式的脚本
- `analyze_training_args.py`: 分析和记录训练参数的脚本
- `dataset/`: 包含训练数据集的目录

## 依赖项

项目需要以下 Python 包：

- torch (>=2.3.0)
- transformers
- datasets
- trl
- peft
- accelerate
- hf_xet
- gguf
- mistral_common
- dotenv

## 输出

成功执行后，最终的 GGUF 模型将位于: `$OUTPUT_DIR/$OUTPUT_DIR.gguf`


# Path: ltpp-docs\src\hyperlane-broadcast\README.md


[GITHUB 地址](https://github.com/hyperlane-dev/hyperlane-broadcast)

[API 文档](https://docs.rs/hyperlane-broadcast/latest/hyperlane_broadcast/)

> hyperlane-broadcast 是对 Tokio 广播通道的一个轻量级且符合人体工程学的封装，旨在为异步 Rust 应用程序提供易于使用的发布-订阅消息传递。它通过提供一个直接的接口，以最少的样板代码向多个订阅者广播消息，

## 安装方式

你可以使用如下命令添加依赖：

```shell
cargo add hyperlane-broadcast
```

## 使用示例

```rust
use hyperlane_broadcast::*;

let broadcast: Broadcast<usize> = Broadcast::new(10);
let mut rec1: BroadcastReceiver<usize> = broadcast.subscribe();
let mut rec2: BroadcastReceiver<usize> = broadcast.subscribe();
broadcast.send(20).unwrap();
assert_eq!(rec1.recv().await, Ok(20));
assert_eq!(rec2.recv().await, Ok(20));

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
```

## 开源协议


# Path: ltpp-docs\src\hyperlane-log\README.md


[GITHUB 地址](https://github.com/hyperlane-dev/hyperlane-log)

[API 文档](https://docs.rs/hyperlane-log/latest/hyperlane_log/)

> 一个支持异步和同步日志记录的 Rust 日志库。它提供多个日志级别，如错误、信息和调试。用户可以定义自定义的日志处理方法并配置日志文件路径。该库支持日志轮换，当当前文件达到指定的大小限制时，会自动创建一个新的日志文件。它允许灵活的日志配置，使其既适用于高性能的异步应用程序，也适用于传统的同步日志记录场景。异步模式利用 Tokio 的异步通道进行高效的日志缓冲，而同步模式则直接将日志写入文件系统。

## 安装

要使用此库，您可以运行以下命令：

```shell
cargo add hyperlane-log
```

## 日志存储位置说明

> 会在用户指定的目录下生成三个目录，分别对应错误日志目录，信息日志目录，调试日志目录，这三个目录下还有一级目录使用日期命名，此目录下的日志文件命名是时间.下标.log

## 使用同步

```rust
use hyperlane_log::*;

let log: Log = Log::new("./logs", 1_024_000);
log.error("error data!", |error| {
    let write_data: String = format!("User error func => {:?}\n", error);
    write_data
});
log.error(String::from("error data!"), |error| {
    let write_data: String = format!("User error func => {:?}\n", error);
    write_data
});
log.info("info data!", |info| {
    let write_data: String = format!("User info func => {:?}\n", info);
    write_data
});
log.info(String::from("info data!"), |info| {
    let write_data: String = format!("User info func => {:?}\n", info);
    write_data
});
log.debug("debug data!", |debug| {
    let write_data: String = format!("User debug func => {:#?}\n", debug);
    write_data
});
log.debug(String::from("debug data!"), |debug| {
    let write_data: String = format!("User debug func => {:#?}\n", debug);
    write_data
});
```

## 使用异步

```rust
use hyperlane_log::*;

let log: Log = Log::new("./logs", 1_024_000);
log.async_error("async error data!", |error| {
    let write_data: String = format!("User error func => {:?}\n", error);
    write_data
}).await;
log.async_error(String::from("async error data!"), |error| {
    let write_data: String = format!("User error func => {:?}\n", error);
    write_data
}).await;
log.async_info("async info data!", |info| {
    let write_data: String = format!("User info func => {:?}\n", info);
    write_data
}).await;
log.async_info(String::from("async info data!"), |info| {
    let write_data: String = format!("User info func => {:?}\n", info);
    write_data
}).await;
log.async_debug("async debug data!", |debug| {
    let write_data: String = format!("User debug func => {:#?}\n", debug);
    write_data
}).await;
log.async_debug(String::from("async debug data!"), |debug| {
    let write_data: String = format!("User debug func => {:#?}\n", debug);
    write_data
}).await;
```

## 禁用日志

```rust
let log: Log = Log::new("./logs", DISABLE_LOG_FILE_SIZE);
```


# Path: ltpp-docs\src\hyperlane-macros\README.md


[GITHUB 地址](https://github.com/hyperlane-dev/hyperlane-macros)

[API 文档](https://docs.rs/hyperlane-macros/latest/hyperlane_macros/)

> 一个用于构建具有增强功能的 HTTP 服务器的综合性过程宏集合。该 crate 提供了属性宏，可简化 HTTP 请求处理、协议验证、响应管理和请求数据提取。

## 安装

要使用此 crate，您可以运行 cmd：

```shell
cargo add hyperlane-macros
```

## 可用宏

### Hyperlane 宏

- `#[hyperlane(server: Server)]` - 使用指定的变量名和类型创建新的 `Server` 实例，并自动注册 crate 内定义的其他钩子和路由。
- `#[hyperlane(config: ServerConfig)]` - 使用指定的变量名和类型创建新的 `ServerConfig` 实例。

### HTTP 方法宏

- `#[methods(method1, method2, ...)]` - 接受多个 HTTP 方法
- `#[get]` - GET 方法处理器
- `#[post]` - POST 方法处理器
- `#[put]` - PUT 方法处理器
- `#[delete]` - DELETE 方法处理器
- `#[patch]` - PATCH 方法处理器
- `#[head]` - HEAD 方法处理器
- `#[options]` - OPTIONS 方法处理器
- `#[connect]` - CONNECT 方法处理器
- `#[trace]` - TRACE 方法处理器

### 协议检查宏

- `#[ws]` - WebSocket 检查，确保函数仅在 WebSocket 升级请求时执行
- `#[http]` - HTTP 检查，确保函数仅在标准 HTTP 请求时执行
- `#[h2c]` - HTTP/2 明文检查，确保函数仅在 HTTP/2 明文请求时执行
- `#[http0_9]` - HTTP/0.9 检查，确保函数仅在 HTTP/0.9 协议请求时执行
- `#[http1_0]` - HTTP/1.0 检查，确保函数仅在 HTTP/1.0 协议请求时执行
- `#[http1_1]` - HTTP/1.1 检查，确保函数仅在 HTTP/1.1 协议请求时执行
- `#[http1_1_or_higher]` - HTTP/1.1 或更高版本检查，确保函数仅在 HTTP/1.1 或更新版本协议请求时执行
- `#[http2]` - HTTP/2 检查，确保函数仅在 HTTP/2 协议请求时执行
- `#[http3]` - HTTP/3 检查，确保函数仅在 HTTP/3 协议请求时执行
- `#[tls]` - TLS 检查，确保函数仅在 TLS 加密连接时执行

### 响应设置宏

- `#[response_status_code(code)]` - 设置响应状态码（支持字面量和全局常量）
- `#[response_reason_phrase("phrase")]` - 设置响应原因短语（支持字面量和全局常量）
- `#[response_header("key", "value")]` - 添加响应头（支持字面量和全局常量）
- `#[response_header("key" => "value")]` - 设置响应头（支持字面量和全局常量）
- `#[response_body("data")]` - 设置响应体（支持字面量和全局常量）
- `#[response_version(version)]` - 设置响应 HTTP 版本（支持字面量和全局常量）

### 发送操作宏

- `#[send]` - 函数执行后发送完整响应（包含头部和主体）
- `#[send_body]` - 函数执行后仅发送响应体
- `#[send_once]` - 函数执行后仅发送一次完整响应
- `#[send_body_once]` - 函数执行后仅发送一次响应体
- `#[send_with_data("data")]` - 函数执行后使用指定数据发送完整响应
- `#[send_once_with_data("data")]` - 函数执行后使用指定数据仅发送一次完整响应
- `#[send_body_with_data("data")]` - 函数执行后使用指定数据仅发送响应体

### 刷新宏

- `#[flush]` - 函数执行后刷新响应流，确保数据立即传输

### 中止宏

- `#[aborted]` - 处理中止的请求，为提前终止的连接提供清理逻辑

### 关闭操作宏

- `#[closed]` - 处理关闭的流，为已完成的连接提供清理逻辑

### 条件宏

- `#[filter(condition)]` - 仅当 `condition`（返回布尔值的代码块）为 `true` 时继续执行。
- `#[reject(condition)]` - 仅当 `condition`（返回布尔值的代码块）为 `false` 时继续执行。

### 请求体宏

- `#[request_body(variable_name)]` - 将原始请求体提取到指定变量中，类型为 RequestBody
- `#[request_body_json(variable_name: type)]` - 将请求体作为 JSON 解析到指定变量和类型中

### 属性宏

- `#[attribute(key => variable_name: type)]` - 通过键将特定属性提取到类型化变量中

### 属性宏集合

- `#[attributes(variable_name)]` - 将所有属性作为 HashMap 获取，用于全面的属性访问

### 路由参数宏

- `#[route_param(key => variable_name)]` - 通过键将特定路由参数提取到变量中

### 路由参数集合宏

- `#[route_params(variable_name)]` - 将所有路由参数作为集合获取

### 请求查询宏

- `#[request_query(key => variable_name)]` - 从 URL 查询字符串中通过键提取特定查询参数

### 请求查询集合宏

- `#[request_querys(variable_name)]` - 将所有查询参数作为集合获取

### 请求头宏

- `#[request_header(key => variable_name)]` - 从请求中通过名称提取特定的 HTTP 头

### 请求头集合宏

- `#[request_headers(variable_name)]` - 将所有 HTTP 头作为集合获取

### 请求 Cookie 宏

- `#[request_cookie(key => variable_name)]` - 从请求 Cookie 头中通过键提取特定的 Cookie 值

### 请求 Cookies 集合宏

- `#[request_cookies(variable_name)]` - 从 Cookie 头中将所有 Cookies 作为原始字符串获取

### 请求版本宏

- `#[request_version(variable_name)]` - 将 HTTP 请求版本提取到变量中

### 请求路径宏

- `#[request_path(variable_name)]` - 将 HTTP 请求路径提取到变量中

### 主机宏

- `#[host("hostname")]` - 限制函数仅在具有特定主机头值的请求时执行
- `#[reject_host("hostname")]` - 拒绝匹配特定主机头值的请求

### Referer 宏

- `#[referer("url")]` - 限制函数仅在具有特定 referer 头值的请求时执行
- `#[reject_referer("url")]` - 拒绝匹配特定 referer 头值的请求

### 钩子宏

- `#[prologue_hook(function_name)]` - 在主处理函数之前执行指定函数
- `#[epilogue_hook(function_name)]` - 在主处理函数之后执行指定函数
- `#[panic_hook]` - 当服务器内发生 panic 时执行函数
- `#[prologue_hooks(macro1, macro2, ...)]` - 在被装饰函数之前注入一系列宏。
- `#[epilogue_hooks(macro1, macro2, ...)]` - 在被装饰函数之后注入一系列宏。

### 中间件宏

- `#[request_middleware]` - 将函数注册为请求中间件
- `#[request_middleware(order)]` - 将函数注册为具有指定顺序的请求中间件
- `#[response_middleware]` - 将函数注册为响应中间件
- `#[response_middleware(order)]` - 将函数注册为具有指定顺序的响应中间件
- `#[panic_hook]` - 将函数注册为 panic 钩子
- `#[panic_hook(order)]` - 将函数注册为具有指定顺序的 panic 钩子

### 流处理宏

- `#[http_from_stream]` - 使用默认缓冲区大小包装函数体进行 HTTP 流处理。仅当成功从 HTTP 流读取数据时，函数体才会执行。
- `#[http_from_stream(buffer_size)]` - 使用指定缓冲区大小包装函数体进行 HTTP 流处理。
- `#[http_from_stream(variable_name)]` - 包装函数体进行 HTTP 流处理，将数据存储在指定变量名中。
- `#[http_from_stream(buffer_size, variable_name)]` - 使用指定缓冲区大小和变量名包装函数体进行 HTTP 流处理。
- `#[http_from_stream(variable_name, buffer_size)]` - 使用指定变量名和缓冲区大小（顺序相反）包装函数体进行 HTTP 流处理。
- `#[ws_from_stream]` - 使用默认缓冲区大小包装函数体进行 WebSocket 流处理。仅当成功从 WebSocket 流读取数据时，函数体才会执行。
- `#[ws_from_stream(buffer_size)]` - 使用指定缓冲区大小包装函数体进行 WebSocket 流处理。
- `#[ws_from_stream(variable_name)]` - 包装函数体进行 WebSocket 流处理，将数据存储在指定变量名中。
- `#[ws_from_stream(buffer_size, variable_name)]` - 使用指定缓冲区大小和变量名包装函数体进行 WebSocket 流处理。
- `#[ws_from_stream(variable_name, buffer_size)]` - 使用指定变量名和缓冲区大小（顺序相反）包装函数体进行 WebSocket 流处理。

### 响应头宏

### 响应体宏

### 路由宏

- `#[route("path")]` - 使用默认服务器为给定路径注册路由处理器（前提：需要 `#[hyperlane(server: Server)]` 宏）

### 辅助提示

- **请求相关宏**（数据提取）使用 **`get`** 操作 - 它们从请求中检索/查询数据
- **响应相关宏**（数据设置）使用 **`set`** 操作 - 它们分配/配置响应数据
- **钩子宏** 对于支持 `order` 参数的钩子相关宏，如果未指定 `order`，则该钩子的优先级高于指定了 `order` 的钩子（仅适用于 `#[request_middleware]`、`#[response_middleware]`、`#[panic_hook]` 等宏）

### 最佳实践警告

- 请求相关宏主要是查询函数，而响应相关宏主要是赋值函数。
- 使用 `prologue_hook` 或 `epilogue_hook` 宏时，不建议将它们与其他宏（如 `#[get]`、`#[post]`、`#[http]` 等）组合在同一函数上。这些宏应放置在钩子函数本身中。如果您不清楚宏是如何展开的，组合它们可能会导致有问题的代码行为。

## 示例用法

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

#[panic_hook]
#[panic_hook(1)]
#[panic_hook("2")]
#[epilogue_hooks(response_body("panic_hook"), send)]
async fn panic_hook(ctx: Context) {}

#[request_middleware]
#[epilogue_hooks(
    response_status_code(200),
    response_version(HttpVersion::HTTP1_1),
    response_header(SERVER => HYPERLANE),
    response_header(CONNECTION => KEEP_ALIVE),
    response_header(CONTENT_TYPE => TEXT_PLAIN),
    response_header(ACCESS_CONTROL_ALLOW_ORIGIN => WILDCARD_ANY),
    response_header(STEP => "request_middleware"),
)]
async fn request_middleware(ctx: Context) {}

#[ws]
#[request_middleware(1)]
#[epilogue_hooks(
    response_body(&vec![]),
    response_status_code(101),
    response_header(UPGRADE => WEBSOCKET),
    response_header(CONNECTION => UPGRADE),
    response_header(SEC_WEBSOCKET_ACCEPT => &WebSocketFrame::generate_accept_key(&ctx.try_get_request_header_back(SEC_WEBSOCKET_KEY).await.unwrap())),
    response_header(STEP => "upgrade_hook"),
    send
)]
async fn upgrade_hook(ctx: Context) {}

#[request_middleware(2)]
#[response_status_code(200)]
#[response_header(SERVER => HYPERLANE)]
#[response_version(HttpVersion::HTTP1_1)]
#[response_header(ACCESS_CONTROL_ALLOW_ORIGIN => WILDCARD_ANY)]
#[response_header(STEP => "connected_hook")]
async fn connected_hook(ctx: Context) {}

#[response_middleware]
#[response_header(STEP => "response_middleware_1")]
async fn response_middleware_1(ctx: Context) {}

#[response_middleware(2)]
#[prologue_hooks(
    reject(ctx.get_request().await.is_ws()),
    response_header(STEP => "response_middleware_2")
)]
#[epilogue_hooks(send, flush)]
async fn response_middleware_2(ctx: Context) {}

#[response_middleware("3")]
#[prologue_hooks(
    ws,
    response_header(STEP => "response_middleware_3")
)]
#[epilogue_hooks(send_body, flush)]
async fn response_middleware_3(ctx: Context) {}

#[get]
#[http]
async fn prologue_hook(ctx: Context) {}

#[response_status_code(200)]
async fn epilogue_hook(ctx: Context) {}

#[route("/response")]
#[response_body(&RESPONSE_DATA)]
#[response_reason_phrase(CUSTOM_REASON)]
#[response_status_code(CUSTOM_STATUS_CODE)]
#[response_header(CUSTOM_HEADER_NAME => CUSTOM_HEADER_VALUE)]
async fn response(ctx: Context) {}

#[route("/connect")]
#[prologue_hooks(connect, response_body("connect"))]
async fn connect(ctx: Context) {}

#[route("/delete")]
#[prologue_hooks(delete, response_body("delete"))]
async fn delete(ctx: Context) {}

#[route("/head")]
#[prologue_hooks(head, response_body("head"))]
async fn head(ctx: Context) {}

#[route("/options")]
#[prologue_hooks(options, response_body("options"))]
async fn options(ctx: Context) {}

#[route("/patch")]
#[prologue_hooks(patch, response_body("patch"))]
async fn patch(ctx: Context) {}

#[route("/put")]
#[prologue_hooks(put, response_body("put"))]
async fn put(ctx: Context) {}

#[route("/trace")]
#[prologue_hooks(trace, response_body("trace"))]
async fn trace(ctx: Context) {}

#[route("/h2c")]
#[prologue_hooks(h2c, response_body("h2c"))]
async fn h2c(ctx: Context) {}

#[route("/http")]
#[prologue_hooks(http, response_body("http"))]
async fn http_only(ctx: Context) {}

#[route("/http0_9")]
#[prologue_hooks(http0_9, response_body("http0_9"))]
async fn http0_9(ctx: Context) {}

#[route("/http1_0")]
#[prologue_hooks(http1_0, response_body("http1_0"))]
async fn http1_0(ctx: Context) {}

#[route("/http1_1")]
#[prologue_hooks(http1_1, response_body("http1_1"))]
async fn http1_1(ctx: Context) {}

#[route("/http2")]
#[prologue_hooks(http2, response_body("http2"))]
async fn http2(ctx: Context) {}

#[route("/http3")]
#[prologue_hooks(http3, response_body("http3"))]
async fn http3(ctx: Context) {}

#[route("/tls")]
#[prologue_hooks(tls, response_body("tls"))]
async fn tls(ctx: Context) {}

#[route("/http1_1_or_higher")]
#[prologue_hooks(http1_1_or_higher, response_body("http1_1_or_higher"))]
async fn http1_1_or_higher(ctx: Context) {}

#[route("/unknown_method")]
#[prologue_hooks(
    filter(ctx.get_request().await.is_unknown_method()),
    response_body("unknown_method")
)]
async fn unknown_method(ctx: Context) {}

#[route("/get")]
#[send_body_once]
#[prologue_hooks(ws, get, response_body("get"))]
async fn get(ctx: Context) {}

#[send_once]
#[route("/post")]
#[prologue_hooks(post, response_body("post"))]
async fn post(ctx: Context) {}

#[ws]
#[route("/ws1")]
#[ws_from_stream]
async fn websocket_1(ctx: Context) {
    let body: RequestBody = ctx.get_request_body().await;
    let body_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(&body);
    ctx.send_body_list_with_data(&body_list).await.unwrap();
}

#[ws]
#[route("/ws2")]
#[ws_from_stream(1024)]
async fn websocket_2(ctx: Context) {
    let body: RequestBody = ctx.get_request_body().await;
    let body_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(&body);
    ctx.send_body_list_with_data(&body_list).await.unwrap();
}

#[ws]
#[route("/ws3")]
#[ws_from_stream(request)]
async fn websocket_3(ctx: Context) {
    let body: RequestBody = request.get_body().clone();
    let body_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(&body);
    ctx.send_body_list_with_data(&body_list).await.unwrap();
}

#[ws]
#[route("/ws4")]
#[ws_from_stream(1024, request)]
async fn websocket_4(ctx: Context) {
    let body: RequestBody = request.get_body().clone();
    let body_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(&body);
    ctx.send_body_list_with_data(&body_list).await.unwrap();
}

#[ws]
#[route("/ws5")]
#[ws_from_stream(request, 1024)]
async fn websocket_5(ctx: Context) {
    let body: RequestBody = request.get_body().clone();
    let body_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(&body);
    ctx.send_body_list_with_data(&body_list).await.unwrap();
}

#[route("/hook")]
#[prologue_hook(prologue_hook)]
#[epilogue_hook(epilogue_hook)]
#[response_body("Testing hook macro")]
async fn hook(ctx: Context) {}

#[closed]
#[route("/get_post")]
#[prologue_hooks(
    http,
    methods(get, post),
    response_body("get_post"),
    response_status_code(200),
    response_reason_phrase("OK")
)]
async fn get_post(ctx: Context) {}

#[route("/attributes")]
#[response_body(&format!("request attributes: {request_attributes:?}"))]
#[attributes(request_attributes)]
async fn attributes(ctx: Context) {}

#[route("/route_params/:test")]
#[response_body(&format!("request route params: {request_route_params:?}"))]
#[route_params(request_route_params)]
async fn route_params(ctx: Context) {}

#[route("/route_param/:test")]
#[response_body(&format!("route param: {request_route_param:?}"))]
#[route_param("test" => request_route_param)]
async fn route_param(ctx: Context) {}

#[route("/host")]
#[host("localhost")]
#[epilogue_hooks(
    response_body("host string literal: localhost"),
    send,
    http_from_stream
)]
#[prologue_hooks(response_body("host string literal: localhost"), send)]
async fn host(ctx: Context) {}

#[route("/request_query")]
#[epilogue_hooks(
    request_query("test" => request_query_option),
    response_body(&format!("request query: {request_query_option:?}")),
    send,
    http_from_stream(1024)
)]
#[prologue_hooks(
    request_query("test" => request_query_option),
    response_body(&format!("request query: {request_query_option:?}")),
    send
)]
async fn request_query(ctx: Context) {}

#[route("/request_header")]
#[epilogue_hooks(
    request_header(HOST => request_header_option),
    response_body(&format!("request header: {request_header_option:?}")),
    send,
    http_from_stream(_request)
)]
#[prologue_hooks(
    request_header(HOST => request_header_option),
    response_body(&format!("request header: {request_header_option:?}")),
    send
)]
async fn request_header(ctx: Context) {}

#[route("/request_querys")]
#[epilogue_hooks(
    request_querys(request_querys),
    response_body(&format!("request querys: {request_querys:?}")),
    send,
    http_from_stream(1024, _request)
)]
#[prologue_hooks(
    request_querys(request_querys),
    response_body(&format!("request querys: {request_querys:?}")),
    send
)]
async fn request_querys(ctx: Context) {}

#[route("/request_headers")]
#[epilogue_hooks(
    request_headers(request_headers),
    response_body(&format!("request headers: {request_headers:?}")),
    send,
    http_from_stream(_request, 1024)
)]
#[prologue_hooks(
    request_headers(request_headers),
    response_body(&format!("request headers: {request_headers:?}")),
    send
)]
async fn request_headers(ctx: Context) {}

#[response_body(&format!("raw body: {raw_body:?}"))]
#[request_body(raw_body)]
#[route("/request_body")]
async fn request_body(ctx: Context) {}

#[route("/reject_host")]
#[prologue_hooks(
    reject_host("filter.localhost"),
    response_body("host filter string literal")
)]
async fn reject_host(ctx: Context) {}

#[route("/attribute")]
#[response_body(&format!("request attribute: {request_attribute_option:?}"))]
#[attribute(TEST_ATTRIBUTE_KEY => request_attribute_option: TestData)]
async fn attribute(ctx: Context) {}

#[route("/request_body_json")]
#[response_body(&format!("request data: {request_data_result:?}"))]
#[request_body_json(request_data_result: TestData)]
async fn request_body_json(ctx: Context) {}

#[route("/referer")]
#[prologue_hooks(
    referer("http://localhost"),
    response_body("referer string literal: http://localhost")
)]
async fn referer(ctx: Context) {}

#[route("/reject_referer")]
#[prologue_hooks(
    reject_referer("http://localhost"),
    response_body("referer filter string literal")
)]
async fn reject_referer(ctx: Context) {}

#[route("/cookies")]
#[response_body(&format!("All cookies: {cookie_value:?}"))]
#[request_cookies(cookie_value)]
async fn cookies(ctx: Context) {}

#[route("/cookie")]
#[response_body(&format!("Session cookie: {session_cookie_opt:?}"))]
#[request_cookie("test" => session_cookie_opt)]
async fn cookie(ctx: Context) {}

#[route("/request_version")]
#[response_body(&format!("HTTP Version: {http_version}"))]
#[request_version(http_version)]
async fn request_version_test(ctx: Context) {}

#[route("/request_path")]
#[response_body(&format!("Request Path: {request_path}"))]
#[request_path(request_path)]
async fn request_path_test(ctx: Context) {}

#[route("/response_header")]
#[response_body("Testing header set and replace operations")]
#[response_header("X-Add-Header", "add-value")]
#[response_header("X-Set-Header" => "set-value")]
async fn response_header_test(ctx: Context) {}

#[route("/literals")]
#[response_status_code(201)]
#[response_header(CONTENT_TYPE => APPLICATION_JSON)]
#[response_body("{\"message\": \"Resource created\"}")]
#[response_reason_phrase(HttpStatus::Created.to_string())]
async fn literals(ctx: Context) {}

#[hyperlane(server: Server)]
#[hyperlane(config: ServerConfig)]
#[tokio::main]
async fn main() {
    config.disable_nodelay().await;
    server.config(config).await;
    let server_hook: ServerHook = server.run().await.unwrap_or_default();
    server_hook.wait().await;
}
```


# Path: ltpp-docs\src\hyperlane-plugin-websocket\README.md


[GITHUB 地址](https://github.com/hyperlane-dev/hyperlane-plugin-websocket)

[API 文档](https://docs.rs/hyperlane-plugin-websocket/latest/hyperlane_plugin_websocket/)

> Hyperlane 框架的 WebSocket 插件，提供强大的 WebSocket 通信功能，并与 hyperlane-broadcast 集成以实现高效的消息传播。

## 安装

使用以下命令添加此依赖：

```shell
cargo add hyperlane-plugin-websocket
```

## 使用示例

```rust
use hyperlane::*;

async fn send_body_hook(ctx: Context) {
    let body: ResponseBody = ctx.get_response_body().await;
    if ctx.get_request().await.is_ws() {
        let frame_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(&body);
        ctx.send_body_list_with_data(&frame_list).await.unwrap();
    } else {
        ctx.send_body().await.unwrap();
    }
}

async fn request_middleware(ctx: Context) {
    ctx.set_send_body_hook(send_body_hook).await;
    let socket_addr: String = ctx.get_socket_addr_string().await;
    ctx.set_response_version(HttpVersion::HTTP1_1)
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
        .set_response_header("SocketAddr", &socket_addr)
        .await;
}

async fn upgrade_hook(ctx: Context) {
    if !ctx.get_request().await.is_ws() {
        return;
    }
    if let Some(key) = &ctx.try_get_request_header_back(SEC_WEBSOCKET_KEY).await {
        let accept_key: String = WebSocketFrame::generate_accept_key(key);
        ctx.set_response_status_code(101)
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
            .await
            .unwrap();
    }
}

async fn response_middleware(ctx: Context) {
    if ctx.get_request().await.is_ws() {
        return;
    }
    let _ = ctx.send().await;
}

async fn root_route(ctx: Context) {
    let path: RequestPath = ctx.get_request_path().await;
    let response_body: String = format!("Hello hyperlane => {}", path);
    let cookie1: String = CookieBuilder::new("key1", "value1").http_only().build();
    let cookie2: String = CookieBuilder::new("key2", "value2").http_only().build();
    ctx.add_response_header(SET_COOKIE, &cookie1)
        .await
        .add_response_header(SET_COOKIE, &cookie2)
        .await
        .set_response_body(&response_body)
        .await;
}

async fn ws_route(ctx: Context) {
    if let Some(send_body_hook) = ctx.try_get_send_body_hook().await {
        while ctx.ws_from_stream(4096).await.is_ok() {
            let request_body: Vec<u8> = ctx.get_request_body().await;
            ctx.set_response_body(&request_body).await;
            send_body_hook(ctx.clone()).await;
        }
    }
}

async fn sse_route(ctx: Context) {
    let _ = ctx
        .set_response_header(CONTENT_TYPE, TEXT_EVENT_STREAM)
        .await
        .send()
        .await;
    for i in 0..10 {
        let _ = ctx
            .set_response_body(&format!("data:{}{}", i, HTTP_DOUBLE_BR))
            .await
            .send_body()
            .await;
    }
    let _ = ctx.closed().await;
}

async fn dynamic_route(ctx: Context) {
    let param: RouteParams = ctx.get_route_params().await;
    panic!("Test panic {:?}", param);
}

async fn panic_hook(ctx: Context) {
    let error: Panic = ctx.try_get_panic().await.unwrap_or_default();
    let response_body: String = error.to_string();
    let content_type: String = ContentType::format_content_type_with_charset(TEXT_PLAIN, UTF8);
    let _ = ctx
        .set_response_status_code(500)
        .await
        .clear_response_headers()
        .await
        .set_response_header(SERVER, HYPERLANE)
        .await
        .set_response_header(CONTENT_TYPE, &content_type)
        .await
        .set_response_body(&response_body)
        .await
        .send()
        .await;
}

#[tokio::main]
async fn main() {
    let config: ServerConfig = ServerConfig::new().await;
    config.host("0.0.0.0").await;
    config.port(60000).await;
    config.buffer(4096).await;
    config.disable_linger().await;
    config.disable_nodelay().await;
    let server: Server = Server::from(config).await;
    server.panic_hook(panic_hook).await;
    server.request_middleware(request_middleware).await;
    server.request_middleware(upgrade_hook).await;
    server.response_middleware(response_middleware).await;
    server.route("/", root_route).await;
    server.route("/ws", ws_route).await;
    server.route("/sse", sse_route).await;
    server.route("/dynamic/{routing}", dynamic_route).await;
    server.route("/regex/{file:^.*$}", dynamic_route).await;
    let server_hook: ServerHook = server.run().await.unwrap_or_default();
    server_hook.wait().await;
}
```


# Path: ltpp-docs\src\hyperlane-time\README.md


[GITHUB 地址](https://github.com/hyperlane-dev/hyperlane-time)

[API 文档](https://docs.rs/hyperlane-time/latest/hyperlane_time/)

> 一个根据系统区域设置获取当前时间的库。

## 安装

要使用这个库，你可以运行以下命令：

```shell
cargo add hyperlane-time
```

## 使用

```rust
use hyperlane_time::*;

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
```


# Path: ltpp-docs\src\hyperlane-utils\README.md


[GITHUB 地址](https://github.com/hyperlane-dev/hyperlane-utils)

[API 文档](https://docs.rs/hyperlane-utils/latest/hyperlane_utils/)

> 一个为 hyperlane 提供工具的库。

## 安装

您可以使用以下命令安装该 crate：

```shell
cargo add hyperlane-utils
```

## 使用方式

```rust
use hyperlane_utils::*;
```


