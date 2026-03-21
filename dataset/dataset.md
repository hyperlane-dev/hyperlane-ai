<!--2026-03-21 13:00:13-->
# Path: hyperlane/README.md
## hyperlane
[Official Documentation](https://docs.ltpp.vip/hyperlane/)
[Api Docs](https://docs.rs/hyperlane/latest/)
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
pub use {attribute::*, config::*, context::*, error::*, hook::*, panic::*, route::*, server::*};
pub use {http_type::*, inventory};
#[cfg(test)]
use std::time::{Duration, Instant};
use std::{
    any::Any,
    cmp::Ordering,
    collections::{HashMap, HashSet},
    future::Future,
    hash::{Hash, Hasher},
    io::{self, Write, stderr, stdout},
    pin::Pin,
    sync::{Arc, OnceLock},
};
#[cfg(test)]
use tokio::time::sleep;
use {
    inventory::collect,
    lombok_macros::*,
    regex::Regex,
    serde::{Deserialize, Serialize},
    tokio::{
        net::{TcpListener, TcpStream},
        spawn,
        sync::watch::{Receiver, Sender, channel},
        task::{JoinError, JoinHandle},
    },
};
```
# Path: hyperlane/src/context/mod.rs
```rust
mod r#impl;
mod r#struct;
#[cfg(test)]
mod test;
pub use r#struct::*;
```
# Path: hyperlane/src/context/impl.rs
```rust
use crate::*;
impl Default for Context {
    #[inline(always)]
    fn default() -> Self {
        Self {
            aborted: false,
            closed: false,
            stream: None,
            request: Request::default(),
            response: Response::default(),
            route_params: RouteParams::default(),
            attributes: ThreadSafeAttributeStore::default(),
            server: default_server(),
        }
    }
}
impl PartialEq for Context {
    #[inline(always)]
    fn eq(&self, other: &Self) -> bool {
        self.get_aborted() == other.get_aborted()
            && self.get_closed() == other.get_closed()
            && self.get_request() == other.get_request()
            && self.get_response() == other.get_response()
            && self.get_route_params() == other.get_route_params()
            && self.get_attributes().len() == other.get_attributes().len()
            && self.try_get_stream().is_some() == other.try_get_stream().is_some()
            && self.get_server() == other.get_server()
    }
}
impl Eq for Context {}
impl From<&'static Server> for Context {
    #[inline(always)]
    fn from(server: &'static Server) -> Self {
        let mut ctx: Context = Context::default();
        ctx.set_server(server);
        ctx
    }
}
impl From<&ArcRwLockStream> for Context {
    #[inline(always)]
    fn from(stream: &ArcRwLockStream) -> Self {
        let mut ctx: Context = Context::default();
        ctx.set_stream(Some(stream.clone()));
        ctx
    }
}
impl From<ArcRwLockStream> for Context {
    #[inline(always)]
    fn from(stream: ArcRwLockStream) -> Self {
        (&stream).into()
    }
}
impl From<usize> for Context {
    #[inline(always)]
    fn from(addr: usize) -> Self {
        let ctx: &Context = addr.into();
        ctx.clone()
    }
}
impl From<usize> for &'static Context {
    #[inline(always)]
    fn from(addr: usize) -> &'static Context {
        unsafe { &*(addr as *const Context) }
    }
}
impl<'a> From<usize> for &'a mut Context {
    #[inline(always)]
    fn from(addr: usize) -> &'a mut Context {
        unsafe { &mut *(addr as *mut Context) }
    }
}
impl From<&Context> for usize {
    #[inline(always)]
    fn from(ctx: &Context) -> Self {
        ctx as *const Context as usize
    }
}
impl From<&mut Context> for usize {
    #[inline(always)]
    fn from(ctx: &mut Context) -> Self {
        ctx as *mut Context as usize
    }
}
impl AsRef<Context> for Context {
    #[inline(always)]
    fn as_ref(&self) -> &Context {
        let addr: usize = (self as &Context).into();
        addr.into()
    }
}
impl AsMut<Context> for Context {
    #[inline(always)]
    fn as_mut(&mut self) -> &mut Context {
        let addr: usize = (self as &mut Context).into();
        addr.into()
    }
}
impl Context {
    #[inline(always)]
    pub(crate) fn new(
        stream: &ArcRwLockStream,
        request: &Request,
        server: &'static Server,
    ) -> Context {
        let mut ctx: Context = Context::default();
        ctx.set_stream(Some(stream.clone()))
            .set_request(request.clone())
            .set_server(server)
            .get_mut_response()
            .set_version(request.get_version().clone());
        ctx
    }
    pub async fn http_from_stream(&mut self) -> Result<Request, RequestError> {
        if self.get_aborted() {
            return Err(RequestError::RequestAborted(HttpStatus::BadRequest));
        }
        if let Some(stream) = self.try_get_stream() {
            let request_res: Result<Request, RequestError> =
                Request::http_from_stream(stream, self.get_server().get_request_config()).await;
            if let Ok(request) = request_res.as_ref() {
                self.set_request(request.clone());
            }
            return request_res;
        };
        Err(RequestError::GetTcpStream(HttpStatus::BadRequest))
    }
    pub async fn ws_from_stream(&mut self) -> Result<Request, RequestError> {
        if self.get_aborted() {
            return Err(RequestError::RequestAborted(HttpStatus::BadRequest));
        }
        if let Some(stream) = self.try_get_stream() {
            let last_request: &Request = self.get_request();
            let request_res: Result<Request, RequestError> = last_request
                .ws_from_stream(stream, self.get_server().get_request_config())
                .await;
            match request_res.as_ref() {
                Ok(request) => {
                    self.set_request(request.clone());
                }
                Err(_) => {
                    self.set_request(last_request.clone());
                }
            }
            return request_res;
        };
        Err(RequestError::GetTcpStream(HttpStatus::BadRequest))
    }
    #[inline(always)]
    pub fn is_terminated(&self) -> bool {
        self.get_aborted() || self.get_closed()
    }
    #[inline(always)]
    pub(crate) fn is_keep_alive(&self, keep_alive: bool) -> bool {
        !self.get_closed() && keep_alive
    }
    #[inline(always)]
    pub fn try_get_route_param<T>(&self, name: T) -> Option<String>
    where
        T: AsRef<str>,
    {
        self.get_route_params().get(name.as_ref()).cloned()
    }
    #[inline(always)]
    pub fn get_route_param<T>(&self, name: T) -> String
    where
        T: AsRef<str>,
    {
        self.try_get_route_param(name).unwrap()
    }
    #[inline(always)]
    pub fn try_get_attribute<V>(&self, key: impl AsRef<str>) -> Option<V>
    where
        V: AnySendSyncClone,
    {
        self.get_attributes()
            .get(&Attribute::External(key.as_ref().to_owned()).to_string())
            .and_then(|arc| arc.downcast_ref::<V>())
            .cloned()
    }
    #[inline(always)]
    pub fn get_attribute<V>(&self, key: impl AsRef<str>) -> V
    where
        V: AnySendSyncClone,
    {
        self.try_get_attribute(key).unwrap()
    }
    #[inline(always)]
    pub fn set_attribute<K, V>(&mut self, key: K, value: V) -> &mut Self
    where
        K: AsRef<str>,
        V: AnySendSyncClone,
    {
        self.get_mut_attributes().insert(
            Attribute::External(key.as_ref().to_owned()).to_string(),
            Arc::new(value),
        );
        self
    }
    #[inline(always)]
    pub fn remove_attribute<K>(&mut self, key: K) -> &mut Self
    where
        K: AsRef<str>,
    {
        self.get_mut_attributes()
            .remove(&Attribute::External(key.as_ref().to_owned()).to_string());
        self
    }
    #[inline(always)]
    pub fn clear_attribute(&mut self) -> &mut Self {
        self.get_mut_attributes().clear();
        self
    }
    #[inline(always)]
    fn try_get_internal_attribute<V>(&self, key: InternalAttribute) -> Option<V>
    where
        V: AnySendSyncClone,
    {
        self.get_attributes()
            .get(&Attribute::Internal(key).to_string())
            .and_then(|arc| arc.downcast_ref::<V>())
            .cloned()
    }
    #[inline(always)]
    fn get_internal_attribute<V>(&self, key: InternalAttribute) -> V
    where
        V: AnySendSyncClone,
    {
        self.try_get_internal_attribute(key).unwrap()
    }
    #[inline(always)]
    fn set_internal_attribute<V>(&mut self, key: InternalAttribute, value: V) -> &mut Self
    where
        V: AnySendSyncClone,
    {
        self.get_mut_attributes()
            .insert(Attribute::Internal(key).to_string(), Arc::new(value));
        self
    }
    #[inline(always)]
    pub(crate) fn set_task_panic(&mut self, panic_data: PanicData) -> &mut Self {
        self.set_internal_attribute(InternalAttribute::TaskPanicData, panic_data)
    }
    #[inline(always)]
    pub fn try_get_task_panic_data(&self) -> Option<PanicData> {
        self.try_get_internal_attribute(InternalAttribute::TaskPanicData)
    }
    #[inline(always)]
    pub fn get_task_panic_data(&self) -> PanicData {
        self.get_internal_attribute(InternalAttribute::TaskPanicData)
    }
    #[inline(always)]
    pub(crate) fn set_request_error_data(&mut self, request_error: RequestError) -> &mut Self {
        self.set_internal_attribute(InternalAttribute::RequestErrorData, request_error)
    }
    #[inline(always)]
    pub fn try_get_request_error_data(&self) -> Option<RequestError> {
        self.try_get_internal_attribute(InternalAttribute::RequestErrorData)
    }
    #[inline(always)]
    pub fn get_request_error_data(&self) -> RequestError {
        self.get_internal_attribute(InternalAttribute::RequestErrorData)
    }
    pub async fn try_send(&mut self) -> Result<(), ResponseError> {
        if self.is_terminated() {
            return Err(ResponseError::Terminated);
        }
        let response_data: ResponseData = self.get_mut_response().build();
        if let Some(stream) = self.try_get_stream() {
            return stream.try_send(response_data).await;
        }
        Err(ResponseError::NotFoundStream)
    }
    pub async fn send(&mut self) {
        self.try_send().await.unwrap();
    }
    pub async fn try_send_body(&self) -> Result<(), ResponseError> {
        if self.is_terminated() {
            return Err(ResponseError::Terminated);
        }
        self.try_send_body_with_data(self.get_response().get_body())
            .await
    }
    pub async fn send_body(&self) {
        self.try_send_body().await.unwrap();
    }
    pub async fn try_send_body_with_data<D>(&self, data: D) -> Result<(), ResponseError>
    where
        D: AsRef<[u8]>,
    {
        if self.is_terminated() {
            return Err(ResponseError::Terminated);
        }
        if let Some(stream) = self.try_get_stream() {
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
        if self.is_terminated() {
            return Err(ResponseError::Terminated);
        }
        if let Some(stream) = self.try_get_stream() {
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
        if self.is_terminated() {
            return Err(ResponseError::Terminated);
        }
        if let Some(stream) = self.try_get_stream() {
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
        if self.is_terminated() {
            return Err(ResponseError::Terminated);
        }
        if let Some(stream) = self.try_get_stream() {
            return stream.try_flush().await;
        }
        Err(ResponseError::NotFoundStream)
    }
    pub async fn flush(&self) {
        self.try_flush().await.unwrap();
    }
}
```
# Path: hyperlane/src/context/struct.rs
```rust
use crate::*;
#[derive(Clone, CustomDebug, Data, DisplayDebug)]
pub struct Context {
    #[get(type(copy))]
    pub(super) aborted: bool,
    #[get(type(copy))]
    pub(super) closed: bool,
    #[get_mut(skip)]
    #[set(pub(super))]
    pub(super) stream: Option<ArcRwLockStream>,
    #[get_mut(skip)]
    #[set(pub(super))]
    pub(super) request: Request,
    pub(super) response: Response,
    #[get_mut(skip)]
    #[set(pub(crate))]
    pub(super) route_params: RouteParams,
    #[get_mut(pub(super))]
    #[set(pub(super))]
    pub(super) attributes: ThreadSafeAttributeStore,
    #[get_mut(skip)]
    #[set(pub(super))]
    pub(super) server: &'static Server,
}
```
# Path: hyperlane/src/context/test.rs
```rust
use crate::*;
#[test]
fn context_from_usize() {
    let mut ctx: Context = Context::default();
    ctx.set_aborted(true);
    let ctx_address: usize = (&ctx).into();
    let ctx_from_addr: Context = ctx_address.into();
    assert_eq!(ctx.get_aborted(), ctx_from_addr.get_aborted());
}
#[test]
fn context_ref_from_usize() {
    let mut ctx: Context = Context::default();
    ctx.set_closed(true);
    let ctx_address: usize = (&ctx).into();
    let ctx_ref: &Context = ctx_address.into();
    assert_eq!(ctx.get_closed(), ctx_ref.get_closed());
}
#[test]
fn context_mut_from_usize() {
    let mut ctx: Context = Context::default();
    let ctx_address: usize = (&mut ctx).into();
    let ctx_mut: &mut Context = ctx_address.into();
    ctx_mut.set_aborted(true);
    assert!(ctx_mut.get_aborted());
}
#[test]
fn context_ref_into_usize() {
    let ctx: Context = Context::default();
    let ctx_address: usize = (&ctx).into();
    assert!(ctx_address > 0);
}
#[test]
fn context_mut_into_usize() {
    let mut ctx: Context = Context::default();
    let ctx_address: usize = (&mut ctx).into();
    assert!(ctx_address > 0);
}
#[test]
fn context_aborted_and_closed() {
    let mut ctx: Context = Context::default();
    assert!(!ctx.get_aborted());
    ctx.set_aborted(true);
    assert!(ctx.get_aborted());
    ctx.set_aborted(false);
    assert!(!ctx.get_aborted());
    assert!(!ctx.get_closed());
    ctx.set_closed(true);
    assert!(ctx.get_closed());
    ctx.set_closed(false);
    assert!(!ctx.get_closed());
    assert!(!ctx.is_terminated());
    ctx.set_aborted(true);
    assert!(ctx.is_terminated());
    ctx.set_aborted(false);
    ctx.set_closed(true);
    assert!(ctx.is_terminated());
}
#[test]
fn context_route_params() {
    let mut ctx: Context = Context::default();
    let mut params: RouteParams = RouteParams::default();
    params.insert("id".to_string(), "123".to_string());
    ctx.set_route_params(params);
    let id: Option<String> = ctx.try_get_route_param("id");
    assert_eq!(id, Some("123".to_string()));
    let name: Option<String> = ctx.try_get_route_param("name");
    assert_eq!(name, None);
}
#[test]
fn context_request_and_response_string() {
    let mut ctx: Context = Context::default();
    let request: Request = Request::default();
    ctx.set_request(request.clone());
    let fetched_request: &Request = ctx.get_request();
    assert_eq!(request.to_string(), fetched_request.to_string());
    let response: Response = Response::default();
    ctx.set_response(response.clone());
    let fetched_response: &Response = ctx.get_response();
    assert_eq!(response.to_string(), fetched_response.to_string());
}
#[test]
fn context_as_ref() {
    let ctx: Context = Context::default();
    let ctx_ref: &Context = ctx.as_ref();
    assert_eq!(ctx.get_aborted(), ctx_ref.get_aborted());
    assert_eq!(ctx.get_closed(), ctx_ref.get_closed());
    assert_eq!(ctx.get_request(), ctx_ref.get_request());
    assert_eq!(ctx.get_response(), ctx_ref.get_response());
}
#[test]
fn context_as_mut() {
    let mut ctx: Context = Context::default();
    ctx.set_aborted(true);
    let ctx_mut: &mut Context = ctx.as_mut();
    assert!(ctx_mut.get_aborted());
    ctx_mut.set_closed(true);
    assert!(ctx.get_closed());
}
```
# Path: hyperlane/src/panic/mod.rs
```rust
mod r#impl;
mod r#struct;
#[cfg(test)]
mod test;
pub use r#struct::*;
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
# Path: hyperlane/src/panic/struct.rs
```rust
use crate::*;
#[derive(
    Clone, CustomDebug, Default, Deserialize, DisplayDebug, Eq, Getter, PartialEq, Serialize, Setter,
)]
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
# Path: hyperlane/src/panic/test.rs
```rust
use crate::*;
#[test]
fn panic_new() {
    let panic: PanicData = PanicData::new(
        Some("message".to_string()),
        Some("location".to_string()),
        Some("payload".to_string()),
    );
    assert_eq!(panic.try_get_message(), &Some("message".to_string()));
    assert_eq!(panic.try_get_location(), &Some("location".to_string()));
    assert_eq!(panic.try_get_payload(), &Some("payload".to_string()));
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
            .try_get_message()
            .clone()
            .unwrap_or_default()
            .contains("test panic");
        assert!(is_panic);
    }
}
```
# Path: hyperlane/src/hook/trait.rs
```rust
use crate::*;
pub trait FnContext<R>: Fn(&mut Context) -> R + Send + Sync {}
pub trait FnContextPinBox<T>: FnContext<FutureBox<T>> {}
pub trait FnContextStatic<Fut, T>: FnContext<Fut> + 'static
where
    Fut: Future<Output = T> + Send,
{
}
```
# Path: hyperlane/src/hook/mod.rs
```rust
mod r#enum;
mod r#fn;
mod r#impl;
mod r#struct;
mod r#trait;
mod r#type;
pub use {r#enum::*, r#fn::*, r#struct::*, r#trait::*, r#type::*};
```
# Path: hyperlane/src/hook/fn.rs
```rust
use crate::*;
#[inline(always)]
pub fn default_server_control_hook_handler() -> ServerControlHookHandler<()> {
    Arc::new(|| Box::pin(async {}))
}
#[inline(always)]
pub fn default_server_hook_handler() -> ServerHookHandler {
    Arc::new(|_: &mut Context| -> FutureBox<()> { Box::pin(async move {}) })
}
#[inline(always)]
pub fn server_hook_factory<R>() -> ServerHookHandler
where
    R: ServerHook,
{
    Arc::new(move |ctx: &mut Context| -> FutureBox<()> {
        let ctx_address: usize = ctx.into();
        Box::pin(async move {
            let ctx: &mut Context = ctx_address.into();
            R::new(ctx).await.handle(ctx).await;
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
impl<F, R> FnContext<R> for F where F: Fn(&mut Context) -> R + Send + Sync {}
impl<F, T> FnContextPinBox<T> for F where F: FnContext<FutureBox<T>> {}
impl<F, Fut, T> FnContextStatic<Fut, T> for F
where
    F: FnContext<Fut> + 'static,
    Fut: Future<Output = T> + Send,
{
}
impl<T, R> FutureSendStatic<R> for T where T: Future<Output = R> + Send + 'static {}
impl<T, O> FutureSend<O> for T where T: Future<Output = O> + Send {}
impl<T, O> FutureFn<O> for T where T: Fn() -> FutureBox<O> + Send + Sync {}
impl Default for ServerControlHook {
    #[inline(always)]
    fn default() -> Self {
        Self {
            wait_hook: default_server_control_hook_handler(),
            shutdown_hook: default_server_control_hook_handler(),
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
    #[inline]
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
    async fn new(_: &mut Context) -> Self {
        Self
    }
    async fn handle(self, _: &mut Context) {}
}
```
# Path: hyperlane/src/hook/struct.rs
```rust
use crate::*;
#[derive(
    Clone, Copy, Debug, Deserialize, DisplayDebug, Eq, Hash, Ord, PartialEq, PartialOrd, Serialize,
)]
pub struct DefaultServerHook;
#[derive(Clone, CustomDebug, DisplayDebug, Getter, Setter)]
pub struct ServerControlHook {
    #[debug(skip)]
    #[get(pub)]
    #[set(pub(crate))]
    pub(super) wait_hook: ServerControlHookHandler<()>,
    #[debug(skip)]
    #[get(pub)]
    #[set(pub(crate))]
    pub(super) shutdown_hook: ServerControlHookHandler<()>,
}
```
# Path: hyperlane/src/hook/type.rs
```rust
use crate::*;
pub type HookHandler<T> = Arc<dyn FnContextPinBox<T>>;
pub type HookHandlerChain<T> = Vec<HookHandler<T>>;
pub type AsyncTask = Pin<Box<dyn Future<Output = ()> + Send + 'static>>;
pub type FutureBox<T> = Pin<Box<dyn Future<Output = T> + Send>>;
pub type ServerControlHookHandler<T> = Arc<dyn FutureFn<T>>;
pub type ServerHookHandlerFactory = fn() -> ServerHookHandler;
pub type ServerHookHandler = Arc<dyn Fn(&mut Context) -> FutureBox<()> + Send + Sync>;
pub type ServerHookList = Vec<ServerHookHandler>;
pub type ServerHookMap = HashMapXxHash3_64<String, ServerHookHandler>;
pub type ServerHookPatternRoute = HashMapXxHash3_64<usize, Vec<(RoutePattern, ServerHookHandler)>>;
```
# Path: hyperlane/src/hook/enum.rs
```rust
use crate::*;
#[derive(Clone, Copy, Debug, DisplayDebug)]
pub enum HookType {
    TaskPanic(Option<isize>, ServerHookHandlerFactory),
    RequestError(Option<isize>, ServerHookHandlerFactory),
    RequestMiddleware(Option<isize>, ServerHookHandlerFactory),
    Route(&'static str, ServerHookHandlerFactory),
    ResponseMiddleware(Option<isize>, ServerHookHandlerFactory),
}
```
# Path: hyperlane/src/config/mod.rs
```rust
mod r#impl;
mod r#struct;
#[cfg(test)]
mod test;
pub use r#struct::*;
```
# Path: hyperlane/src/config/impl.rs
```rust
use crate::*;
impl Default for ServerConfig {
    #[inline(always)]
    fn default() -> Self {
        Self {
            address: Server::format_bind_address(DEFAULT_HOST, DEFAULT_WEB_PORT),
            nodelay: DEFAULT_NODELAY,
            ttl: DEFAULT_TTI,
        }
    }
}
impl ServerConfig {
    pub fn from_json<C>(json: C) -> Result<Self, serde_json::Error>
    where
        C: AsRef<str>,
    {
        serde_json::from_str(json.as_ref())
    }
}
```
# Path: hyperlane/src/config/struct.rs
```rust
use crate::*;
#[derive(Clone, CustomDebug, Data, Deserialize, DisplayDebug, Eq, New, PartialEq, Serialize)]
pub struct ServerConfig {
    #[set(type(AsRef<str>))]
    pub(super) address: String,
    pub(super) nodelay: Option<bool>,
    pub(super) ttl: Option<u32>,
}
```
# Path: hyperlane/src/config/test.rs
```rust
use crate::*;
#[test]
fn server_config_from_json() {
    let server_config_json: &'static str = r#"
    {
        "address": "0.0.0.0:80",
        "nodelay": true,
        "ttl": 64
    }
    "#;
    let server_config: ServerConfig = ServerConfig::from_json(server_config_json).unwrap();
    let mut new_server_config: ServerConfig = ServerConfig::default();
    new_server_config
        .set_address("0.0.0.0:80")
        .set_nodelay(Some(true))
        .set_ttl(Some(64));
    assert_eq!(server_config, new_server_config);
}
```
# Path: hyperlane/src/server/mod.rs
```rust
mod r#fn;
mod r#impl;
mod r#struct;
#[cfg(test)]
mod test;
mod r#type;
pub use {r#struct::*, r#type::*};
pub(crate) use r#fn::*;
```
# Path: hyperlane/src/server/fn.rs
```rust
use crate::*;
pub(crate) fn default_server() -> &'static Server {
    static DEFAULT_SERVER: OnceLock<Server> = OnceLock::new();
    DEFAULT_SERVER.get_or_init(Server::default)
}
```
# Path: hyperlane/src/server/impl.rs
```rust
use crate::*;
impl Default for Server {
    #[inline(always)]
    fn default() -> Self {
        Self {
            server_config: ServerConfig::default(),
            request_config: RequestConfig::default(),
            task_panic: vec![],
            request_error: vec![],
            route_matcher: RouteMatcher::new(),
            request_middleware: vec![],
            response_middleware: vec![],
        }
    }
}
impl PartialEq for Server {
    #[inline]
    fn eq(&self, other: &Self) -> bool {
        self.get_server_config() == other.get_server_config()
            && self.get_request_config() == other.get_request_config()
            && self.get_route_matcher() == other.get_route_matcher()
            && self.get_task_panic().len() == other.get_task_panic().len()
            && self.get_request_error().len() == other.get_request_error().len()
            && self.get_request_middleware().len() == other.get_request_middleware().len()
            && self.get_response_middleware().len() == other.get_response_middleware().len()
            && self
                .get_task_panic()
                .iter()
                .zip(other.get_task_panic().iter())
                .all(|(a, b)| Arc::ptr_eq(a, b))
            && self
                .get_request_error()
                .iter()
                .zip(other.get_request_error().iter())
                .all(|(a, b)| Arc::ptr_eq(a, b))
            && self
                .get_request_middleware()
                .iter()
                .zip(other.get_request_middleware().iter())
                .all(|(a, b)| Arc::ptr_eq(a, b))
            && self
                .get_response_middleware()
                .iter()
                .zip(other.get_response_middleware().iter())
                .all(|(a, b)| Arc::ptr_eq(a, b))
    }
}
impl Eq for Server {}
impl From<usize> for Server {
    #[inline(always)]
    fn from(addr: usize) -> Self {
        let server: &Server = addr.into();
        server.clone()
    }
}
impl From<usize> for &'static Server {
    #[inline(always)]
    fn from(addr: usize) -> &'static Server {
        unsafe { &*(addr as *const Server) }
    }
}
impl From<usize> for &'static mut Server {
    #[inline(always)]
    fn from(addr: usize) -> &'static mut Server {
        unsafe { &mut *(addr as *mut Server) }
    }
}
impl From<&Server> for usize {
    #[inline(always)]
    fn from(server: &Server) -> Self {
        server as *const Server as usize
    }
}
impl From<&mut Server> for usize {
    #[inline(always)]
    fn from(server: &mut Server) -> Self {
        server as *mut Server as usize
    }
}
impl AsRef<Server> for Server {
    #[inline(always)]
    fn as_ref(&self) -> &Server {
        let addr: usize = (self as &Server).into();
        addr.into()
    }
}
impl AsMut<Server> for Server {
    #[inline(always)]
    fn as_mut(&mut self) -> &mut Server {
        let addr: usize = (self as &mut Server).into();
        addr.into()
    }
}
impl From<ServerConfig> for Server {
    #[inline(always)]
    fn from(server_config: ServerConfig) -> Self {
        Self {
            server_config,
            ..Default::default()
        }
    }
}
impl From<RequestConfig> for Server {
    #[inline(always)]
    fn from(request_config: RequestConfig) -> Self {
        Self {
            request_config,
            ..Default::default()
        }
    }
}
impl Server {
    #[inline]
    pub fn handle_hook(&mut self, hook: HookType) {
        match hook {
            HookType::TaskPanic(_, hook) => {
                self.get_mut_task_panic().push(hook());
            }
            HookType::RequestError(_, hook) => {
                self.get_mut_request_error().push(hook());
            }
            HookType::RequestMiddleware(_, hook) => {
                self.get_mut_request_middleware().push(hook());
            }
            HookType::Route(path, hook) => {
                self.get_mut_route_matcher().add(path, hook()).unwrap();
            }
            HookType::ResponseMiddleware(_, hook) => {
                self.get_mut_response_middleware().push(hook());
            }
        };
    }
    #[inline]
    pub fn config_from_json<C>(&mut self, json: C) -> &mut Self
    where
        C: AsRef<str>,
    {
        let config: ServerConfig = serde_json::from_str(json.as_ref()).unwrap();
        self.set_server_config(config);
        self
    }
    #[inline(always)]
    pub fn server_config(&mut self, config: ServerConfig) -> &mut Self {
        self.set_server_config(config);
        self
    }
    #[inline(always)]
    pub fn request_config(&mut self, config: RequestConfig) -> &mut Self {
        self.set_request_config(config);
        self
    }
    #[inline(always)]
    pub fn task_panic<S>(&mut self) -> &mut Self
    where
        S: ServerHook,
    {
        self.get_mut_task_panic().push(server_hook_factory::<S>());
        self
    }
    #[inline(always)]
    pub fn request_error<S>(&mut self) -> &mut Self
    where
        S: ServerHook,
    {
        self.get_mut_request_error()
            .push(server_hook_factory::<S>());
        self
    }
    #[inline(always)]
    pub fn route<S>(&mut self, path: impl AsRef<str>) -> &mut Self
    where
        S: ServerHook,
    {
        self.get_mut_route_matcher()
            .add(path.as_ref(), server_hook_factory::<S>())
            .unwrap();
        self
    }
    #[inline(always)]
    pub fn request_middleware<S>(&mut self) -> &mut Self
    where
        S: ServerHook,
    {
        self.get_mut_request_middleware()
            .push(server_hook_factory::<S>());
        self
    }
    #[inline(always)]
    pub fn response_middleware<S>(&mut self) -> &mut Self
    where
        S: ServerHook,
    {
        self.get_mut_response_middleware()
            .push(server_hook_factory::<S>());
        self
    }
    #[inline(always)]
    pub fn format_bind_address<H>(host: H, port: u16) -> String
    where
        H: AsRef<str>,
    {
        format!("{}{COLON}{port}", host.as_ref())
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
    async fn handle_panic_with_context(&self, ctx: &mut Context, panic: &PanicData) {
        ctx.set_aborted(false)
            .set_closed(false)
            .set_task_panic(panic.clone());
        for hook in self.get_task_panic().iter() {
            Box::pin(self.task_handler(ctx, hook, false)).await;
            if ctx.get_aborted() {
                return;
            }
        }
        ctx.set_aborted(true).set_closed(true);
    }
    async fn handle_task_panic(&self, ctx: &mut Context, join_error: JoinError) {
        let panic: PanicData = PanicData::from_join_error(join_error);
        ctx.get_mut_response()
            .set_status_code(HttpStatus::InternalServerError.code());
        self.handle_panic_with_context(ctx, &panic).await
    }
    async fn task_handler(&self, ctx: &mut Context, hook: &ServerHookHandler, progress: bool) {
        if let Err(join_error) = spawn(hook(ctx)).await {
            if !join_error.is_panic() {
                return;
            }
            if progress {
                Box::pin(self.handle_task_panic(ctx, join_error)).await;
                return;
            }
            eprintln!("{}", join_error);
            let _ = Self::try_flush_stdout_and_stderr();
        };
    }
    async fn configure_stream(&self, stream: &TcpStream) {
        let config: ServerConfig = self.get_server_config().clone();
        if let Some(nodelay) = config.try_get_nodelay() {
            let _ = stream.set_nodelay(*nodelay);
        }
        if let Some(ttl) = config.try_get_ttl() {
            let _ = stream.set_ttl(*ttl);
        }
    }
    pub(super) async fn handle_request_middleware(&self, ctx: &mut Context) -> bool {
        for hook in self.get_request_middleware().iter() {
            self.task_handler(ctx, hook, true).await;
            if ctx.get_aborted() {
                return true;
            }
        }
        false
    }
    pub(super) async fn handle_route_matcher(&self, ctx: &mut Context, path: &str) -> bool {
        if let Some(hook) = self.get_route_matcher().try_resolve_route(ctx, path) {
            self.task_handler(ctx, &hook, true).await;
            if ctx.get_aborted() {
                return true;
            }
        }
        false
    }
    pub(super) async fn handle_response_middleware(&self, ctx: &mut Context) -> bool {
        for hook in self.get_response_middleware().iter() {
            self.task_handler(ctx, hook, true).await;
            if ctx.get_aborted() {
                return true;
            }
        }
        false
    }
    async fn spawn_connection_handler(&self, stream: ArcRwLockStream) {
        let server_address: usize = self.into();
        spawn(async move {
            let server: &'static Server = server_address.into();
            server.handle_connection(stream).await;
        });
    }
    pub async fn handle_request_error(&self, ctx: &mut Context, error: &RequestError) {
        ctx.set_aborted(false)
            .set_closed(false)
            .set_request_error_data(error.clone());
        for hook in self.get_request_error().iter() {
            self.task_handler(ctx, hook, true).await;
            if ctx.get_aborted() {
                return;
            }
        }
        ctx.set_aborted(true).set_closed(true);
    }
    async fn request_hook(&self, state: &HandlerState, request: &Request) -> bool {
        let route: &str = request.get_path();
        let ctx: &mut Context = &mut Context::new(state.get_stream(), request, state.get_server());
        let keep_alive: bool = request.is_enable_keep_alive();
        if self.handle_request_middleware(ctx).await {
            return ctx.is_keep_alive(keep_alive);
        }
        if self.handle_route_matcher(ctx, route).await {
            return ctx.is_keep_alive(keep_alive);
        }
        if self.handle_response_middleware(ctx).await {
            return ctx.is_keep_alive(keep_alive);
        }
        ctx.is_keep_alive(keep_alive)
    }
    async fn handle_http_requests(&self, state: &HandlerState, request: &Request) {
        if !self.request_hook(state, request).await {
            return;
        }
        let stream: &ArcRwLockStream = state.get_stream();
        let request_config: &RequestConfig = state.get_server().get_request_config();
        loop {
            match Request::http_from_stream(stream, request_config).await {
                Ok(new_request) => {
                    if !self.request_hook(state, &new_request).await {
                        return;
                    }
                }
                Err(error) => {
                    self.handle_request_error(&mut state.get_stream().into(), &error)
                        .await;
                    return;
                }
            }
        }
    }
    async fn handle_connection(&self, stream: ArcRwLockStream) {
        match Request::http_from_stream(&stream, self.get_request_config()).await {
            Ok(request) => {
                let server_address: usize = self.into();
                let hook: HandlerState = HandlerState::new(stream, server_address.into());
                self.handle_http_requests(&hook, &request).await;
            }
            Err(error) => {
                self.handle_request_error(&mut stream.into(), &error).await;
            }
        }
    }
    async fn accept_connections(&self, tcp_listener: &TcpListener) -> Result<(), ServerError> {
        while let Ok((stream, _)) = tcp_listener.accept().await {
            self.configure_stream(&stream).await;
            let stream: ArcRwLockStream = ArcRwLockStream::from_stream(stream);
            self.spawn_connection_handler(stream).await;
        }
        Ok(())
    }
    async fn create_tcp_listener(&self) -> Result<TcpListener, ServerError> {
        Ok(TcpListener::bind(self.get_server_config().get_address()).await?)
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
        let wait_hook: ServerControlHookHandler<()> = Arc::new(move || {
            let mut wait_receiver_clone: Receiver<()> = wait_receiver.clone();
            Box::pin(async move {
                let _ = wait_receiver_clone.changed().await;
            })
        });
        let shutdown_hook: ServerControlHookHandler<()> = Arc::new(move || {
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
# Path: hyperlane/src/server/struct.rs
```rust
use crate::*;
#[derive(Clone, CustomDebug, DisplayDebug, Getter, New)]
pub(crate) struct HandlerState {
    pub(super) stream: ArcRwLockStream,
    pub(super) server: &'static Server,
}
#[derive(Clone, CustomDebug, Data, DisplayDebug, New)]
pub struct Server {
    #[get_mut(skip)]
    #[set(pub(super))]
    pub(super) server_config: ServerConfig,
    #[get_mut(skip)]
    #[set(pub(super))]
    pub(super) request_config: RequestConfig,
    #[get_mut(pub(super))]
    #[set(skip)]
    pub(super) route_matcher: RouteMatcher,
    #[debug(skip)]
    #[get_mut(pub(super))]
    #[set(skip)]
    pub(super) request_error: ServerHookList,
    #[debug(skip)]
    #[get_mut(pub(super))]
    #[set(skip)]
    pub(super) task_panic: ServerHookList,
    #[debug(skip)]
    #[get_mut(pub(super))]
    #[set(skip)]
    pub(super) request_middleware: ServerHookList,
    #[debug(skip)]
    #[get_mut(pub(super))]
    #[set(skip)]
    pub(super) response_middleware: ServerHookList,
}
```
# Path: hyperlane/src/server/type.rs
```rust
use crate::*;
pub type ArcServer = Arc<Server>;
```
# Path: hyperlane/src/server/test.rs
```rust
use crate::*;
#[test]
fn server_partial_eq() {
    let server1: Server = Server::default();
    let server2: Server = Server::default();
    assert_eq!(server1, server2);
    let server1_clone: Server = server1.clone();
    assert_eq!(server1, server1_clone);
}
#[test]
fn server_from_usize() {
    let mut server: Server = Server::default();
    server.set_request_config(RequestConfig::default());
    let server_address: usize = (&server).into();
    let server_from_addr: Server = server_address.into();
    assert_eq!(
        server.get_request_config(),
        server_from_addr.get_request_config()
    );
}
#[test]
fn server_ref_from_usize() {
    let mut server: Server = Server::default();
    server.set_server_config(ServerConfig::default());
    let server_address: usize = (&server).into();
    let server_ref: &Server = server_address.into();
    assert_eq!(server.get_server_config(), server_ref.get_server_config());
}
#[test]
fn server_mut_from_usize() {
    let mut server: Server = Server::default();
    let server_address: usize = (&mut server).into();
    let server_mut: &mut Server = server_address.into();
    let mut config: ServerConfig = ServerConfig::default();
    config.set_nodelay(Some(true));
    server_mut.set_server_config(config);
    assert!(server_mut.get_server_config().try_get_nodelay().is_some());
}
#[test]
fn server_from_server_config() {
    let mut server_config: ServerConfig = ServerConfig::default();
    server_config.set_nodelay(Some(true));
    let server: Server = server_config.clone().into();
    assert_eq!(server.get_request_config(), &RequestConfig::default());
    assert_eq!(server.get_server_config(), &server_config);
    assert!(server.get_task_panic().is_empty());
    assert!(server.get_request_error().is_empty());
    assert!(server.get_request_middleware().is_empty());
    assert!(server.get_response_middleware().is_empty());
}
#[test]
fn server_from_request_config() {
    let mut request_config: RequestConfig = RequestConfig::default();
    request_config.set_buffer_size(KB_1);
    let server: Server = request_config.into();
    assert_eq!(server.get_request_config(), &request_config);
    assert_eq!(server.get_server_config(), &ServerConfig::default());
    assert!(server.get_task_panic().is_empty());
    assert!(server.get_request_error().is_empty());
    assert!(server.get_request_middleware().is_empty());
    assert!(server.get_response_middleware().is_empty());
}
#[test]
fn server_inner_partial_eq() {
    let inner1: Server = Server::default();
    let inner2: Server = Server::default();
    assert_eq!(inner1, inner2);
}
#[test]
fn server_ref_into_usize() {
    let server: Server = Server::default();
    let server_address: usize = (&server).into();
    assert!(server_address > 0);
}
#[test]
fn server_mut_into_usize() {
    let mut server: Server = Server::default();
    let server_address: usize = (&mut server).into();
    assert!(server_address > 0);
}
#[test]
fn server_as_ref() {
    let mut server: Server = Server::default();
    server.set_server_config(ServerConfig::default());
    let server_ref: &Server = server.as_ref();
    assert_eq!(server.get_server_config(), server_ref.get_server_config());
    assert_eq!(server.get_request_config(), server_ref.get_request_config());
}
#[test]
fn server_as_mut() {
    let mut server: Server = Server::default();
    let server_mut: &mut Server = server.as_mut();
    let mut config: ServerConfig = ServerConfig::default();
    config.set_nodelay(Some(true));
    server_mut.set_server_config(config);
    assert!(server.get_server_config().try_get_nodelay().is_some());
}
struct TestSendRoute;
impl ServerHook for TestSendRoute {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    async fn handle(self, _ctx: &mut Context) {}
}
#[test]
fn server_send_sync() {
    fn assert_send<T: Send>() {}
    fn assert_sync<T: Sync>() {}
    fn assert_send_sync<T: Send + Sync>() {}
    assert_send::<Server>();
    assert_sync::<Server>();
    assert_send_sync::<Server>();
}
#[tokio::test]
async fn server_clone_across_threads() {
    let mut server: Server = Server::default();
    server.route::<TestSendRoute>("/test");
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
    let mut server: Server = Server::default();
    server.route::<TestSendRoute>("/test");
    let server: Arc<Server> = Arc::new(server);
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
struct TaskPanicHook {
    response_body: String,
    content_type: String,
}
impl ServerHook for TaskPanicHook {
    async fn new(ctx: &mut Context) -> Self {
        let error: PanicData = ctx.try_get_task_panic_data().unwrap_or_default();
        let response_body: String = error.to_string();
        let content_type: String = ContentType::format_content_type_with_charset(TEXT_PLAIN, UTF8);
        Self {
            response_body,
            content_type,
        }
    }
    async fn handle(self, ctx: &mut Context) {
        ctx.get_mut_response()
            .set_version(HttpVersion::Http1_1)
            .set_status_code(500)
            .clear_headers()
            .set_header(SERVER, HYPERLANE)
            .set_header(CONTENT_TYPE, &self.content_type)
            .set_body(&self.response_body);
        if ctx.try_send().await.is_err() {
            ctx.set_aborted(true).set_closed(true);
        }
    }
}
struct RequestErrorHook {
    response_status_code: ResponseStatusCode,
    response_body: String,
}
impl ServerHook for RequestErrorHook {
    async fn new(ctx: &mut Context) -> Self {
        let request_error: RequestError = ctx.try_get_request_error_data().unwrap_or_default();
        Self {
            response_status_code: request_error.get_http_status_code(),
            response_body: request_error.to_string(),
        }
    }
    async fn handle(self, ctx: &mut Context) {
        ctx.get_mut_response()
            .set_version(HttpVersion::Http1_1)
            .set_status_code(self.response_status_code)
            .set_body(self.response_body);
        if ctx.try_send().await.is_err() {
            ctx.set_aborted(true).set_closed(true);
        }
    }
}
struct RequestMiddleware {
    socket_addr: String,
}
impl ServerHook for RequestMiddleware {
    async fn new(ctx: &mut Context) -> Self {
        let mut socket_addr: String = String::new();
        if let Some(stream) = ctx.try_get_stream().as_ref() {
            socket_addr = stream
                .read()
                .await
                .peer_addr()
                .map(|data| data.to_string())
                .unwrap_or_default();
        }
        Self { socket_addr }
    }
    async fn handle(self, ctx: &mut Context) {
        ctx.get_mut_response()
            .set_version(HttpVersion::Http1_1)
            .set_status_code(200)
            .set_header(SERVER, HYPERLANE)
            .set_header(CONNECTION, KEEP_ALIVE)
            .set_header(CONTENT_TYPE, TEXT_PLAIN)
            .set_header(ACCESS_CONTROL_ALLOW_ORIGIN, WILDCARD_ANY)
            .set_header("SocketAddr", &self.socket_addr);
    }
}
struct UpgradeMiddleware;
impl ServerHook for UpgradeMiddleware {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &mut Context) {
        if !ctx.get_request().is_ws_upgrade_type() {
            return;
        }
        if let Some(key) = &ctx.get_request().try_get_header_back(SEC_WEBSOCKET_KEY) {
            let accept_key: String = WebSocketFrame::generate_accept_key(key);
            ctx.get_mut_response()
                .set_version(HttpVersion::Http1_1)
                .set_status_code(101)
                .set_header(UPGRADE, WEBSOCKET)
                .set_header(CONNECTION, UPGRADE)
                .set_header(SEC_WEBSOCKET_ACCEPT, &accept_key)
                .set_body(vec![]);
            if ctx.try_send().await.is_err() {
                ctx.set_aborted(true).set_closed(true);
            }
        }
    }
}
struct ResponseMiddleware;
impl ServerHook for ResponseMiddleware {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &mut Context) {
        if ctx.get_request().is_ws_upgrade_type() {
            return;
        }
        if ctx.try_send().await.is_err() {
            ctx.set_aborted(true).set_closed(true);
        }
    }
}
struct RootRoute {
    response_body: String,
    cookie1: String,
    cookie2: String,
}
impl ServerHook for RootRoute {
    async fn new(ctx: &mut Context) -> Self {
        let response_body: String = format!("Hello hyperlane => {}", ctx.get_request().get_path());
        let cookie1: String = CookieBuilder::new("key1", "value1").http_only().build();
        let cookie2: String = CookieBuilder::new("key2", "value2").http_only().build();
        Self {
            response_body,
            cookie1,
            cookie2,
        }
    }
    async fn handle(self, ctx: &mut Context) {
        ctx.get_mut_response()
            .add_header(SET_COOKIE, &self.cookie1)
            .add_header(SET_COOKIE, &self.cookie2)
            .set_body(&self.response_body);
    }
}
struct SseRoute;
impl ServerHook for SseRoute {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &mut Context) {
        ctx.get_mut_response()
            .set_header(CONTENT_TYPE, TEXT_EVENT_STREAM)
            .set_body(vec![]);
        if ctx.try_send().await.is_err() {
            ctx.set_aborted(true).set_closed(true);
            return;
        }
        for i in 0..10 {
            ctx.get_mut_response()
                .set_body(format!("data:{i}{HTTP_DOUBLE_BR}"));
            if ctx.try_send_body().await.is_err() {
                ctx.set_aborted(true).set_closed(true);
                return;
            }
        }
        ctx.set_aborted(true).set_closed(true);
    }
}
struct WebsocketRoute;
impl WebsocketRoute {
    async fn try_send_body_hook(&self, ctx: &mut Context) -> Result<(), ResponseError> {
        let send_result: Result<(), ResponseError> = if ctx.get_request().is_ws_upgrade_type() {
            let body: &ResponseBody = ctx.get_response().get_body();
            let frame_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(body);
            ctx.try_send_body_list_with_data(&frame_list).await
        } else {
            ctx.try_send_body().await
        };
        if send_result.is_err() {
            ctx.set_aborted(true).set_closed(true);
        }
        send_result
    }
}
impl ServerHook for WebsocketRoute {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &mut Context) {
        loop {
            match ctx.ws_from_stream().await {
                Ok(_) => {
                    let body: Vec<u8> = ctx.get_request().get_body().clone();
                    ctx.get_mut_response().set_body(body);
                    if self.try_send_body_hook(ctx).await.is_err() {
                        return;
                    }
                }
                Err(error) => {
                    ctx.get_mut_response().set_body(error.to_string());
                    let _ = self.try_send_body_hook(ctx).await;
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
    async fn new(ctx: &mut Context) -> Self {
        Self {
            params: ctx.get_route_params().clone(),
        }
    }
    async fn handle(mut self, _ctx: &mut Context) {
        self.params.insert("key".to_owned(), "value".to_owned());
        panic!("Test panic {:?}", self.params);
    }
}
struct GetAllRoutes;
impl ServerHook for GetAllRoutes {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &mut Context) {
        let route_matcher: &RouteMatcher = ctx.get_server().get_route_matcher();
        let mut response_body: String = String::new();
        for key in route_matcher.get_static_route().keys() {
            response_body.push_str(&format!("Static route: {key}\n"));
        }
        for value in route_matcher.get_dynamic_route().values() {
            for (route_pattern, _) in value {
                response_body.push_str(&format!("Dynamic route: {route_pattern}\n"));
            }
        }
        for value in route_matcher.get_regex_route().values() {
            for (route_pattern, _) in value {
                response_body.push_str(&format!("Regex route: {route_pattern}\n"));
            }
        }
        ctx.get_mut_response().set_body(&response_body);
    }
}
#[tokio::test]
async fn main() {
    let mut server: Server = Server::default();
    let mut server_config: ServerConfig = ServerConfig::default();
    server_config
        .set_address(Server::format_bind_address(DEFAULT_HOST, 80))
        .set_nodelay(Some(false));
    server.server_config(server_config);
    server.task_panic::<TaskPanicHook>();
    server.request_error::<RequestErrorHook>();
    server.request_middleware::<RequestMiddleware>();
    server.request_middleware::<UpgradeMiddleware>();
    server.response_middleware::<ResponseMiddleware>();
    server.route::<RootRoute>("/");
    server.route::<SseRoute>("/sse");
    server.route::<WebsocketRoute>("/websocket");
    server.route::<GetAllRoutes>("/get/all/routes");
    server.route::<DynamicRoute>("/dynamic/{routing}");
    server.route::<DynamicRoute>("/regex/{file:^.*$}");
    let server_control_hook_1: ServerControlHook = server.run().await.unwrap_or_default();
    let server_control_hook_2: ServerControlHook = server_control_hook_1.clone();
    spawn(async move {
        sleep(Duration::from_secs(60)).await;
        server_control_hook_2.shutdown().await;
    });
    server_control_hook_1.wait().await;
}
```
# Path: hyperlane/src/route/mod.rs
```rust
mod r#enum;
mod r#impl;
mod r#struct;
#[cfg(test)]
mod test;
mod r#type;
pub use {r#enum::*, r#struct::*, r#type::*};
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
    pub(crate) fn try_resolve_route(
        &self,
        ctx: &mut Context,
        path: &str,
    ) -> Option<ServerHookHandler> {
        if let Some(hook) = self.get_static_route().get(path) {
            ctx.set_route_params(RouteParams::default());
            return Some(hook.clone());
        }
        let path_segment_count: usize = Self::count_path_segments(path);
        if let Some(routes) = self.get_dynamic_route().get(&path_segment_count) {
            for (pattern, hook) in routes {
                if let Some(params) = pattern.try_match_path(path) {
                    ctx.set_route_params(params);
                    return Some(hook.clone());
                }
            }
        }
        if let Some(routes) = self.get_regex_route().get(&path_segment_count) {
            for (pattern, hook) in routes {
                if let Some(params) = pattern.try_match_path(path) {
                    ctx.set_route_params(params);
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
                    ctx.set_route_params(params);
                    return Some(hook.clone());
                }
            }
        }
        None
    }
}
```
# Path: hyperlane/src/route/struct.rs
```rust
use crate::*;
#[derive(Clone, Debug, DisplayDebug, Getter)]
pub struct RoutePattern(
    #[get]
    pub(super) RouteSegmentList,
);
#[derive(Clone, CustomDebug, DisplayDebug, Getter, GetterMut, Setter)]
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
# Path: hyperlane/src/route/type.rs
```rust
use crate::*;
pub type RouteParams = HashMapXxHash3_64<String, String>;
pub type RouteSegmentList = Vec<RouteSegment>;
pub(crate) type PathComponentList<'a> = Vec<&'a str>;
```
# Path: hyperlane/src/route/test.rs
```rust
use crate::*;
struct TestRoute {
    data: String,
}
impl ServerHook for TestRoute {
    async fn new(_ctx: &mut Context) -> Self {
        Self {
            data: String::new(),
        }
    }
    async fn handle(mut self, _ctx: &mut Context) {
        self.data = String::from("test");
    }
}
#[test]
#[should_panic(expected = "EmptyPattern")]
fn empty_route() {
    let _server: &Server = Server::default().route::<TestRoute>(EMPTY_STR);
}
#[test]
#[should_panic(expected = "DuplicatePattern")]
fn duplicate_route() {
    let _server: &Server = Server::default()
        .route::<TestRoute>(ROOT_PATH)
        .route::<TestRoute>(ROOT_PATH);
}
#[test]
fn get_route() {
    let mut server: Server = Server::default();
    server
        .route::<TestRoute>(ROOT_PATH)
        .route::<TestRoute>("/dynamic/{routing}")
        .route::<TestRoute>("/regex/{file:^.*$}");
    let route_matcher: RouteMatcher = server.get_route_matcher().clone();
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
#[test]
fn segment_count_optimization() {
    let mut server: Server = Server::default();
    server.route::<TestRoute>("/users/{id}");
    server.route::<TestRoute>("/users/{id}/posts");
    server.route::<TestRoute>("/users/{id}/posts/{post_id}");
    server.route::<TestRoute>("/api/v1/users/{id}");
    let route_matcher: RouteMatcher = server.get_route_matcher().clone();
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
#[test]
fn regex_route_segment_count() {
    let mut server: Server = Server::default();
    server.route::<TestRoute>("/files/{path:.*}");
    server.route::<TestRoute>("/api/{version:\\d+}/users");
    server.route::<TestRoute>("/api/{version:\\d+}/posts/{id:\\d+}");
    let route_matcher: RouteMatcher = server.get_route_matcher().clone();
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
#[test]
fn mixed_route_types() {
    let mut server: Server = Server::default();
    server.route::<TestRoute>("/");
    server.route::<TestRoute>("/about");
    server.route::<TestRoute>("/users/{id}");
    server.route::<TestRoute>("/posts/{slug}");
    server.route::<TestRoute>("/files/{path:.*}");
    let route_matcher: RouteMatcher = server.get_route_matcher().clone();
    assert_eq!(route_matcher.get_static_route().len(), 2);
    assert!(route_matcher.get_dynamic_route().contains_key(&2));
    assert!(route_matcher.get_regex_route().contains_key(&2));
}
#[test]
fn large_dynamic_routes() {
    const ROUTE_COUNT: u32 = 1000;
    let mut server: Server = Server::default();
    let start_insert: Instant = Instant::now();
    for i in 0..ROUTE_COUNT {
        let path: String = format!("/api/resource{i}/{{id}}");
        server.route::<TestRoute>(&path);
    }
    let insert_duration: Duration = start_insert.elapsed();
    println!(
        "Inserted {} dynamic routes in: {:?}",
        ROUTE_COUNT, insert_duration
    );
    let route_matcher: RouteMatcher = server.get_route_matcher().clone();
    assert!(!route_matcher.get_dynamic_route().is_empty());
    let mut ctx: Context = Context::default();
    let start_match: Instant = Instant::now();
    for i in 0..ROUTE_COUNT {
        let path: String = format!("/api/resource{i}/123");
        let _ = route_matcher.try_resolve_route(&mut ctx, &path);
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
#[test]
fn large_regex_routes() {
    const ROUTE_COUNT: u32 = 1000;
    let mut server: Server = Server::default();
    let start_insert: Instant = Instant::now();
    for i in 0..ROUTE_COUNT {
        let path: String = format!("/api/resource{i}/{{id:[0-9]+}}");
        server.route::<TestRoute>(&path);
    }
    let insert_duration: Duration = start_insert.elapsed();
    println!(
        "Inserted {} regex routes in: {:?}",
        ROUTE_COUNT, insert_duration
    );
    let route_matcher: RouteMatcher = server.get_route_matcher().clone();
    assert!(!route_matcher.get_regex_route().is_empty());
    let mut ctx: Context = Context::default();
    let start_match: Instant = Instant::now();
    for i in 0..ROUTE_COUNT {
        let path: String = format!("/api/resource{i}/123");
        let _ = route_matcher.try_resolve_route(&mut ctx, &path);
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
#[test]
fn large_tail_regex_routes() {
    const ROUTE_COUNT: u32 = 1000;
    let mut server: Server = Server::default();
    let start_insert: Instant = Instant::now();
    for i in 0..ROUTE_COUNT {
        let path: String = format!("/api/resource{i}/{{path:.*}}");
        server.route::<TestRoute>(&path);
    }
    let insert_duration: Duration = start_insert.elapsed();
    println!(
        "Inserted {} tail regex routes in: {:?}",
        ROUTE_COUNT, insert_duration
    );
    let route_matcher: RouteMatcher = server.get_route_matcher().clone();
    assert!(!route_matcher.get_regex_route().is_empty());
    let mut ctx: Context = Context::default();
    let start_match: Instant = Instant::now();
    for i in 0..ROUTE_COUNT {
        let path: String = format!("/api/resource{i}/some/nested/path");
        let _ = route_matcher.try_resolve_route(&mut ctx, &path);
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
# Path: hyperlane/src/attribute/mod.rs
```rust
mod r#enum;
mod r#impl;
#[cfg(test)]
mod test;
mod r#type;
pub use r#type::*;
pub(crate) use r#enum::*;
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
# Path: hyperlane/src/attribute/test.rs
```rust
use crate::*;
#[test]
fn get_panic_from_context() {
    let mut ctx: Context = Context::default();
    let set_panic: PanicData = PanicData::new(
        Some("test".to_string()),
        Some("test".to_string()),
        Some("test".to_string()),
    );
    ctx.set_task_panic(set_panic.clone());
    let get_panic: PanicData = ctx.try_get_task_panic_data().unwrap();
    assert_eq!(set_panic, get_panic);
}
#[test]
fn context_attributes() {
    let mut ctx: Context = Context::default();
    ctx.set_attribute("key1", "value1".to_string());
    let value: Option<String> = ctx.try_get_attribute("key1");
    assert_eq!(value, Some("value1".to_string()));
    ctx.remove_attribute("key1");
    let value: Option<String> = ctx.try_get_attribute("key1");
    assert_eq!(value, None);
    ctx.set_attribute("key2", 123);
    ctx.clear_attribute();
    let value: Option<i32> = ctx.try_get_attribute("key2");
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
    assert!(!panic_struct.try_get_message().is_none());
    assert!(
        panic_struct
            .try_get_message()
            .clone()
            .unwrap_or_default()
            .contains(message)
    );
}
#[test]
fn run_set_func() {
    let mut ctx: Context = Context::default();
    const KEY: &str = "string";
    const PARAM: &str = "test";
    let func: &(dyn Fn(&str) -> String + Send + Sync) = &|msg: &str| msg.to_string();
    ctx.set_attribute(KEY, func);
    let get_key: &(dyn Fn(&str) -> String + Send + Sync) = ctx.try_get_attribute(KEY).unwrap();
    assert_eq!(get_key(PARAM), func(PARAM));
    let func: &(dyn Fn(&str) + Send + Sync) = &|msg: &str| {
        assert_eq!(msg, PARAM);
    };
    ctx.set_attribute(KEY, func);
    let hyperlane = ctx.get_attribute::<&(dyn Fn(&str) + Send + Sync)>(KEY);
    hyperlane(PARAM);
}
```
# Path: hyperlane/src/attribute/enum.rs
```rust
use crate::*;
#[derive(Clone, CustomDebug, Deserialize, DisplayDebug, Eq, Hash, PartialEq, Serialize)]
pub(crate) enum Attribute {
    External(String),
    Internal(InternalAttribute),
}
#[derive(Clone, Copy, CustomDebug, Deserialize, DisplayDebug, Eq, Hash, PartialEq, Serialize)]
pub(crate) enum InternalAttribute {
    TaskPanicData,
    RequestErrorData,
}
```
# Path: hyperlane/src/error/mod.rs
```rust
mod r#enum;
mod r#impl;
#[cfg(test)]
mod test;
pub use r#enum::*;
```
# Path: hyperlane/src/error/impl.rs
```rust
use crate::*;
impl From<std::io::Error> for ServerError {
    #[inline(always)]
    fn from(error: std::io::Error) -> Self {
        ServerError::TcpBind(error.to_string())
    }
}
```
# Path: hyperlane/src/error/test.rs
```rust
use crate::*;
#[test]
fn server_error() {
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
#[test]
fn route_error() {
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
# Path: hyperlane/src/error/enum.rs
```rust
use crate::*;
#[derive(Clone, CustomDebug, Deserialize, DisplayDebug, Eq, PartialEq, Serialize)]
pub enum ServerError {
    TcpBind(String),
    Unknown(String),
    HttpRead(String),
    InvalidHttpRequest(Request),
    Other(String),
}
#[derive(Clone, CustomDebug, Deserialize, DisplayDebug, Eq, PartialEq, Serialize)]
pub enum RouteError {
    EmptyPattern,
    DuplicatePattern(String),
    InvalidRegexPattern(String),
}
```
# Path: hyperlane-time/README.md
## hyperlane-time
[Official Documentation](https://docs.ltpp.vip/hyperlane-time/)
[Api Docs](https://docs.rs/hyperlane-time/latest/)
> A library for fetching the current time based on the system's locale settings.
## Installation
To use this crate, you can run cmd:
```shell
cargo add hyperlane-time
```
## Contact
# Path: hyperlane-time/src/lib.rs
```rust
mod r#enum;
mod r#fn;
mod r#impl;
#[cfg(test)]
mod test;
pub use r#fn::*;
use r#enum::*;
use std::{
    env, fmt,
    fmt::Write,
    str::FromStr,
    time::{Duration, SystemTime, UNIX_EPOCH},
};
```
# Path: hyperlane-time/src/fn.rs
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
# Path: hyperlane-time/src/impl.rs
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
# Path: hyperlane-time/src/test.rs
```rust
use crate::*;
#[test]
fn test_lang() {
    println!("test_lang: {}", from_env_var());
}
#[test]
fn test_now_time() {
    println!("test_now_time: {}", time());
}
#[test]
fn test_methods() {
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
# Path: hyperlane-time/src/enum.rs
```rust
#[derive(Clone, Copy, Debug, Default, Eq, Hash, Ord, PartialEq, PartialOrd)]
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
# Path: hyperlane-utils/README.md
## hyperlane-utils
[Official Documentation](https://docs.ltpp.vip/hyperlane-utils/)
[Api Docs](https://docs.rs/hyperlane-utils/latest/)
> A library providing utils for hyperlane.
## Installation
To use this crate, you can run cmd:
```shell
cargo add hyperlane-utils
```
## Contact
# Path: hyperlane-utils/src/lib.rs
```rust
pub use {
    ahash, base64, bin_encode_decode::*, bytemuck_derive, chrono, chunkify::*, clonelicious::*,
    color_output::*, compare_version::*, dotenvy, file_operation::*, future_fn::*, futures, hex,
    hot_restart::*, http_request::*, hyperlane_broadcast::*, hyperlane_log::*, hyperlane_macros::*,
    hyperlane_plugin_websocket::*, instrument_level::*, jsonwebtoken, jwt_service::*, log,
    lombok_macros::*, num_cpus, once_cell, recoverable_spawn::*, recoverable_thread_pool::*, redis,
    regex, rust_decimal, sea_orm, serde_urlencoded, serde_with, serde_xml_rs, serde_yaml,
    server_manager::*, sha2, simd_json, snafu, sqlx, std_macro_extensions::*, sysinfo, tracing_log,
    tracing_subscriber, twox_hash, url, urlencoding, utoipa, utoipa_rapidoc, utoipa_swagger_ui,
    uuid,
};
```
# Path: hyperlane-broadcast/README.md
## hyperlane-broadcast
[Official Documentation](https://docs.ltpp.vip/hyperlane-broadcast/)
[Api Docs](https://docs.rs/hyperlane-broadcast/latest/)
> hyperlane-broadcast is a lightweight and ergonomic wrapper over Tokio’s broadcast channel designed for easy-to-use publish-subscribe messaging in async Rust applications. It simplifies the native Tokio broadcast API by providing a straightforward interface for broadcasting messages to multiple subscribers with minimal boilerplate.
## Installation
To use this crate, you can run cmd:
```shell
cargo add hyperlane-broadcast
```
## Contact
# Path: hyperlane-broadcast/src/lib.rs
```rust
mod broadcast;
mod broadcast_map;
pub use {broadcast::*, broadcast_map::*};
#[cfg(test)]
use std::time::Duration;
use std::{fmt::Debug, hash::BuildHasherDefault};
#[cfg(test)]
use tokio::{
    sync::broadcast::error::RecvError,
    time::{error::Elapsed, timeout},
};
use {
    dashmap::{mapref::one::Ref, *},
    tokio::sync::broadcast::{
        error::SendError,
        {Receiver, Sender},
    },
    twox_hash::XxHash3_64,
};
```
# Path: hyperlane-broadcast/src/broadcast_map/trait.rs
```rust
use crate::*;
pub trait BroadcastMapTrait: Clone + Debug {}
```
# Path: hyperlane-broadcast/src/broadcast_map/mod.rs
```rust
mod r#impl;
mod r#struct;
#[cfg(test)]
mod test;
mod r#trait;
mod r#type;
pub use {r#struct::*, r#trait::*, r#type::*};
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
    pub fn insert<K>(&self, key: K, capacity: Capacity) -> Option<Broadcast<T>>
    where
        K: AsRef<str>,
    {
        let broadcast: Broadcast<T> = Broadcast::new(capacity);
        self.get().insert(key.as_ref().to_owned(), broadcast)
    }
    #[inline(always)]
    pub fn receiver_count<K>(&self, key: K) -> Option<ReceiverCount>
    where
        K: AsRef<str>,
    {
        self.get()
            .get(key.as_ref())
            .map(|receiver: Ref<'_, String, Broadcast<T>>| receiver.receiver_count())
    }
    #[inline(always)]
    pub fn subscribe<K>(&self, key: K) -> Option<BroadcastMapReceiver<T>>
    where
        K: AsRef<str>,
    {
        self.get()
            .get(key.as_ref())
            .map(|receiver: Ref<'_, String, Broadcast<T>>| receiver.subscribe())
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
    pub fn try_send<K>(&self, key: K, data: T) -> Result<Option<ReceiverCount>, SendError<T>>
    where
        K: AsRef<str>,
    {
        match self.get().get(key.as_ref()) {
            Some(sender) => sender.send(data).map(Some),
            None => Ok(None),
        }
    }
    #[inline(always)]
    pub fn send<K>(&self, key: K, data: T) -> Option<ReceiverCount>
    where
        K: AsRef<str>,
    {
        self.try_send(key, data).unwrap()
    }
    #[inline(always)]
    pub fn unsubscribe<K>(&self, key: K) -> Option<Broadcast<T>>
    where
        K: AsRef<str>,
    {
        self.get()
            .remove(key.as_ref())
            .map(|(_, broadcast): (String, Broadcast<T>)| broadcast)
    }
}
```
# Path: hyperlane-broadcast/src/broadcast_map/struct.rs
```rust
use crate::*;
#[derive(Clone, Debug)]
pub struct BroadcastMap<T: BroadcastTrait>(pub(super) DashMapStringBroadcast<T>);
```
# Path: hyperlane-broadcast/src/broadcast_map/type.rs
```rust
use crate::*;
pub type BroadcastMapSendError<T> = SendError<T>;
pub type BroadcastMapReceiver<T> = Receiver<T>;
pub type BroadcastMapSender<T> = Sender<T>;
pub type DashMapStringBroadcast<T> = DashMap<String, Broadcast<T>, BuildHasherDefault<XxHash3_64>>;
```
# Path: hyperlane-broadcast/src/broadcast_map/test.rs
```rust
use crate::*;
#[tokio::test]
pub async fn test_broadcast_map() {
    let broadcast_map: BroadcastMap<u128> = BroadcastMap::new();
    broadcast_map.insert("test_key", 10);
    let mut rec1: BroadcastMapReceiver<u128> = broadcast_map.subscribe("test_key").unwrap();
    let mut rec2: BroadcastMapReceiver<u128> = broadcast_map.subscribe("test_key").unwrap();
    let mut rec3: BroadcastMapReceiver<u128> =
        broadcast_map.subscribe_or_insert("another_key", DEFAULT_BROADCAST_SENDER_CAPACITY);
    broadcast_map.send("test_key", 20).unwrap();
    broadcast_map.send("another_key", 10).unwrap();
    assert_eq!(rec1.recv().await, Ok(20));
    assert_eq!(rec2.recv().await, Ok(20));
    assert_eq!(rec3.recv().await, Ok(10));
}
#[tokio::test]
pub async fn test_broadcast_map_unsubscribe() {
    let broadcast_map: BroadcastMap<u128> = BroadcastMap::new();
    broadcast_map.insert("test_key", 10);
    let mut rec1: BroadcastMapReceiver<u128> = broadcast_map.subscribe("test_key").unwrap();
    let removed: Option<Broadcast<u128>> = broadcast_map.unsubscribe("test_key");
    assert!(removed.is_some());
    drop(removed);
    let not_exist: Option<Broadcast<u128>> = broadcast_map.unsubscribe("nonexistent_key");
    assert!(not_exist.is_none());
    assert!(broadcast_map.subscribe("test_key").is_none());
    let send_result: Result<Option<ReceiverCount>, SendError<u128>> =
        broadcast_map.try_send("test_key", 30);
    assert!(send_result.unwrap().is_none());
    let result: Result<Result<u128, RecvError>, Elapsed> =
        timeout(Duration::from_millis(100), rec1.recv()).await;
    assert!(result.is_ok(), "recv should not timeout after unsubscribe");
    assert_eq!(result.unwrap(), Err(RecvError::Closed));
}
#[tokio::test]
pub async fn test_broadcast_map_unsubscribe_and_reinsert() {
    let broadcast_map: BroadcastMap<u128> = BroadcastMap::new();
    broadcast_map.insert("test_key", 10);
    broadcast_map.subscribe("test_key").unwrap();
    let removed: Option<Broadcast<u128>> = broadcast_map.unsubscribe("test_key");
    assert!(removed.is_some());
    broadcast_map.insert("test_key", 10);
    let mut rec2: BroadcastMapReceiver<u128> = broadcast_map.subscribe("test_key").unwrap();
    broadcast_map.send("test_key", 100).unwrap();
    assert_eq!(rec2.recv().await, Ok(100));
}
#[tokio::test]
pub async fn test_broadcast_map_unsubscribe_receiver_count() {
    let broadcast_map: BroadcastMap<String> = BroadcastMap::new();
    broadcast_map.insert("test_key", 10);
    let _rec1: BroadcastMapReceiver<String> = broadcast_map.subscribe("test_key").unwrap();
    let _rec2: BroadcastMapReceiver<String> = broadcast_map.subscribe("test_key").unwrap();
    assert_eq!(broadcast_map.receiver_count("test_key"), Some(2));
    let removed: Option<Broadcast<String>> = broadcast_map.unsubscribe("test_key");
    assert!(removed.is_some());
    assert_eq!(broadcast_map.receiver_count("test_key"), None);
}
#[tokio::test]
pub async fn test_broadcast_map_send() {
    let broadcast_map: BroadcastMap<u128> = BroadcastMap::new();
    broadcast_map.insert("test_key", 10);
    let mut rec1: BroadcastMapReceiver<u128> = broadcast_map.subscribe("test_key").unwrap();
    let mut rec2: BroadcastMapReceiver<u128> = broadcast_map.subscribe("test_key").unwrap();
    let count: Option<ReceiverCount> = broadcast_map.send("test_key", 42);
    assert_eq!(count, Some(2));
    assert_eq!(rec1.recv().await, Ok(42));
    assert_eq!(rec2.recv().await, Ok(42));
    let non_existent: Option<ReceiverCount> = broadcast_map.send("non_existent_key", 100);
    assert_eq!(non_existent, None);
}
```
# Path: hyperlane-broadcast/src/broadcast/const.rs
```rust
pub const DEFAULT_BROADCAST_SENDER_CAPACITY: usize = 1024;
```
# Path: hyperlane-broadcast/src/broadcast/trait.rs
```rust
use crate::*;
pub trait BroadcastTrait: Clone + Debug {}
```
# Path: hyperlane-broadcast/src/broadcast/mod.rs
```rust
mod r#const;
mod r#impl;
mod r#struct;
#[cfg(test)]
mod test;
mod r#trait;
mod r#type;
pub use {r#const::*, r#struct::*, r#trait::*, r#type::*};
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
# Path: hyperlane-broadcast/src/broadcast/struct.rs
```rust
use crate::*;
#[derive(Clone, Debug)]
pub struct Broadcast<T: BroadcastTrait>(pub(super) BroadcastSender<T>);
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
# Path: hyperlane-broadcast/src/broadcast/test.rs
```rust
use crate::*;
#[tokio::test]
pub async fn test_broadcast() {
    let broadcast: Broadcast<usize> = Broadcast::new(10);
    let mut rec1: BroadcastReceiver<usize> = broadcast.subscribe();
    let mut rec2: BroadcastReceiver<usize> = broadcast.subscribe();
    broadcast.send(20).unwrap();
    assert_eq!(rec1.recv().await, Ok(20));
    assert_eq!(rec2.recv().await, Ok(20));
}
```
# Path: hyperlane-plugin-websocket/README.md
## hyperlane-plugin-websocket
[Official Documentation](https://docs.ltpp.vip/hyperlane-plugin-websocket/)
[Api Docs](https://docs.rs/hyperlane-plugin-websocket/latest/)
> A WebSocket plugin for the Hyperlane framework, providing robust WebSocket communication capabilities and integrating with hyperlane-broadcast for efficient message dissemination.
## Installation
To use this crate, you can run cmd:
```shell
cargo add hyperlane-plugin-websocket
```
## Contact
# Path: hyperlane-plugin-websocket/src/const.rs
```rust
pub(crate) const POINT_TO_POINT_KEY: &str = "ptp-";
pub(crate) const POINT_TO_GROUP_KEY: &str = "ptg-";
```
# Path: hyperlane-plugin-websocket/src/lib.rs
```rust
mod r#const;
mod r#enum;
mod r#impl;
mod r#struct;
#[cfg(test)]
mod test;
mod r#trait;
pub use {r#enum::*, r#struct::*};
use {r#const::*, r#trait::*};
use std::{
    convert::Infallible,
    net::{IpAddr, Ipv4Addr, Ipv6Addr, SocketAddr},
    num::{
        NonZeroI8, NonZeroI16, NonZeroI32, NonZeroI64, NonZeroI128, NonZeroIsize, NonZeroU8,
        NonZeroU16, NonZeroU32, NonZeroU64, NonZeroU128, NonZeroUsize,
    },
};
#[cfg(test)]
use std::{sync::OnceLock, time::Duration};
#[cfg(test)]
use tokio::{spawn, time::sleep};
use {
    hyperlane::{
        tokio::sync::broadcast::{Receiver, error::SendError},
        *,
    },
    hyperlane_broadcast::*,
};
```
# Path: hyperlane-plugin-websocket/src/trait.rs
```rust
pub trait BroadcastTypeTrait: ToString + PartialOrd + Clone {}
```
# Path: hyperlane-plugin-websocket/src/impl.rs
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
impl<B> Default for BroadcastType<B>
where
    B: BroadcastTypeTrait,
{
    #[inline(always)]
    fn default() -> Self {
        BroadcastType::Unknown
    }
}
impl<B> BroadcastType<B>
where
    B: BroadcastTypeTrait,
{
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
impl<'a, B> WebSocketConfig<'a, B>
where
    B: BroadcastTypeTrait,
{
    #[inline(always)]
    pub fn new(context: &'a mut Context) -> Self {
        Self {
            context,
            capacity: DEFAULT_BROADCAST_SENDER_CAPACITY,
            broadcast_type: BroadcastType::default(),
            connected_hook: default_server_hook_handler(),
            request_hook: default_server_hook_handler(),
            sended_hook: default_server_hook_handler(),
            closed_hook: default_server_hook_handler(),
        }
    }
}
impl<'a, B> WebSocketConfig<'a, B>
where
    B: BroadcastTypeTrait,
{
    #[inline(always)]
    pub fn set_capacity(mut self, capacity: Capacity) -> Self {
        self.capacity = capacity;
        self
    }
    #[inline(always)]
    pub fn set_context(mut self, context: &'a mut Context) -> Self {
        self.context = context;
        self
    }
    #[inline(always)]
    pub fn set_broadcast_type(mut self, broadcast_type: BroadcastType<B>) -> Self {
        self.broadcast_type = broadcast_type;
        self
    }
    #[inline(always)]
    pub fn get_context(&mut self) -> &mut Context {
        self.context
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
    fn subscribe_unwrap_or_insert<B>(
        &self,
        broadcast_type: BroadcastType<B>,
        capacity: Capacity,
    ) -> BroadcastMapReceiver<Vec<u8>>
    where
        B: BroadcastTypeTrait,
    {
        let key: String = BroadcastType::get_key(broadcast_type);
        self.broadcast_map.subscribe_or_insert(&key, capacity)
    }
    #[inline(always)]
    fn point_to_point<B>(
        &self,
        key1: &B,
        key2: &B,
        capacity: Capacity,
    ) -> BroadcastMapReceiver<Vec<u8>>
    where
        B: BroadcastTypeTrait,
    {
        self.subscribe_unwrap_or_insert(
            BroadcastType::PointToPoint(key1.clone(), key2.clone()),
            capacity,
        )
    }
    #[inline(always)]
    fn point_to_group<B>(&self, key: &B, capacity: Capacity) -> BroadcastMapReceiver<Vec<u8>>
    where
        B: BroadcastTypeTrait,
    {
        self.subscribe_unwrap_or_insert(BroadcastType::PointToGroup(key.clone()), capacity)
    }
    #[inline(always)]
    pub fn receiver_count<B>(&self, broadcast_type: BroadcastType<B>) -> ReceiverCount
    where
        B: BroadcastTypeTrait,
    {
        let key: String = BroadcastType::get_key(broadcast_type);
        self.broadcast_map.receiver_count(&key).unwrap_or(0)
    }
    #[inline(always)]
    pub fn receiver_count_before_connected<B>(
        &self,
        broadcast_type: BroadcastType<B>,
    ) -> ReceiverCount
    where
        B: BroadcastTypeTrait,
    {
        let count: ReceiverCount = self.receiver_count(broadcast_type);
        count.clamp(0, ReceiverCount::MAX - 1) + 1
    }
    #[inline(always)]
    pub fn receiver_count_after_closed<B>(&self, broadcast_type: BroadcastType<B>) -> ReceiverCount
    where
        B: BroadcastTypeTrait,
    {
        let count: ReceiverCount = self.receiver_count(broadcast_type);
        count.clamp(1, ReceiverCount::MAX) - 1
    }
    #[inline(always)]
    pub fn try_send<T, B>(
        &self,
        broadcast_type: BroadcastType<B>,
        data: T,
    ) -> Result<Option<ReceiverCount>, SendError<Vec<u8>>>
    where
        T: Into<Vec<u8>>,
        B: BroadcastTypeTrait,
    {
        let key: String = BroadcastType::get_key(broadcast_type);
        self.broadcast_map.try_send(&key, data.into())
    }
    #[inline(always)]
    pub fn send<T, B>(&self, broadcast_type: BroadcastType<B>, data: T) -> Option<ReceiverCount>
    where
        T: Into<Vec<u8>>,
        B: BroadcastTypeTrait,
    {
        self.try_send(broadcast_type, data).unwrap()
    }
    pub async fn run<B>(&self, mut websocket_config: WebSocketConfig<'_, B>)
    where
        B: BroadcastTypeTrait,
    {
        let capacity: Capacity = websocket_config.get_capacity();
        let broadcast_type: BroadcastType<B> = websocket_config.get_broadcast_type().clone();
        let connected_hook: ServerHookHandler = websocket_config.get_connected_hook().clone();
        let sended_hook: ServerHookHandler = websocket_config.get_sended_hook().clone();
        let request_hook: ServerHookHandler = websocket_config.get_request_hook().clone();
        let closed_hook: ServerHookHandler = websocket_config.get_closed_hook().clone();
        let ctx: &mut Context = websocket_config.get_context();
        let mut receiver: Receiver<Vec<u8>> = match &broadcast_type {
            BroadcastType::PointToPoint(key1, key2) => self.point_to_point(key1, key2, capacity),
            BroadcastType::PointToGroup(key) => self.point_to_group(key, capacity),
            BroadcastType::Unknown => panic!("BroadcastType must be PointToPoint or PointToGroup"),
        };
        let key: String = BroadcastType::get_key(broadcast_type);
        connected_hook(ctx).await;
        loop {
            tokio::select! {
                request_res = ctx.ws_from_stream() => {
                    let mut is_err: bool = false;
                    if request_res.is_ok() {
                        request_hook(ctx).await;
                    } else {
                        is_err = true;
                        closed_hook(ctx).await;
                    }
                    if ctx.get_aborted() {
                        continue;
                    }
                    if ctx.get_closed() {
                        break;
                    }
                    let body: ResponseBody = ctx.get_response().get_body().clone();
                    is_err = self.broadcast_map.try_send(&key, body).is_err() || is_err;
                    sended_hook(ctx).await;
                    if is_err || ctx.get_closed() {
                        break;
                    }
                },
                msg_res = receiver.recv() => {
                    if let Ok(msg) = &msg_res {
                        if ctx.try_send_body_list_with_data(&WebSocketFrame::create_frame_list(msg)).await.is_ok() {
                            continue;
                        } else {
                            break;
                        }
                    }
                    break;
                }
            }
        }
        ctx.set_aborted(true).set_closed(true);
    }
}
```
# Path: hyperlane-plugin-websocket/src/struct.rs
```rust
use crate::*;
#[derive(Clone, Debug, Default)]
pub struct WebSocket {
    pub(super) broadcast_map: BroadcastMap<Vec<u8>>,
}
pub struct WebSocketConfig<'a, B: BroadcastTypeTrait> {
    pub(super) context: &'a mut Context,
    pub(super) capacity: Capacity,
    pub(super) broadcast_type: BroadcastType<B>,
    pub(super) connected_hook: ServerHookHandler,
    pub(super) request_hook: ServerHookHandler,
    pub(super) sended_hook: ServerHookHandler,
    pub(super) closed_hook: ServerHookHandler,
}
```
# Path: hyperlane-plugin-websocket/src/test.rs
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
    async fn new(ctx: &mut Context) -> Self {
        let error: PanicData = ctx.try_get_task_panic_data().unwrap_or_default();
        let response_body: String = error.to_string();
        let content_type: String = ContentType::format_content_type_with_charset(TEXT_PLAIN, UTF8);
        Self {
            response_body,
            content_type,
        }
    }
    async fn handle(self, ctx: &mut Context) {
        ctx.get_mut_response()
            .set_version(HttpVersion::Http1_1)
            .set_status_code(500)
            .clear_headers()
            .set_header(SERVER, HYPERLANE)
            .set_header(CONTENT_TYPE, &self.content_type)
            .set_body(&self.response_body);
        if ctx.try_send().await.is_err() {
            ctx.set_aborted(true).set_closed(true);
        }
    }
}
struct RequestErrorHook {
    response_status_code: ResponseStatusCode,
    response_body: String,
}
impl ServerHook for RequestErrorHook {
    async fn new(ctx: &mut Context) -> Self {
        let request_error: RequestError = ctx.try_get_request_error_data().unwrap_or_default();
        Self {
            response_status_code: request_error.get_http_status_code(),
            response_body: request_error.to_string(),
        }
    }
    async fn handle(self, ctx: &mut Context) {
        ctx.get_mut_response()
            .set_version(HttpVersion::Http1_1)
            .set_status_code(self.response_status_code)
            .set_body(self.response_body);
        if ctx.try_send().await.is_err() {
            ctx.set_aborted(true).set_closed(true);
        }
    }
}
struct RequestMiddleware {
    socket_addr: String,
}
impl ServerHook for RequestMiddleware {
    async fn new(ctx: &mut Context) -> Self {
        let mut socket_addr: String = String::new();
        if let Some(stream) = ctx.try_get_stream().as_ref() {
            socket_addr = stream
                .read()
                .await
                .peer_addr()
                .map(|data| data.to_string())
                .unwrap_or_default();
        }
        Self { socket_addr }
    }
    async fn handle(self, ctx: &mut Context) {
        ctx.get_mut_response()
            .set_version(HttpVersion::Http1_1)
            .set_status_code(200)
            .set_header(SERVER, HYPERLANE)
            .set_header(CONNECTION, KEEP_ALIVE)
            .set_header(CONTENT_TYPE, TEXT_PLAIN)
            .set_header(ACCESS_CONTROL_ALLOW_ORIGIN, WILDCARD_ANY)
            .set_header("SocketAddr", &self.socket_addr);
    }
}
struct UpgradeHook;
impl ServerHook for UpgradeHook {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &mut Context) {
        if !ctx.get_request().is_ws_upgrade_type() {
            return;
        }
        if let Some(key) = &ctx.get_request().try_get_header_back(SEC_WEBSOCKET_KEY) {
            let accept_key: String = WebSocketFrame::generate_accept_key(key);
            ctx.get_mut_response()
                .set_version(HttpVersion::Http1_1)
                .set_status_code(101)
                .set_header(UPGRADE, WEBSOCKET)
                .set_header(CONNECTION, UPGRADE)
                .set_header(SEC_WEBSOCKET_ACCEPT, &accept_key)
                .set_body(vec![]);
            if ctx.try_send().await.is_err() {
                ctx.set_aborted(true).set_closed(true);
            }
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
    async fn new(ctx: &mut Context) -> Self {
        let group_name: String = ctx.try_get_route_param("group_name").unwrap_or_default();
        let group_broadcast_type: BroadcastType<String> = BroadcastType::PointToGroup(group_name);
        let receiver_count: ReceiverCount =
            get_broadcast_map().receiver_count(group_broadcast_type.clone());
        let my_name: String = ctx.try_get_route_param("my_name").unwrap_or_default();
        let your_name: String = ctx.try_get_route_param("your_name").unwrap_or_default();
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
    async fn handle(self, _ctx: &mut Context) {
        get_broadcast_map()
            .try_send(self.group_broadcast_type, self.data.clone())
            .unwrap_or_else(|err| {
                println!("[connected_hook] send group error => {:?}", err.to_string());
                None
            });
        get_broadcast_map()
            .try_send(self.private_broadcast_type, self.data)
            .unwrap_or_else(|err| {
                println!(
                    "[connected_hook] send private error => {:?}",
                    err.to_string()
                );
                None
            });
        println!(
            "[connected_hook] receiver_count => {:?}",
            self.receiver_count
        );
        Server::flush_stdout();
    }
}
struct SendedHook {
    msg: String,
}
impl ServerHook for SendedHook {
    async fn new(ctx: &mut Context) -> Self {
        let msg: String = ctx.get_response().get_body_string();
        Self { msg }
    }
    async fn handle(self, _ctx: &mut Context) {
        println!("[sended_hook] msg => {}", self.msg);
        Server::flush_stdout();
    }
}
struct GroupChatRequestHook {
    body: RequestBody,
    receiver_count: ReceiverCount,
}
impl ServerHook for GroupChatRequestHook {
    async fn new(ctx: &mut Context) -> Self {
        let group_name: String = ctx.try_get_route_param("group_name").unwrap();
        let key: BroadcastType<String> = BroadcastType::PointToGroup(group_name);
        let mut receiver_count: ReceiverCount = get_broadcast_map().receiver_count(key.clone());
        let mut body: RequestBody = ctx.get_request().get_body().clone();
        if body.is_empty() {
            receiver_count = get_broadcast_map().receiver_count_after_closed(key);
            body = format!("receiver_count => {receiver_count:?}").into();
        }
        Self {
            body,
            receiver_count,
        }
    }
    async fn handle(self, ctx: &mut Context) {
        ctx.get_mut_response().set_body(&self.body);
        println!("[group_chat] receiver_count => {:?}", self.receiver_count);
        Server::flush_stdout();
    }
}
struct GroupClosedHook {
    body: String,
    receiver_count: ReceiverCount,
}
impl ServerHook for GroupClosedHook {
    async fn new(ctx: &mut Context) -> Self {
        let group_name: String = ctx.try_get_route_param("group_name").unwrap();
        let key: BroadcastType<String> = BroadcastType::PointToGroup(group_name);
        let receiver_count: ReceiverCount =
            get_broadcast_map().receiver_count_after_closed(key.clone());
        let body: String = format!("receiver_count => {receiver_count:?}");
        Self {
            body,
            receiver_count,
        }
    }
    async fn handle(self, ctx: &mut Context) {
        ctx.get_mut_response().set_body(&self.body);
        println!("[group_closed] receiver_count => {:?}", self.receiver_count);
        Server::flush_stdout();
    }
}
struct GroupChat;
impl ServerHook for GroupChat {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &mut Context) {
        let group_name: String = ctx.try_get_route_param("group_name").unwrap();
        let key: BroadcastType<String> = BroadcastType::PointToGroup(group_name);
        let config: WebSocketConfig<String> = WebSocketConfig::new(ctx)
            .set_capacity(1024)
            .set_broadcast_type(key)
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
    async fn new(ctx: &mut Context) -> Self {
        let my_name: String = ctx.try_get_route_param("my_name").unwrap();
        let your_name: String = ctx.try_get_route_param("your_name").unwrap();
        let key: BroadcastType<String> = BroadcastType::PointToPoint(my_name, your_name);
        let mut receiver_count: ReceiverCount = get_broadcast_map().receiver_count(key.clone());
        let mut body: RequestBody = ctx.get_request().get_body().clone();
        if body.is_empty() {
            receiver_count = get_broadcast_map().receiver_count_after_closed(key);
            body = format!("receiver_count => {receiver_count:?}").into();
        }
        Self {
            body,
            receiver_count,
        }
    }
    async fn handle(self, ctx: &mut Context) {
        ctx.get_mut_response().set_body(&self.body);
        println!("[private_chat] receiver_count => {:?}", self.receiver_count);
        Server::flush_stdout();
    }
}
struct PrivateClosedHook {
    body: String,
    receiver_count: ReceiverCount,
}
impl ServerHook for PrivateClosedHook {
    async fn new(ctx: &mut Context) -> Self {
        let my_name: String = ctx.try_get_route_param("my_name").unwrap();
        let your_name: String = ctx.try_get_route_param("your_name").unwrap();
        let key: BroadcastType<String> = BroadcastType::PointToPoint(my_name, your_name);
        let receiver_count: ReceiverCount = get_broadcast_map().receiver_count_after_closed(key);
        let body: String = format!("receiver_count => {receiver_count:?}");
        Self {
            body,
            receiver_count,
        }
    }
    async fn handle(self, ctx: &mut Context) {
        ctx.get_mut_response().set_body(&self.body);
        println!(
            "[private_closed] receiver_count => {:?}",
            self.receiver_count
        );
        Server::flush_stdout();
    }
}
struct PrivateChat;
impl ServerHook for PrivateChat {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &mut Context) {
        let my_name: String = ctx.try_get_route_param("my_name").unwrap();
        let your_name: String = ctx.try_get_route_param("your_name").unwrap();
        let key: BroadcastType<String> = BroadcastType::PointToPoint(my_name, your_name);
        let config: WebSocketConfig<String> = WebSocketConfig::new(ctx)
            .set_capacity(1024)
            .set_broadcast_type(key)
            .set_connected_hook::<ConnectedHook>()
            .set_request_hook::<PrivateChatRequestHook>()
            .set_sended_hook::<SendedHook>()
            .set_closed_hook::<PrivateClosedHook>();
        get_broadcast_map().run(config).await;
    }
}
#[tokio::test]
async fn main() {
    let mut server: Server = Server::default();
    server.task_panic::<TaskPanicHook>();
    server.request_error::<RequestErrorHook>();
    server.request_middleware::<RequestMiddleware>();
    server.request_middleware::<UpgradeHook>();
    server.route::<GroupChat>("/{group_name}");
    server.route::<PrivateChat>("/{my_name}/{your_name}");
    let server_control_hook_1: ServerControlHook = server.run().await.unwrap_or_default();
    let server_control_hook_2: ServerControlHook = server_control_hook_1.clone();
    spawn(async move {
        sleep(Duration::from_secs(60)).await;
        server_control_hook_2.shutdown().await;
    });
    server_control_hook_1.wait().await;
}
```
# Path: hyperlane-plugin-websocket/src/enum.rs
```rust
use crate::*;
#[derive(Clone, Copy, Debug, Eq, Hash, PartialEq)]
pub enum BroadcastType<T: BroadcastTypeTrait> {
    PointToPoint(T, T),
    PointToGroup(T),
    Unknown,
}
```
# Path: hyperlane-macros/README.md
## hyperlane-macros
[Official Documentation](https://docs.ltpp.vip/hyperlane-macros/)
[Api Docs](https://docs.rs/hyperlane-macros/latest/)
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
- `#[get_method]` - GET method handler
- `#[post_method]` - POST method handler
- `#[put_method]` - PUT method handler
- `#[delete_method]` - DELETE method handler
- `#[patch_method]` - PATCH method handler
- `#[head_method]` - HEAD method handler
- `#[options_method]` - OPTIONS method handler
- `#[connect_method]` - CONNECT method handler
- `#[trace_method]` - TRACE method handler
- `#[unknown_method]` - Unknown method handler
### HTTP Version Macros
- `#[http0_9_version]` - HTTP/0.9 check, ensures function only executes for HTTP/0.9 protocol requests
- `#[http1_0_version]` - HTTP/1.0 check, ensures function only executes for HTTP/1.0 protocol requests
- `#[http1_1_version]` - HTTP/1.1 check, ensures function only executes for HTTP/1.1 protocol requests
- `#[http2_version]` - HTTP/2 check, ensures function only executes for HTTP/2 protocol requests
- `#[http3_version]` - HTTP/3 check, ensures function only executes for HTTP/3 protocol requests
- `#[http1_1_or_higher_version]` - HTTP/1.1 or higher version check, ensures function only executes for HTTP/1.1 or newer protocol versions
- `#[http_version]` - HTTP check, ensures function only executes for standard HTTP requests
- `#[unknown_version]` - Unknown version check, ensures function only executes for requests with unknown HTTP versions
### Upgrade type Macros
- `#[ws_upgrade_type]` - WebSocket check, ensures function only executes for WebSocket upgrade requests
- `#[h2c_upgrade_type]` - HTTP/2 Cleartext check, ensures function only executes for HTTP/2 cleartext requests
- `#[tls_upgrade_type]` - TLS check, ensures function only executes for TLS-secured connections
- `#[unknown_upgrade_type]` - Unknown upgrade type check, ensures function only executes for requests with unknown upgrade types
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
- `#[prologue_hooks(method::expression, another::method)]` - Supports method expressions for advanced hook configurations
- `#[epilogue_hooks(method::expression, another::method)]` - Supports method expressions for advanced hook configurations
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
- `#[http_from_stream]` - Wraps function body with HTTP stream processing. The function body only executes if data is successfully read from the HTTP stream.
- `#[http_from_stream(variable_name)]` - Wraps function body with HTTP stream processing, storing data in specified variable name.
- `#[ws_from_stream]` - Wraps function body with WebSocket stream processing. The function body only executes if data is successfully read from the WebSocket stream.
- `#[ws_from_stream(variable_name)]` - Wraps function body with WebSocket stream processing, storing data in specified variable name.
### Response Header Macros
### Response Body Macros
### Route Macros
- `#[route("path")]` - Register a route handler for the given path using the default server (Prerequisite: requires the #[hyperlane(server: Server)] macro)
### Helper Tips
- **Request related macros** (data extraction) use **`get`** operations - they retrieve/query data from the request
- **Response related macros** (data setting) use **`set`** operations - they assign/configure response data
- **Hook macros** For hook-related macros that support an `order` parameter, if `order` is not specified, the hook will have higher priority than hooks with a specified `order` (applies only to macros like `#[request_middleware]`, `#[response_middleware]`, `#[task_panic]`, `#[request_error]`)
- **Multi-parameter support** Most data extraction macros support multiple parameters in a single call (e.g., `#[request_body(var1, var2)]`, `#[request_query("k1" => v1, "k2" => v2)]`). This reduces macro repetition and improves code readability.
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
#[derive(Clone, Debug, Deserialize, Serialize)]
struct TestData {
    name: String,
    age: u32,
}
#[task_panic]
#[task_panic(1)]
#[task_panic("2")]
struct TakPanicHook;
impl ServerHook for TakPanicHook {
    async fn new(_ctx: &mut Context) -> Self {
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
    async fn handle(self, ctx: &mut Context) {}
}
#[request_error]
#[request_error(1)]
#[request_error("2")]
struct RequestErrorHook;
impl ServerHook for RequestErrorHook {
    async fn new(_ctx: &mut Context) -> Self {
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
    async fn handle(self, ctx: &mut Context) {}
}
#[request_middleware]
struct RequestMiddleware;
impl ServerHook for RequestMiddleware {
    async fn new(_ctx: &mut Context) -> Self {
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
    async fn handle(self, ctx: &mut Context) {}
}
#[request_middleware(1)]
struct UpgradeHook;
impl ServerHook for UpgradeHook {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[epilogue_macros(
        ws_upgrade_type,
        response_body(&vec![]),
        response_status_code(101),
        response_header(UPGRADE => WEBSOCKET),
        response_header(CONNECTION => UPGRADE),
        response_header(SEC_WEBSOCKET_ACCEPT => &WebSocketFrame::generate_accept_key(ctx.get_request().get_header_back(SEC_WEBSOCKET_KEY))),
        response_header(STEP => "upgrade_hook"),
        send
    )]
    async fn handle(self, ctx: &mut Context) {}
}
#[request_middleware(2)]
struct ConnectedHook;
impl ServerHook for ConnectedHook {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[response_status_code(200)]
    #[response_header(SERVER => HYPERLANE)]
    #[response_version(HttpVersion::Http1_1)]
    #[response_header(ACCESS_CONTROL_ALLOW_ORIGIN => WILDCARD_ANY)]
    #[response_header(STEP => "connected_hook")]
    async fn handle(self, ctx: &mut Context) {}
}
#[response_middleware]
struct ResponseMiddleware1;
impl ServerHook for ResponseMiddleware1 {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[response_header(STEP => "response_middleware_1")]
    async fn handle(self, ctx: &mut Context) {}
}
#[response_middleware(2)]
struct ResponseMiddleware2;
impl ServerHook for ResponseMiddleware2 {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        reject(ctx.get_request().get_upgrade_type().is_ws()),
        response_header(STEP => "response_middleware_2")
    )]
    #[epilogue_macros(try_send, flush)]
    async fn handle(self, ctx: &mut Context) {}
}
#[response_middleware("3")]
struct ResponseMiddleware3;
impl ServerHook for ResponseMiddleware3 {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        ws_upgrade_type,
        response_header(STEP => "response_middleware_3")
    )]
    #[epilogue_macros(try_send, flush)]
    async fn handle(self, ctx: &mut Context) {}
}
struct PrologueHooks;
impl ServerHook for PrologueHooks {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[get_method]
    #[http_version]
    async fn handle(self, _ctx: &mut Context) {}
}
struct EpilogueHooks;
impl ServerHook for EpilogueHooks {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[response_status_code(200)]
    async fn handle(self, ctx: &mut Context) {}
}
async fn prologue_hooks_fn(ctx: &mut Context) {
    let hook = PrologueHooks::new(ctx).await;
    hook.handle(ctx).await;
}
async fn epilogue_hooks_fn(ctx: &mut Context) {
    let hook = EpilogueHooks::new(ctx).await;
    hook.handle(ctx).await;
}
#[route("/response")]
struct Response;
impl ServerHook for Response {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[response_body(&RESPONSE_DATA)]
    #[response_reason_phrase(CUSTOM_REASON)]
    #[response_status_code(CUSTOM_STATUS_CODE)]
    #[response_header(CUSTOM_HEADER_NAME => CUSTOM_HEADER_VALUE)]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/connect")]
struct ConnectMethod;
impl ServerHook for ConnectMethod {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(connect_method, response_body("connect"))]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/delete")]
struct DeleteMethod;
impl ServerHook for DeleteMethod {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(delete_method, response_body("delete"))]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/head")]
struct HeadMethod;
impl ServerHook for HeadMethod {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(head_method, response_body("head"))]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/options")]
struct OptionsMethod;
impl ServerHook for OptionsMethod {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(options_method, response_body("options"))]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/patch")]
struct PatchMethod;
impl ServerHook for PatchMethod {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(patch_method, response_body("patch"))]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/put")]
struct PutMethod;
impl ServerHook for PutMethod {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(put_method, response_body("put"))]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/trace")]
struct TraceMethod;
impl ServerHook for TraceMethod {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(trace_method, response_body("trace"))]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/get_post_method")]
struct GetPostMethod;
impl ServerHook for GetPostMethod {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[closed]
    #[prologue_macros(
        http_version,
        methods(get, post),
        response_body("get_post_method"),
        response_status_code(200),
        response_reason_phrase("OK")
    )]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/get_method")]
struct GetMethod;
impl ServerHook for GetMethod {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(ws_upgrade_type, get_method, response_body("get_method"))]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/post_method")]
struct PostMethod;
impl ServerHook for PostMethod {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(post_method, response_body("post_method"), try_send)]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/unknown_method")]
struct UnknownMethod;
impl ServerHook for UnknownMethod {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(unknown_method, response_body("unknown_method"), try_send)]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/http0_9_version")]
struct Http09Version;
impl ServerHook for Http09Version {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(http0_9_version, response_body("http0_9_version"))]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/http1_0_version")]
struct Http10Version;
impl ServerHook for Http10Version {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(http1_0_version, response_body("http1_0_version"))]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/http1_1_version")]
struct Http11Version;
impl ServerHook for Http11Version {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(http1_1_version, response_body("http1_1_version"))]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/http2_version")]
struct Http2Version;
impl ServerHook for Http2Version {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(http2_version, response_body("http2_version"))]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/http3_version")]
struct Http3Version;
impl ServerHook for Http3Version {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(http3_version, response_body("http3_version"))]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/http1_1_or_higher_version")]
struct Http11OrHigher;
impl ServerHook for Http11OrHigher {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(http1_1_or_higher_version, response_body("http1_1_or_higher_version"))]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/http_version")]
struct HttpAllVersion;
impl ServerHook for HttpAllVersion {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(http_version, response_body("http_version"))]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/unknown_version")]
struct UnknownVersion;
impl ServerHook for UnknownVersion {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(unknown_version, response_body("unknown_version"))]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/ws_upgrade_type")]
struct WsUpgradeType;
impl ServerHook for WsUpgradeType {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[ws_upgrade_type]
    async fn handle(self, _ctx: &mut Context) {}
}
#[route("/h2c_upgrade_type")]
struct H2cUpgradeType;
impl ServerHook for H2cUpgradeType {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(h2c_upgrade_type, response_body("h2c_upgrade_type"))]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/tls_upgrade_type")]
struct Tls;
impl ServerHook for Tls {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(tls_upgrade_type, response_body("tls_upgrade_type"))]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/unknown_upgrade_type")]
struct UnknownUpgradeType;
impl ServerHook for UnknownUpgradeType {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(unknown_upgrade_type, response_body("unknown_upgrade_type"))]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/ws1")]
struct Websocket1;
impl ServerHook for Websocket1 {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[ws_upgrade_type]
    #[ws_from_stream]
    async fn handle(self, ctx: &mut Context) {
        let body: &RequestBody = ctx.get_request().get_body();
        let body_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(body);
        ctx.send_body_list_with_data(&body_list).await;
    }
}
#[route("/ws2")]
struct Websocket2;
impl ServerHook for Websocket2 {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[ws_upgrade_type]
    #[ws_from_stream(request)]
    async fn handle(self, ctx: &mut Context) {
        let body: &RequestBody = request.get_body();
        let body_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(body);
        ctx.send_body_list_with_data(&body_list).await;
    }
}
#[route("/ws3")]
struct Websocket3;
impl ServerHook for Websocket3 {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[ws_upgrade_type]
    #[ws_from_stream(request)]
    async fn handle(self, ctx: &mut Context) {
        let body: &RequestBody = request.get_body();
        let body_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(body);
        ctx.send_body_list_with_data(&body_list).await;
    }
}
#[route("/ws4")]
struct Websocket4;
impl ServerHook for Websocket4 {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[ws_upgrade_type]
    #[ws_from_stream(request)]
    async fn handle(self, ctx: &mut Context) {
        let body: &RequestBody = request.get_body();
        let body_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(body);
        ctx.send_body_list_with_data(&body_list).await;
    }
}
#[route("/ws5")]
struct Websocket5;
impl ServerHook for Websocket5 {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[ws_upgrade_type]
    #[ws_from_stream]
    async fn handle(self, ctx: &mut Context) {
        let body: &RequestBody = ctx.get_request().get_body();
        let body_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(body);
        ctx.send_body_list_with_data(&body_list).await;
    }
}
#[route("/hook")]
struct Hook;
impl ServerHook for Hook {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_hooks(prologue_hooks_fn)]
    #[epilogue_hooks(epilogue_hooks_fn)]
    #[response_body("Testing hook macro")]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/attributes")]
struct Attributes;
impl ServerHook for Attributes {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[response_body(&format!("request attributes: {request_attributes:?}"))]
    #[attributes(request_attributes)]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/route_params/:test")]
struct RouteParams;
impl ServerHook for RouteParams {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[response_body(&format!("request route params: {request_route_params:?}"))]
    #[route_params(request_route_params)]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/route_param_option/:test")]
struct RouteParamOption;
impl ServerHook for RouteParamOption {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[response_body(&format!("route param: {request_route_param_option1:?} {request_route_param_option2:?} {request_route_param_option3:?}"))]
    #[route_param_option("test1" => request_route_param_option1)]
    #[route_param_option("test2" => request_route_param_option2, "test3" => request_route_param_option3)]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/route_param/:test")]
struct RouteParam;
impl ServerHook for RouteParam {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[response_body(&format!("route param: {request_route_param1} {request_route_param2} {request_route_param3}"))]
    #[route_param("test1" => request_route_param1)]
    #[route_param("test2" => request_route_param2, "test3" => request_route_param3)]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/host")]
struct Host;
impl ServerHook for Host {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[host("localhost")]
    #[epilogue_macros(
        response_body("host string literal: localhost"),
        send,
        http_from_stream
    )]
    #[prologue_macros(response_body("host string literal: localhost"), send)]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/request_query_option")]
struct RequestQueryOption;
impl ServerHook for RequestQueryOption {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[epilogue_macros(
        request_query_option("test" => request_query_option),
        response_body(&format!("request query: {request_query_option:?}")),
        send,
        http_from_stream
    )]
    #[prologue_macros(
        request_query_option("test" => request_query_option),
        response_body(&format!("request query: {request_query_option:?}")),
        send
    )]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/request_query")]
struct RequestQuery;
impl ServerHook for RequestQuery {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[epilogue_macros(
        request_query("test" => request_query),
        response_body(&format!("request query: {request_query}")),
        send,
        http_from_stream
    )]
    #[prologue_macros(
        request_query("test" => request_query),
        response_body(&format!("request query: {request_query}")),
        send
    )]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/request_header_option")]
struct RequestHeaderOption;
impl ServerHook for RequestHeaderOption {
    async fn new(_ctx: &mut Context) -> Self {
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
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/request_header")]
struct RequestHeader;
impl ServerHook for RequestHeader {
    async fn new(_ctx: &mut Context) -> Self {
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
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/request_querys")]
struct RequestQuerys;
impl ServerHook for RequestQuerys {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[epilogue_macros(
        request_querys(request_querys),
        response_body(&format!("request querys: {request_querys:?}")),
        send,
        http_from_stream(_request)
    )]
    #[prologue_macros(
        request_querys(request_querys),
        response_body(&format!("request querys: {request_querys:?}")),
        send
    )]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/request_headers")]
struct RequestHeaders;
impl ServerHook for RequestHeaders {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[epilogue_macros(
        request_headers(request_headers),
        response_body(&format!("request headers: {request_headers:?}")),
        send,
        http_from_stream(_request)
    )]
    #[prologue_macros(
        request_headers(request_headers),
        response_body(&format!("request headers: {request_headers:?}")),
        send
    )]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/request_body")]
struct RequestBodyRoute;
impl ServerHook for RequestBodyRoute {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[response_body(&format!("raw body: {raw_body:?}"))]
    #[request_body(raw_body)]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/reject_host")]
struct RejectHost;
impl ServerHook for RejectHost {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        reject_host("filter.localhost"),
        response_body("host filter string literal")
    )]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/attribute_option")]
struct AttributeOption;
impl ServerHook for AttributeOption {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[response_body(&format!("request attribute: {request_attribute_option:?}"))]
    #[attribute_option(TEST_ATTRIBUTE_KEY => request_attribute_option: TestData)]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/attribute")]
struct Attribute;
impl ServerHook for Attribute {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[response_body(&format!("request attribute: {request_attribute:?}"))]
    #[attribute(TEST_ATTRIBUTE_KEY => request_attribute: TestData)]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/request_body_json_result")]
struct RequestBodyJsonResult;
impl ServerHook for RequestBodyJsonResult {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[response_body(&format!("request data: {request_data_result:?}"))]
    #[request_body_json_result(request_data_result: TestData)]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/request_body_json")]
struct RequestBodyJson;
impl ServerHook for RequestBodyJson {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[response_body(&format!("request data: {request_data_result:?}"))]
    #[request_body_json(request_data_result: TestData)]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/referer")]
struct Referer;
impl ServerHook for Referer {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        referer("http://localhost"),
        response_body("referer string literal: http://localhost")
    )]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/reject_referer")]
struct RejectReferer;
impl ServerHook for RejectReferer {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        reject_referer("http://localhost"),
        response_body("referer filter string literal")
    )]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/cookies")]
struct Cookies;
impl ServerHook for Cookies {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[response_body(&format!("All cookies: {cookie_value:?}"))]
    #[request_cookies(cookie_value)]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/request_cookie_option")]
struct CookieOption;
impl ServerHook for CookieOption {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[response_body(&format!("Session cookie: {session_cookie1_option:?}, {session_cookie2_option:?}"))]
    #[request_cookie_option("test1" => session_cookie1_option, "test2" => session_cookie2_option)]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/request_cookie")]
struct Cookie;
impl ServerHook for Cookie {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[response_body(&format!("Session cookie: {session_cookie1}, {session_cookie2}"))]
    #[request_cookie("test1" => session_cookie1, "test2" => session_cookie2)]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/request_version")]
struct RequestVersionTest;
impl ServerHook for RequestVersionTest {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[response_body(&format!("HTTP Version: {http_version}"))]
    #[request_version(http_version)]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/request_path")]
struct RequestPathTest;
impl ServerHook for RequestPathTest {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[response_body(&format!("Request Path: {request_path}"))]
    #[request_path(request_path)]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/response_header")]
struct ResponseHeaderTest;
impl ServerHook for ResponseHeaderTest {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[response_body("Testing header set and replace operations")]
    #[response_header("X-Add-Header", "add-value")]
    #[response_header("X-Set-Header" => "set-value")]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/literals")]
struct Literals;
impl ServerHook for Literals {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[response_status_code(201)]
    #[response_header(CONTENT_TYPE => APPLICATION_JSON)]
    #[response_body("{\"message\": \"Resource created\"}")]
    #[response_reason_phrase(HttpStatus::Created.to_string())]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/inject/response_body")]
struct InjectResponseBody;
impl ServerHook for InjectResponseBody {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &mut Context) {
        self.response_body_with_ref_self(ctx).await;
    }
}
impl InjectResponseBody {
    #[response_body("response body with ref self")]
    async fn response_body_with_ref_self(&self, ctx: &mut Context) {}
}
#[route("/inject/post_method")]
struct InjectPostMethod;
impl ServerHook for InjectPostMethod {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &mut Context) {
        self.post_method_with_ref_self(ctx).await;
    }
}
impl InjectPostMethod {
    #[prologue_macros(post_method, response_body("post method with ref self"))]
    async fn post_method_with_ref_self(&self, ctx: &mut Context) {}
}
#[route("/inject/send_flush")]
struct InjectSendFlush;
impl ServerHook for InjectSendFlush {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &mut Context) {
        self.send_and_flush_with_ref_self(ctx).await;
    }
}
impl InjectSendFlush {
    #[epilogue_macros(try_send, flush)]
    async fn send_and_flush_with_ref_self(&self, ctx: &mut Context) {}
}
#[route("/inject/request_body")]
struct InjectRequestBody;
impl ServerHook for InjectRequestBody {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &mut Context) {
        self.extract_request_body_with_ref_self(ctx).await;
    }
}
impl InjectRequestBody {
    #[request_body(_raw_body)]
    async fn extract_request_body_with_ref_self(&self, _ctx: &mut Context) {}
}
#[route("/inject/multiple_methods")]
struct InjectMultipleMethods;
impl ServerHook for InjectMultipleMethods {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &mut Context) {
        self.multiple_methods_with_ref_self(ctx).await;
    }
}
impl InjectMultipleMethods {
    #[methods(get, post)]
    async fn multiple_methods_with_ref_self(&self, ctx: &mut Context) {}
    #[unknown_method]
    async fn unknown_method_with_ref_self(&self, ctx: &mut Context) {}
}
#[route("/inject/http_stream")]
struct InjectHttpStream;
impl ServerHook for InjectHttpStream {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &mut Context) {
        self.http_stream_handler_with_ref_self(ctx).await;
    }
}
impl InjectHttpStream {
    #[http_from_stream(_request)]
    async fn http_stream_handler_with_ref_self(&self, _ctx: &mut Context) {}
}
#[route("/inject/ws_stream")]
struct InjectWsStream;
impl ServerHook for InjectWsStream {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &mut Context) {
        self.websocket_stream_handler_with_ref_self(ctx).await;
    }
}
impl InjectWsStream {
    #[ws_from_stream(_request)]
    async fn websocket_stream_handler_with_ref_self(&self, _ctx: &mut Context) {}
}
#[route("/inject/complex_post")]
struct InjectComplexPost;
impl ServerHook for InjectComplexPost {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &mut Context) {
        self.complex_post_handler_with_ref_self(ctx).await;
    }
}
impl InjectComplexPost {
    #[prologue_macros(
        post_method,
        http_version,
        request_body(raw_body),
        response_status_code(201),
        response_header(CONTENT_TYPE => APPLICATION_JSON),
        response_body(&format!("Received: {raw_body:?}"))
    )]
    #[epilogue_macros(try_send, flush)]
    async fn complex_post_handler_with_ref_self(&self, ctx: &mut Context) {}
}
impl InjectComplexPost {
    #[post_method]
    async fn test_with_bool_param(_a: bool, ctx: &mut Context) {}
    #[get_method]
    async fn test_with_multiple_params(_a: bool, ctx: &mut Context, _b: i32) {}
}
#[route("/test/send")]
struct TestSend;
impl ServerHook for TestSend {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        get_method,
        response_status_code(200),
        response_header(CONTENT_TYPE => TEXT_PLAIN),
        response_body("Test send operation")
    )]
    #[epilogue_macros(send)]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/test/send_body")]
struct TestSendBody;
impl ServerHook for TestSendBody {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        get_method,
        response_status_code(200),
        response_header(CONTENT_TYPE => TEXT_PLAIN),
        response_body("Test send body operation")
    )]
    #[epilogue_macros(send_body)]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/test/send_body_with_data")]
struct TestSendBodyWithData;
impl ServerHook for TestSendBodyWithData {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        get_method,
        response_status_code(200),
        response_header(CONTENT_TYPE => TEXT_PLAIN)
    )]
    #[epilogue_macros(send_body_with_data("Custom data from send_body_with_data"))]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/test/try_send")]
struct TestTrySend;
impl ServerHook for TestTrySend {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        get_method,
        response_status_code(200),
        response_header(CONTENT_TYPE => TEXT_PLAIN),
        response_body("Test try send operation")
    )]
    #[epilogue_macros(try_send)]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/test/try_send_body")]
struct TestTrySendBody;
impl ServerHook for TestTrySendBody {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        get_method,
        response_status_code(200),
        response_header(CONTENT_TYPE => TEXT_PLAIN),
        response_body("Test try send body operation")
    )]
    #[epilogue_macros(try_send_body)]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/test/try_send_body_with_data")]
struct TestTrySendBodyWithData;
impl ServerHook for TestTrySendBodyWithData {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        get_method,
        response_status_code(200),
        response_header(CONTENT_TYPE => TEXT_PLAIN)
    )]
    #[epilogue_macros(try_send_body_with_data("Custom data from try_send_body_with_data"))]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/test/try_flush")]
struct TestTryFlush;
impl ServerHook for TestTryFlush {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        get_method,
        response_status_code(200),
        response_header(CONTENT_TYPE => TEXT_PLAIN),
        response_body("Test try flush operation")
    )]
    #[epilogue_macros(try_flush)]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/test/aborted")]
struct TestAborted;
impl ServerHook for TestAborted {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        get_method,
        response_status_code(200),
        response_header(CONTENT_TYPE => TEXT_PLAIN),
        response_body("Test aborted operation")
    )]
    #[epilogue_macros(aborted)]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/test/closed")]
struct TestClosed;
impl ServerHook for TestClosed {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        get_method,
        response_status_code(200),
        response_header(CONTENT_TYPE => TEXT_PLAIN),
        response_body("Test closed operation")
    )]
    #[epilogue_macros(closed)]
    async fn handle(self, ctx: &mut Context) {}
}
#[route("/test/flush")]
struct TestFlush;
impl ServerHook for TestFlush {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        get_method,
        response_status_code(200),
        response_header(CONTENT_TYPE => TEXT_PLAIN),
        response_body("Test flush operation")
    )]
    #[epilogue_macros(flush)]
    async fn handle(self, ctx: &mut Context) {}
}
#[response_body("standalone response body")]
async fn standalone_response_body_handler(ctx: &mut Context) {}
#[prologue_macros(get_method, response_body("standalone get handler"))]
async fn standalone_get_handler(ctx: &mut Context) {}
#[epilogue_macros(try_send, flush)]
async fn standalone_send_and_flush_handler(ctx: &mut Context) {}
#[request_body(_raw_body)]
async fn standalone_request_body_extractor(ctx: &mut Context) {}
#[methods(get, post)]
async fn standalone_multiple_methods_handler(ctx: &mut Context) {}
#[http_from_stream]
async fn standalone_http_stream_handler(ctx: &mut Context) {}
#[ws_from_stream]
async fn standalone_websocket_stream_handler(ctx: &mut Context) {}
#[aborted]
async fn standalone_aborted_handler(ctx: &mut Context) {}
#[closed]
async fn standalone_closed_handler(ctx: &mut Context) {}
#[flush]
async fn standalone_flush_handler(ctx: &mut Context) {}
#[try_flush]
async fn standalone_try_flush_handler(ctx: &mut Context) {}
#[prologue_macros(
    get_method,
    http_version,
    response_status_code(200),
    response_header(CONTENT_TYPE => TEXT_PLAIN),
    response_body("standalone complex handler")
)]
#[epilogue_macros(try_send, flush)]
async fn standalone_complex_get_handler(ctx: &mut Context) {}
#[request_body(body1, body2, body3)]
async fn test_multi_request_body(ctx: &mut Context) {
    println!("body1: {:?}, body2: {:?}, body3: {:?}", body1, body2, body3);
}
#[route("/test_multi_request_body_json")]
#[derive(Debug, serde::Deserialize)]
struct User {
    name: String,
}
impl ServerHook for User {
    async fn new(_ctx: &mut Context) -> Self {
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
    async fn handle(self, ctx: &mut Context) {}
}
#[attribute("key1" => attr1: String, "key2" => attr2: i32)]
async fn test_multi_attribute(ctx: &mut Context) {
    println!("attr1: {:?}, attr2: {:?}", attr1, attr2);
}
#[attributes(attrs1, attrs2)]
async fn test_multi_attributes(ctx: &mut Context) {
    println!("attrs1: {:?}, attrs2: {:?}", attrs1, attrs2);
}
#[route_params(params1, params2)]
async fn test_multi_route_params(ctx: &mut Context) {
    println!("params1: {:?}, params2: {:?}", params1, params2);
}
#[request_querys(querys1, querys2)]
async fn test_multi_request_querys(ctx: &mut Context) {
    println!("querys1: {:?}, querys2: {:?}", querys1, querys2);
}
#[request_headers(headers1, headers2)]
async fn test_multi_request_headers(ctx: &mut Context) {
    println!("headers1: {:?}, headers2: {:?}", headers1, headers2);
}
#[request_cookies(cookies1, cookies2)]
async fn test_multi_request_cookies(ctx: &mut Context) {
    println!("cookies1: {:?}, cookies2: {:?}", cookies1, cookies2);
}
#[request_version(version1, version2)]
async fn test_multi_request_version(ctx: &mut Context) {
    println!("version1: {:?}, version2: {:?}", version1, version2);
}
#[request_path(path1, path2)]
async fn test_multi_request_path(ctx: &mut Context) {
    println!("path1: {:?}, path2: {:?}", path1, path2);
}
#[host("localhost", "127.0.0.1")]
async fn test_multi_host(ctx: &mut Context) {
    println!("Host check passed");
}
#[reject_host("localhost", "127.0.0.1")]
async fn test_multi_reject_host(ctx: &mut Context) {
    println!("Reject host check passed");
}
#[referer("http://localhost", "http://127.0.0.1")]
async fn test_multi_referer(ctx: &mut Context) {
    println!("Referer check passed");
}
#[reject_referer("http://localhost", "http://127.0.0.1")]
async fn test_multi_reject_referer(ctx: &mut Context) {
    println!("Reject referer check passed");
}
#[hyperlane(server1: Server, server2: Server)]
async fn test_multi_hyperlane() {
    println!("server1 and server2 initialized");
}
#[response_status_code(200)]
async fn standalone_response_status_code_handler(_ctx: &mut Context) {}
#[response_reason_phrase("Custom Reason")]
async fn standalone_response_reason_phrase_handler(_ctx: &mut Context) {}
#[response_header(CONTENT_TYPE => APPLICATION_JSON)]
async fn standalone_response_header_handler(_ctx: &mut Context) {}
#[response_header("X-Custom-Header", "custom-value")]
async fn standalone_response_header_with_comma_handler(_ctx: &mut Context) {}
#[response_version(HttpVersion::Http1_1)]
async fn standalone_response_version_handler(_ctx: &mut Context) {}
#[connect_method]
async fn standalone_connect_handler(_ctx: &mut Context) {}
#[delete_method]
async fn standalone_delete_handler(_ctx: &mut Context) {}
#[head_method]
async fn standalone_head_handler(_ctx: &mut Context) {}
#[options_method]
async fn standalone_options_handler(_ctx: &mut Context) {}
#[patch_method]
async fn standalone_patch_handler(_ctx: &mut Context) {}
#[put_method]
async fn standalone_put_handler(_ctx: &mut Context) {}
#[trace_method]
async fn standalone_trace_handler(_ctx: &mut Context) {}
#[get_method]
async fn standalone_get_handler_with_param(_a: bool, ctx: &mut Context) {}
#[unknown_method]
async fn standalone_unknown_method_handler(_ctx: &mut Context) {}
#[methods(get, post, put)]
async fn standalone_methods_multiple_handler(_ctx: &mut Context) {}
#[http0_9_version]
async fn standalone_http0_9_version_handler(_ctx: &mut Context) {}
#[http1_0_version]
async fn standalone_http1_0_version_handler(_ctx: &mut Context) {}
#[http1_1_version]
async fn standalone_http1_1_handler(_ctx: &mut Context) {}
#[http2_version]
async fn standalone_http2_version_handler(_ctx: &mut Context) {}
#[http3_version]
async fn standalone_http3_version_handler(_ctx: &mut Context) {}
#[http1_1_or_higher_version]
async fn standalone_http1_1_or_higher_version_handler(_ctx: &mut Context) {}
#[unknown_version]
async fn standalone_unknown_version_handler(_ctx: &mut Context) {}
#[h2c_upgrade_type]
async fn standalone_h2c_upgrade_type_handler(_ctx: &mut Context) {}
#[tls_upgrade_type]
async fn standalone_tls_upgrade_type_handler(_ctx: &mut Context) {}
#[ws_upgrade_type]
async fn standalone_ws_handler(ctx: &mut Context) {}
#[unknown_upgrade_type]
async fn standalone_unknown_upgrade_type_handler(_ctx: &mut Context) {}
#[filter(_ctx.get_request().get_method().is_get())]
async fn standalone_filter_handler(_ctx: &mut Context) {}
#[reject(_ctx.get_request().get_method().is_post())]
async fn standalone_reject_handler(_ctx: &mut Context) {}
#[reject_host("example.com")]
async fn standalone_reject_host_handler(_ctx: &mut Context) {}
#[referer("https://example.com")]
async fn standalone_referer_handler(_ctx: &mut Context) {}
#[reject_referer("https://malicious.com")]
async fn standalone_reject_referer_handler(_ctx: &mut Context) {}
#[request_query("param" => _value)]
async fn standalone_request_query_handler(_ctx: &mut Context) {}
#[request_query_option("optional_param" => _optional_value)]
async fn standalone_request_query_option_handler(_ctx: &mut Context) {}
#[request_header(HOST => _host_value)]
async fn standalone_request_header_handler(_ctx: &mut Context) {}
#[request_header_option(USER_AGENT => _user_agent)]
async fn standalone_request_header_option_handler(_ctx: &mut Context) {}
#[request_querys(_querys)]
async fn standalone_request_querys_handler(_ctx: &mut Context) {}
#[request_headers(_headers)]
async fn standalone_request_headers_handler(_ctx: &mut Context) {}
#[request_cookies(_cookies)]
async fn standalone_request_cookies_handler(_ctx: &mut Context) {}
#[request_cookie("session" => _session_cookie)]
async fn standalone_request_cookie_handler(_ctx: &mut Context) {}
#[request_cookie_option("optional_cookie" => _optional_cookie)]
async fn standalone_request_cookie_option_handler(_ctx: &mut Context) {}
#[request_version(_version)]
async fn standalone_request_version_handler(_ctx: &mut Context) {}
#[request_path(_path)]
async fn standalone_request_path_handler(_ctx: &mut Context) {}
#[attribute("key" => _attr_value: String)]
async fn standalone_attribute_handler(_ctx: &mut Context) {}
#[attribute_option("optional_key" => _optional_attr: String)]
async fn standalone_attribute_option_handler(_ctx: &mut Context) {}
#[attributes(_attrs)]
async fn standalone_attributes_handler(_ctx: &mut Context) {}
#[route_params(_params)]
async fn standalone_route_params_handler(_ctx: &mut Context) {}
#[route_param("param" => _param_value)]
async fn standalone_route_param_handler(_ctx: &mut Context) {}
#[route_param_option("optional_param" => _optional_param_value)]
async fn standalone_route_param_option_handler(_ctx: &mut Context) {}
#[request_body_json(_user: TestData)]
async fn standalone_request_body_json_handler(_ctx: &mut Context) {}
#[request_body_json_result(_user_result: TestData)]
async fn standalone_request_body_json_result_handler(_ctx: &mut Context) {}
#[http_from_stream]
async fn standalone_http_from_stream_with_config_handler(_ctx: &mut Context) {}
#[ws_from_stream]
async fn standalone_ws_from_stream_with_config_handler(_ctx: &mut Context) {}
#[http_from_stream(_request)]
async fn standalone_http_from_stream_with_request_handler(_ctx: &mut Context) {}
#[ws_from_stream(_request)]
async fn standalone_ws_from_stream_with_request_handler(_ctx: &mut Context) {}
#[http_from_stream(_request)]
async fn standalone_http_from_stream_full_handler(_ctx: &mut Context) {}
#[ws_from_stream(_request)]
async fn standalone_ws_from_stream_full_handler(_ctx: &mut Context) {}
#[send]
async fn standalone_send_handler_2(_ctx: &mut Context) {}
#[send_body]
async fn standalone_send_body_handler_2(_ctx: &mut Context) {}
#[send_body_with_data("Custom send body data")]
async fn standalone_send_body_with_data_handler_2(_ctx: &mut Context) {}
#[try_send]
async fn standalone_try_send_handler_2(_ctx: &mut Context) {}
#[try_send_body]
async fn standalone_try_send_body_handler_2(_ctx: &mut Context) {}
#[try_send_body_with_data("Custom try send body data")]
async fn standalone_try_send_body_with_data_handler_2(_ctx: &mut Context) {}
#[flush]
async fn standalone_flush_handler_2(_ctx: &mut Context) {}
#[try_flush]
async fn standalone_try_flush_handler_2(_ctx: &mut Context) {}
#[aborted]
async fn standalone_aborted_handler_2(_ctx: &mut Context) {}
#[closed]
async fn standalone_closed_handler_2(_ctx: &mut Context) {}
#[clear_response_headers]
async fn standalone_clear_response_headers_handler(_ctx: &mut Context) {}
#[prologue_macros(
    get_method,
    response_status_code(200),
    response_header(CONTENT_TYPE => TEXT_PLAIN),
    response_body("prologue macros test")
)]
async fn standalone_prologue_macros_complex_handler(_ctx: &mut Context) {}
#[epilogue_macros(
    response_status_code(201),
    response_header(CONTENT_TYPE => APPLICATION_JSON),
    response_body("epilogue macros test"),
    try_send,
    flush
)]
async fn standalone_epilogue_macros_complex_handler(_ctx: &mut Context) {}
#[prologue_hooks(prologue_hooks_fn)]
async fn standalone_prologue_hooks_handler(_ctx: &mut Context) {}
#[epilogue_hooks(epilogue_hooks_fn)]
async fn standalone_epilogue_hooks_handler(_ctx: &mut Context) {}
#[route("/hooks_expression")]
struct HooksExpression;
impl ServerHook for HooksExpression {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[get_method]
    #[prologue_hooks(HooksExpression::new_hook, HooksExpression::method_hook)]
    #[epilogue_hooks(HooksExpression::new_hook, HooksExpression::method_hook)]
    #[response_body("hooks expression test")]
    async fn handle(self, ctx: &mut Context) {}
}
impl HooksExpression {
    async fn new_hook(_ctx: &mut Context) {}
    async fn method_hook(_ctx: &mut Context) {}
}
#[route("/server_config")]
struct MultiServerConfig;
impl ServerHook for MultiServerConfig {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[get_method]
    #[response_body("multi server config test")]
    async fn handle(self, ctx: &mut Context) {}
}
impl MultiServerConfig {
    #[hyperlane(server_config: ServerConfig)]
    async fn server_config_1() -> ServerConfig {
        server_config
    }
    #[hyperlane(server_config: ServerConfig)]
    async fn server_config_2(self) -> ServerConfig {
        server_config
    }
    #[hyperlane(server_config: ServerConfig)]
    async fn server_config_3(&self) -> ServerConfig {
        server_config
    }
}
#[hyperlane(server: Server)]
#[hyperlane(config: ServerConfig)]
#[tokio::main]
async fn main() {
    config.set_nodelay(Some(false));
    server.server_config(config);
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
mod context;
mod filter;
mod flush;
mod from_stream;
mod hook;
mod host;
mod hyperlane;
mod inject;
mod method;
mod referer;
mod reject;
mod request;
mod request_middleware;
mod response;
mod response_middleware;
mod route;
mod send;
mod stream;
mod upgrade;
mod version;
use {
    aborted::*, closed::*, common::*, context::*, filter::*, flush::*, from_stream::*, hook::*,
    host::*, hyperlane::*, inject::*, method::*, referer::*, reject::*, request::*,
    request_middleware::*, response::*, response_middleware::*, route::*, send::*, stream::*,
    upgrade::*, version::*,
};
use {
    proc_macro::TokenStream,
    proc_macro2::TokenStream as TokenStream2,
    quote::quote,
    syn::{
        Ident, Token,
        parse::{Parse, ParseStream, Parser, Result},
        punctuated::Punctuated,
        token::Comma,
        *,
    },
};
#[proc_macro_attribute]
pub fn ws_from_stream(attr: TokenStream, item: TokenStream) -> TokenStream {
    ws_from_stream_macro(attr, item)
}
#[proc_macro_attribute]
pub fn http_from_stream(attr: TokenStream, item: TokenStream) -> TokenStream {
    http_from_stream_macro(attr, item)
}
#[proc_macro_attribute]
pub fn get_method(_attr: TokenStream, item: TokenStream) -> TokenStream {
    get_method_handler(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn post_method(_attr: TokenStream, item: TokenStream) -> TokenStream {
    post_method_handler(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn put_method(_attr: TokenStream, item: TokenStream) -> TokenStream {
    put_method_handler(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn delete_method(_attr: TokenStream, item: TokenStream) -> TokenStream {
    delete_method_handler(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn patch_method(_attr: TokenStream, item: TokenStream) -> TokenStream {
    patch_method_handler(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn head_method(_attr: TokenStream, item: TokenStream) -> TokenStream {
    head_method_handler(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn options_method(_attr: TokenStream, item: TokenStream) -> TokenStream {
    options_method_handler(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn connect_method(_attr: TokenStream, item: TokenStream) -> TokenStream {
    connect_method_handler(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn trace_method(_attr: TokenStream, item: TokenStream) -> TokenStream {
    trace_method_handler(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn unknown_method(_attr: TokenStream, item: TokenStream) -> TokenStream {
    unknown_method_handler(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn methods(attr: TokenStream, item: TokenStream) -> TokenStream {
    methods_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn http0_9_version(_attr: TokenStream, item: TokenStream) -> TokenStream {
    http0_9_version_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn http1_0_version(_attr: TokenStream, item: TokenStream) -> TokenStream {
    http1_0_version_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn http1_1_version(_attr: TokenStream, item: TokenStream) -> TokenStream {
    http1_1_version_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn http2_version(_attr: TokenStream, item: TokenStream) -> TokenStream {
    http2_version_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn http3_version(_attr: TokenStream, item: TokenStream) -> TokenStream {
    http3_version_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn http1_1_or_higher_version(_attr: TokenStream, item: TokenStream) -> TokenStream {
    http1_1_or_higher_version_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn http_version(_attr: TokenStream, item: TokenStream) -> TokenStream {
    http_version_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn unknown_version(_attr: TokenStream, item: TokenStream) -> TokenStream {
    unknown_version_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn ws_upgrade_type(_attr: TokenStream, item: TokenStream) -> TokenStream {
    ws_upgrade_type_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn h2c_upgrade_type(_attr: TokenStream, item: TokenStream) -> TokenStream {
    h2c_upgrade_type_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn tls_upgrade_type(_attr: TokenStream, item: TokenStream) -> TokenStream {
    tls_upgrade_type_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn unknown_upgrade_type(_attr: TokenStream, item: TokenStream) -> TokenStream {
    unknown_upgrade_type_macro(item, Position::Prologue)
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
#[proc_macro]
pub fn context(input: TokenStream) -> TokenStream {
    context_macro(input)
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
mod r#static;
mod r#struct;
mod r#type;
pub(crate) use {r#const::*, r#enum::*, r#fn::*, r#static::*, r#struct::*, r#type::*};
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
pub(crate) fn into_new_context(context: &Ident) -> TokenStream2 {
    quote! {
        std::convert::Into::<&mut ::hyperlane::Context>::into(#context as *mut ::hyperlane::Context as usize)
    }
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
# Path: hyperlane-macros/src/common/type.rs
```rust
use crate::*;
pub(crate) type MacroHandlerPosition = fn(TokenStream, Position) -> TokenStream;
pub(crate) type MacroHandlerWithAttr = fn(TokenStream, TokenStream) -> TokenStream;
pub(crate) type MacroHandlerWithAttrPosition =
    fn(TokenStream, TokenStream, Position) -> TokenStream;
```
# Path: hyperlane-macros/src/common/static.rs
```rust
use crate::*;
pub(crate) static INJECTABLE_MACROS: &[InjectableMacro] = &[
    InjectableMacro {
        name: "aborted",
        handler: Handler::NoAttrPosition(aborted_macro),
    },
    InjectableMacro {
        name: "closed",
        handler: Handler::NoAttrPosition(closed_macro),
    },
    InjectableMacro {
        name: "filter",
        handler: Handler::WithAttrPosition(filter_macro),
    },
    InjectableMacro {
        name: "try_flush",
        handler: Handler::NoAttrPosition(try_flush_macro),
    },
    InjectableMacro {
        name: "flush",
        handler: Handler::NoAttrPosition(flush_macro),
    },
    InjectableMacro {
        name: "task_panic",
        handler: Handler::WithAttr(task_panic_macro),
    },
    InjectableMacro {
        name: "request_error",
        handler: Handler::WithAttr(request_error_macro),
    },
    InjectableMacro {
        name: "prologue_hooks",
        handler: Handler::WithAttrPosition(prologue_hooks_macro),
    },
    InjectableMacro {
        name: "epilogue_hooks",
        handler: Handler::WithAttrPosition(epilogue_hooks_macro),
    },
    InjectableMacro {
        name: "host",
        handler: Handler::WithAttrPosition(host_macro),
    },
    InjectableMacro {
        name: "reject_host",
        handler: Handler::WithAttrPosition(reject_host_macro),
    },
    InjectableMacro {
        name: "hyperlane",
        handler: Handler::WithAttr(hyperlane_macro),
    },
    InjectableMacro {
        name: "methods",
        handler: Handler::WithAttrPosition(methods_macro),
    },
    InjectableMacro {
        name: "get_method",
        handler: Handler::NoAttrPosition(get_method_handler),
    },
    InjectableMacro {
        name: "post_method",
        handler: Handler::NoAttrPosition(post_method_handler),
    },
    InjectableMacro {
        name: "put_method",
        handler: Handler::NoAttrPosition(put_method_handler),
    },
    InjectableMacro {
        name: "delete_method",
        handler: Handler::NoAttrPosition(delete_method_handler),
    },
    InjectableMacro {
        name: "patch_method",
        handler: Handler::NoAttrPosition(patch_method_handler),
    },
    InjectableMacro {
        name: "head_method",
        handler: Handler::NoAttrPosition(head_method_handler),
    },
    InjectableMacro {
        name: "options_method",
        handler: Handler::NoAttrPosition(options_method_handler),
    },
    InjectableMacro {
        name: "connect_method",
        handler: Handler::NoAttrPosition(connect_method_handler),
    },
    InjectableMacro {
        name: "trace_method",
        handler: Handler::NoAttrPosition(trace_method_handler),
    },
    InjectableMacro {
        name: "unknown_method",
        handler: Handler::NoAttrPosition(unknown_method_handler),
    },
    InjectableMacro {
        name: "referer",
        handler: Handler::WithAttrPosition(referer_macro),
    },
    InjectableMacro {
        name: "reject_referer",
        handler: Handler::WithAttrPosition(reject_referer_macro),
    },
    InjectableMacro {
        name: "reject",
        handler: Handler::WithAttrPosition(reject_macro),
    },
    InjectableMacro {
        name: "request_body",
        handler: Handler::WithAttrPosition(request_body_macro),
    },
    InjectableMacro {
        name: "request_body_json_result",
        handler: Handler::WithAttrPosition(request_body_json_result_macro),
    },
    InjectableMacro {
        name: "request_body_json",
        handler: Handler::WithAttrPosition(request_body_json_macro),
    },
    InjectableMacro {
        name: "attribute_option",
        handler: Handler::WithAttrPosition(attribute_option_macro),
    },
    InjectableMacro {
        name: "attribute",
        handler: Handler::WithAttrPosition(attribute_macro),
    },
    InjectableMacro {
        name: "attributes",
        handler: Handler::WithAttrPosition(attributes_macro),
    },
    InjectableMacro {
        name: "task_panic_data_option",
        handler: Handler::WithAttrPosition(task_panic_data_option_macro),
    },
    InjectableMacro {
        name: "task_panic_data",
        handler: Handler::WithAttrPosition(task_panic_data_macro),
    },
    InjectableMacro {
        name: "request_error_data_option",
        handler: Handler::WithAttrPosition(request_error_data_option_macro),
    },
    InjectableMacro {
        name: "request_error_data",
        handler: Handler::WithAttrPosition(request_error_data_macro),
    },
    InjectableMacro {
        name: "route_param_option",
        handler: Handler::WithAttrPosition(route_param_option_macro),
    },
    InjectableMacro {
        name: "route_param",
        handler: Handler::WithAttrPosition(route_param_macro),
    },
    InjectableMacro {
        name: "route_params",
        handler: Handler::WithAttrPosition(route_params_macro),
    },
    InjectableMacro {
        name: "request_query_option",
        handler: Handler::WithAttrPosition(request_query_option_macro),
    },
    InjectableMacro {
        name: "request_query",
        handler: Handler::WithAttrPosition(request_query_macro),
    },
    InjectableMacro {
        name: "request_querys",
        handler: Handler::WithAttrPosition(request_querys_macro),
    },
    InjectableMacro {
        name: "request_header_option",
        handler: Handler::WithAttrPosition(request_header_option_macro),
    },
    InjectableMacro {
        name: "request_header",
        handler: Handler::WithAttrPosition(request_header_macro),
    },
    InjectableMacro {
        name: "request_headers",
        handler: Handler::WithAttrPosition(request_headers_macro),
    },
    InjectableMacro {
        name: "request_cookie_option",
        handler: Handler::WithAttrPosition(request_cookie_option_macro),
    },
    InjectableMacro {
        name: "request_cookie",
        handler: Handler::WithAttrPosition(request_cookie_macro),
    },
    InjectableMacro {
        name: "request_cookies",
        handler: Handler::WithAttrPosition(request_cookies_macro),
    },
    InjectableMacro {
        name: "request_version",
        handler: Handler::WithAttrPosition(request_version_macro),
    },
    InjectableMacro {
        name: "request_path",
        handler: Handler::WithAttrPosition(request_path_macro),
    },
    InjectableMacro {
        name: "request_middleware",
        handler: Handler::WithAttr(request_middleware_macro),
    },
    InjectableMacro {
        name: "response_status_code",
        handler: Handler::WithAttrPosition(response_status_code_macro),
    },
    InjectableMacro {
        name: "response_reason_phrase",
        handler: Handler::WithAttrPosition(response_reason_phrase_macro),
    },
    InjectableMacro {
        name: "response_header",
        handler: Handler::WithAttrPosition(response_header_macro),
    },
    InjectableMacro {
        name: "response_body",
        handler: Handler::WithAttrPosition(response_body_macro),
    },
    InjectableMacro {
        name: "clear_response_headers",
        handler: Handler::NoAttrPosition(clear_response_headers_macro),
    },
    InjectableMacro {
        name: "response_version",
        handler: Handler::WithAttrPosition(response_version_macro),
    },
    InjectableMacro {
        name: "response_middleware",
        handler: Handler::WithAttr(response_middleware_macro),
    },
    InjectableMacro {
        name: "route",
        handler: Handler::WithAttr(route_macro),
    },
    InjectableMacro {
        name: "try_send",
        handler: Handler::NoAttrPosition(try_send_macro),
    },
    InjectableMacro {
        name: "send",
        handler: Handler::NoAttrPosition(send_macro),
    },
    InjectableMacro {
        name: "try_send_body",
        handler: Handler::NoAttrPosition(try_send_body_macro),
    },
    InjectableMacro {
        name: "send_body",
        handler: Handler::NoAttrPosition(send_body_macro),
    },
    InjectableMacro {
        name: "try_send_body_with_data",
        handler: Handler::WithAttrPosition(try_send_body_with_data_macro),
    },
    InjectableMacro {
        name: "send_body_with_data",
        handler: Handler::WithAttrPosition(send_body_with_data_macro),
    },
    InjectableMacro {
        name: "http_from_stream",
        handler: Handler::WithAttr(http_from_stream_macro),
    },
    InjectableMacro {
        name: "ws_from_stream",
        handler: Handler::WithAttr(ws_from_stream_macro),
    },
    InjectableMacro {
        name: "ws_upgrade_type",
        handler: Handler::NoAttrPosition(ws_upgrade_type_macro),
    },
    InjectableMacro {
        name: "h2c_upgrade_type",
        handler: Handler::NoAttrPosition(h2c_upgrade_type_macro),
    },
    InjectableMacro {
        name: "tls_upgrade_type",
        handler: Handler::NoAttrPosition(tls_upgrade_type_macro),
    },
    InjectableMacro {
        name: "unknown_upgrade_type",
        handler: Handler::NoAttrPosition(unknown_upgrade_type_macro),
    },
    InjectableMacro {
        name: "http0_9_version",
        handler: Handler::NoAttrPosition(http0_9_version_macro),
    },
    InjectableMacro {
        name: "http1_0_version",
        handler: Handler::NoAttrPosition(http1_0_version_macro),
    },
    InjectableMacro {
        name: "http1_1_version",
        handler: Handler::NoAttrPosition(http1_1_version_macro),
    },
    InjectableMacro {
        name: "http2_version",
        handler: Handler::NoAttrPosition(http2_version_macro),
    },
    InjectableMacro {
        name: "http3_version",
        handler: Handler::NoAttrPosition(http3_version_macro),
    },
    InjectableMacro {
        name: "http1_1_or_higher_version",
        handler: Handler::NoAttrPosition(http1_1_or_higher_version_macro),
    },
    InjectableMacro {
        name: "http_version",
        handler: Handler::NoAttrPosition(http_version_macro),
    },
    InjectableMacro {
        name: "unknown_version",
        handler: Handler::NoAttrPosition(unknown_version_macro),
    },
];
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
# Path: hyperlane-macros/src/context/mod.rs
```rust
mod r#fn;
mod r#impl;
mod r#struct;
pub(crate) use {r#fn::*, r#struct::*};
```
# Path: hyperlane-macros/src/context/fn.rs
```rust
use crate::*;
pub(crate) fn context_macro(input: TokenStream) -> TokenStream {
    let context_input: ContextInput = match parse(input) {
        Ok(input) => input,
        Err(err) => return err.to_compile_error().into(),
    };
    let source_ctx: Ident = context_input.source_ctx;
    into_new_context(&source_ctx).into()
}
```
# Path: hyperlane-macros/src/context/impl.rs
```rust
use crate::*;
impl Parse for ContextInput {
    fn parse(input: ParseStream) -> Result<Self> {
        let source_ctx: Ident = input.parse()?;
        Ok(ContextInput { source_ctx })
    }
}
```
# Path: hyperlane-macros/src/context/struct.rs
```rust
use crate::*;
pub(crate) struct ContextInput {
    pub(crate) source_ctx: Ident,
}
```
# Path: hyperlane-macros/src/hyperlane/mod.rs
```rust
mod r#fn;
mod r#impl;
mod r#struct;
pub(crate) use {r#fn::*, r#struct::*};
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
    let attrs: &Vec<Attribute> = &input_fn.attrs;
    let stmts: &Vec<Stmt> = &block.stmts;
    let mut init_statements: Vec<TokenStream2> = Vec::new();
    for (var_name, type_name) in &multi_hyperlane.params {
        init_statements.push(quote! {
            let mut #var_name: #type_name = #type_name::default();
        });
        if type_name == SERVER_TYPE_KEY {
            init_statements.push(quote! {
                let mut hooks: Vec<::hyperlane::HookType> = inventory::iter().cloned().collect();
                assert_hook_unique_order(hooks.clone());
                hooks.sort_by_key(|hook| hook.try_get_order());
                for hook in hooks {
                    #var_name.handle_hook(hook.clone());
                }
            });
        }
    }
    let gen_code: TokenStream2 = quote! {
        #(#attrs)*
        #vis #sig {
            #(#init_statements)*
            #(#stmts)*
        }
    };
    gen_code.into()
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
# Path: hyperlane-macros/src/hyperlane/struct.rs
```rust
use crate::*;
pub(crate) struct MultiHyperlaneAttr {
    pub(crate) params: Vec<(Ident, Ident)>,
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
        let new_context: TokenStream2 = into_new_context(context);
        quote! {
            #new_context.set_aborted(true);
        }
    })
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
pub(crate) fn prologue_hooks_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let functions: Punctuated<Expr, Token![,]> =
        parse_macro_input!(attr with Punctuated::parse_terminated);
    inject(position, item, |context| {
        let hook_calls = functions.iter().map(|function_expr| {
            quote! {
                let _ = #function_expr(#context).await;
            }
        });
        quote! {
            #(#hook_calls)*
        }
    })
}
pub(crate) fn epilogue_hooks_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let functions: Punctuated<Expr, Token![,]> =
        parse_macro_input!(attr with Punctuated::parse_terminated);
    inject(position, item, |context| {
        let hook_calls = functions.iter().map(|function_expr| {
            quote! {
                let _ = #function_expr(#context).await;
            }
        });
        quote! {
            #(#hook_calls)*
        }
    })
}
```
# Path: hyperlane-macros/src/from_stream/mod.rs
```rust
mod r#impl;
mod r#struct;
pub(crate) use r#struct::*;
```
# Path: hyperlane-macros/src/from_stream/impl.rs
```rust
use crate::*;
impl Parse for FromStreamData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let variable_name: Option<Expr> = if input.is_empty() {
            None
        } else {
            let expr: Expr = input.parse()?;
            if !input.is_empty() {
                return Err(syn::Error::new(
                    input.span(),
                    "expected at most one parameter",
                ));
            }
            Some(expr)
        };
        Ok(FromStreamData { variable_name })
    }
}
```
# Path: hyperlane-macros/src/from_stream/struct.rs
```rust
use crate::*;
pub(crate) struct FromStreamData {
    pub(crate) variable_name: Option<Expr>,
}
```
# Path: hyperlane-macros/src/response_middleware/mod.rs
```rust
mod r#fn;
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
        let new_context: TokenStream2 = into_new_context(context);
        quote! {
            let _ = #new_context.try_flush().await;
        }
    })
}
pub(crate) fn flush_macro(item: TokenStream, position: Position) -> TokenStream {
    inject(position, item, |context| {
        quote! {{
            let new_context: &mut Context = (#context as *mut Context as usize).into();
            new_context.flush().await;
        }}
    })
}
```
# Path: hyperlane-macros/src/upgrade/mod.rs
```rust
mod r#fn;
pub(crate) use r#fn::*;
```
# Path: hyperlane-macros/src/upgrade/fn.rs
```rust
use crate::*;
pub(crate) fn create_protocol_check(
    upgrade_type: &proc_macro2::Ident,
) -> impl FnOnce(&Ident) -> TokenStream2 {
    let upgrade_type_str: String = upgrade_type.to_string();
    move |context| {
        let check_fn: proc_macro2::Ident =
            Ident::new(&format!("is_{upgrade_type_str}"), context.span());
        quote! {
            if !#context.get_request().get_upgrade_type().#check_fn() {
                return;
            }
        }
    }
}
macro_rules! impl_protocol_check_macro {
    ($name:ident, $submit_name:ident, $upgrade_type:ident) => {
        pub(crate) fn $name(item: TokenStream, position: Position) -> TokenStream {
            inject(
                position,
                item,
                create_protocol_check(&proc_macro2::Ident::new(
                    stringify!($upgrade_type),
                    proc_macro2::Span::call_site(),
                )),
            )
        }
    };
}
impl_protocol_check_macro!(ws_upgrade_type_macro, ws_upgrade_type, ws);
impl_protocol_check_macro!(h2c_upgrade_type_macro, h2c_upgrade_type, h2c);
impl_protocol_check_macro!(tls_upgrade_type_macro, tls_upgrade_type, tls);
impl_protocol_check_macro!(unknown_upgrade_type_macro, unknown_upgrade_type, unknown);
```
# Path: hyperlane-macros/src/method/mod.rs
```rust
mod r#fn;
pub(crate) use r#fn::*;
```
# Path: hyperlane-macros/src/method/fn.rs
```rust
use crate::*;
pub(crate) fn create_method_check(
    method: &proc_macro2::Ident,
) -> impl FnOnce(&Ident) -> TokenStream2 {
    let method_str: String = method.to_string();
    move |context| {
        let check_fn: proc_macro2::Ident = Ident::new(&format!("is_{method_str}"), context.span());
        quote! {
            if !#context.get_request().get_method().#check_fn() {
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
                let method_str: String = method.to_string();
                let check_fn: proc_macro2::Ident =
                    Ident::new(&format!("is_{method_str}"), method.span());
                quote! {
                    #context.get_request().get_method().#check_fn()
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
macro_rules! impl_http_method_macro {
    ($name:ident, $submit_name:ident, $method:ident) => {
        pub(crate) fn $name(item: TokenStream, position: Position) -> TokenStream {
            inject(
                position,
                item,
                create_method_check(&proc_macro2::Ident::new(
                    stringify!($method),
                    proc_macro2::Span::call_site(),
                )),
            )
        }
    };
}
impl_http_method_macro!(get_method_handler, get_method, get);
impl_http_method_macro!(post_method_handler, post_method, post);
impl_http_method_macro!(put_method_handler, put_method, put);
impl_http_method_macro!(delete_method_handler, delete_method, delete);
impl_http_method_macro!(patch_method_handler, patch_method, patch);
impl_http_method_macro!(head_method_handler, head_method, head);
impl_http_method_macro!(options_method_handler, options_method, options);
impl_http_method_macro!(connect_method_handler, connect_method, connect);
impl_http_method_macro!(trace_method_handler, trace_method, trace);
impl_http_method_macro!(unknown_method_handler, unknown_method, unknown);
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
        let new_context: TokenStream2 = into_new_context(context);
        quote! {
            #new_context.set_closed(true);
        }
    })
}
```
# Path: hyperlane-macros/src/request/mod.rs
```rust
mod r#fn;
mod r#impl;
mod r#struct;
pub(crate) use {r#fn::*, r#struct::*};
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
        let new_context: TokenStream2 = into_new_context(context);
        let statements = multi_body.variables.iter().map(|variable| {
            quote! {
                let #variable: &::hyperlane::RequestBody = #new_context.get_request().get_body();
            }
        });
        quote! {
            #(#statements)*
        }
    })
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
                let #variable: Result<#type_name, ::hyperlane::serde_json::Error> = #context.get_request().try_get_body_json::<#type_name>();
            }
        });
        quote! {
            #(#statements)*
        }
    })
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
                let #variable: #type_name = #context.get_request().get_body_json::<#type_name>();
            }
        });
        quote! {
            #(#statements)*
        }
    })
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
                    let #variable: Option<#type_name> = #context.try_get_attribute(&#key_name);
                }
            });
        quote! {
            #(#statements)*
        }
    })
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
                    let #variable: #type_name = #context.get_attribute(&#key_name);
                }
            });
        quote! {
            #(#statements)*
        }
    })
}
pub(crate) fn attributes_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_attrs: MultiAttributesData = parse_macro_input!(attr as MultiAttributesData);
    inject(position, item, |context| {
        let new_context: TokenStream2 = into_new_context(context);
        let statements = multi_attrs.variables.iter().map(|variable| {
            quote! {
                let #variable: &::hyperlane::ThreadSafeAttributeStore = #new_context.get_attributes();
            }
        });
        quote! {
            #(#statements)*
        }
    })
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
                let #variable: Option<::hyperlane::PanicData> = #context.try_get_task_panic_data();
            }
        });
        quote! {
            #(#statements)*
        }
    })
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
                let #variable: ::hyperlane::PanicData = #context.get_task_panic_data();
            }
        });
        quote! {
            #(#statements)*
        }
    })
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
                let #variable: Option<::hyperlane::RequestError> = #context.try_get_request_error_data();
            }
        });
        quote! {
            #(#statements)*
        }
    })
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
                let #variable: ::hyperlane::RequestError = #context.get_request_error_data();
            }
        });
        quote! {
            #(#statements)*
        }
    })
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
                let #variable: Option<std::string::String> = #context.try_get_route_param(#key_name);
            }
        });
        quote! {
            #(#statements)*
        }
    })
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
                let #variable: std::string::String = #context.get_route_param(#key_name);
            }
        });
        quote! {
            #(#statements)*
        }
    })
}
pub(crate) fn route_params_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_route_params: MultiRouteParamsData = parse_macro_input!(attr as MultiRouteParamsData);
    inject(position, item, |context| {
        let new_context: TokenStream2 = into_new_context(context);
        let statements = multi_route_params.variables.iter().map(|variable| {
            quote! {
                let #variable: &::hyperlane::RouteParams = #new_context.get_route_params();
            }
        });
        quote! {
            #(#statements)*
        }
    })
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
                let #variable: Option<::hyperlane::RequestQuerysValue> = #context.get_request().try_get_query(#key_name);
            }
        });
        quote! {
            #(#statements)*
        }
    })
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
                let #variable: ::hyperlane::RequestQuerysValue = #context.get_request().get_query(#key_name);
            }
        });
        quote! {
            #(#statements)*
        }
    })
}
pub(crate) fn request_querys_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_querys: MultiQuerysData = parse_macro_input!(attr as MultiQuerysData);
    inject(position, item, |context| {
        let new_context: TokenStream2 = into_new_context(context);
        let statements = multi_querys.variables.iter().map(|variable| {
            quote! {
                let #variable: &::hyperlane::RequestQuerys = #new_context.get_request().get_querys();
            }
        });
        quote! {
            #(#statements)*
        }
    })
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
                let #variable: Option<::hyperlane::RequestHeadersValueItem> = #context.get_request().try_get_header_back(#key_name);
            }
        });
        quote! {
            #(#statements)*
        }
    })
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
                let #variable: ::hyperlane::RequestHeadersValueItem = #context.get_request().get_header_back(#key_name);
            }
        });
        quote! {
            #(#statements)*
        }
    })
}
pub(crate) fn request_headers_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_headers: MultiHeadersData = parse_macro_input!(attr as MultiHeadersData);
    inject(position, item, |context| {
        let new_context: TokenStream2 = into_new_context(context);
        let statements = multi_headers.variables.iter().map(|variable| {
            quote! {
                let #variable: &::hyperlane::RequestHeaders = #new_context.get_request().get_headers();
            }
        });
        quote! {
            #(#statements)*
        }
    })
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
                let #variable: Option<::hyperlane::CookieValue> = #context.get_request().try_get_cookie(#key_name);
            }
        });
        quote! {
            #(#statements)*
        }
    })
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
                let #variable: ::hyperlane::CookieValue = #context.get_request().get_cookie(#key_name);
            }
        });
        quote! {
            #(#statements)*
        }
    })
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
                let #variable: ::hyperlane::Cookies = #context.get_request().get_cookies();
            }
        });
        quote! {
            #(#statements)*
        }
    })
}
pub(crate) fn request_version_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_version: MultiRequestVersionData =
        parse_macro_input!(attr as MultiRequestVersionData);
    inject(position, item, |context| {
        let new_context: TokenStream2 = into_new_context(context);
        let statements = multi_version.variables.iter().map(|variable| {
            quote! {
                let #variable: &::hyperlane::RequestVersion = #new_context.get_request().get_version();
            }
        });
        quote! {
            #(#statements)*
        }
    })
}
pub(crate) fn request_path_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_path: MultiRequestPathData = parse_macro_input!(attr as MultiRequestPathData);
    inject(position, item, |context| {
        let new_context: TokenStream2 = into_new_context(context);
        let statements = multi_path.variables.iter().map(|variable| {
            quote! {
                let #variable: &::hyperlane::RequestPath = #new_context.get_request().get_path();
            }
        });
        quote! {
            #(#statements)*
        }
    })
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
```
# Path: hyperlane-macros/src/route/mod.rs
```rust
mod r#fn;
mod r#impl;
mod r#struct;
pub(crate) use {r#fn::*, r#struct::*};
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
# Path: hyperlane-macros/src/route/struct.rs
```rust
use crate::*;
pub(crate) struct RouteAttr {
    pub(crate) path: Expr,
}
```
# Path: hyperlane-macros/src/response/mod.rs
```rust
mod r#enum;
mod r#fn;
mod r#impl;
mod r#struct;
pub(crate) use {r#enum::*, r#fn::*, r#struct::*};
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
        let new_context: TokenStream2 = into_new_context(context);
        quote! {
            #new_context.get_mut_response().set_status_code(::hyperlane::ResponseStatusCode::from(#value as usize));
        }
    })
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
        let new_context: TokenStream2 = into_new_context(context);
        quote! {
            #new_context.get_mut_response().set_reason_phrase(&#value);
        }
    })
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
    inject(position, item, |context| {
        let new_context: TokenStream2 = into_new_context(context);
        match operation {
            HeaderOperation::Add => {
                quote! {
                    #new_context.get_mut_response().add_header(&#key, &#value);
                }
            }
            HeaderOperation::Set => {
                quote! {
                    #new_context.get_mut_response().set_header(&#key, &#value);
                }
            }
        }
    })
}
pub(crate) fn response_body_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let body_data: ResponseBodyData = parse_macro_input!(attr as ResponseBodyData);
    let body: Expr = body_data.body;
    inject(position, item, |context| {
        let new_context: TokenStream2 = into_new_context(context);
        quote! {
            #new_context.get_mut_response().set_body(&#body);
        }
    })
}
pub(crate) fn clear_response_headers_macro(item: TokenStream, position: Position) -> TokenStream {
    inject(position, item, |context| {
        let new_context: TokenStream2 = into_new_context(context);
        quote! {
            #new_context.get_mut_response().clear_headers();
        }
    })
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
        let new_context: TokenStream2 = into_new_context(context);
        quote! {
            #new_context.get_mut_response().set_version(#value);
        }
    })
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
# Path: hyperlane-macros/src/response/struct.rs
```rust
use crate::*;
pub(crate) struct SendData {
    pub(crate) data: Expr,
}
```
# Path: hyperlane-macros/src/response/enum.rs
```rust
pub(crate) enum HeaderOperation {
    Set,
    Add,
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
```
# Path: hyperlane-macros/src/send/mod.rs
```rust
mod r#fn;
mod r#impl;
mod r#struct;
pub(crate) use {r#fn::*, r#struct::*};
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
pub(crate) fn send_macro(item: TokenStream, position: Position) -> TokenStream {
    inject(position, item, |context| {
        quote! {
            #context.send().await;
        }
    })
}
pub(crate) fn try_send_body_macro(item: TokenStream, position: Position) -> TokenStream {
    inject(position, item, |context| {
        quote! {
            let _ = #context.try_send_body().await;
        }
    })
}
pub(crate) fn send_body_macro(item: TokenStream, position: Position) -> TokenStream {
    inject(position, item, |context| {
        quote! {
            #context.send_body().await;
        }
    })
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
# Path: hyperlane-macros/src/host/mod.rs
```rust
mod r#fn;
mod r#impl;
mod r#struct;
pub(crate) use {r#fn::*, r#struct::*};
```
# Path: hyperlane-macros/src/host/fn.rs
```rust
use crate::*;
pub(crate) fn host_macro(attr: TokenStream, item: TokenStream, position: Position) -> TokenStream {
    let multi_host: MultiHostData = parse_macro_input!(attr as MultiHostData);
    inject(position, item, |context| {
        let statements = multi_host.host_values.iter().map(|host_value| {
            quote! {
                if #context.get_request().get_host() != #host_value {
                    return;
                }
            }
        });
        quote! {
            #(#statements)*
        }
    })
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
                if #context.get_request().get_host() == #host_value {
                    return;
                }
            }
        });
        quote! {
            #(#statements)*
        }
    })
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
# Path: hyperlane-macros/src/host/struct.rs
```rust
use crate::*;
pub(crate) struct MultiHostData {
    pub(crate) host_values: Vec<Expr>,
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
    match data.variable_name.clone() {
        Some(variable_name) => {
            quote! {
                while let Ok(#variable_name) = #context.#method_ident().await {
                    #(#stmts)*
                }
            }
        }
        None => {
            quote! {
                while #context.#method_ident().await.is_ok() {
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
```
# Path: hyperlane-macros/src/request_middleware/mod.rs
```rust
mod r#fn;
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
```
# Path: hyperlane-macros/src/referer/mod.rs
```rust
mod r#fn;
mod r#impl;
mod r#struct;
pub(crate) use {r#fn::*, r#struct::*};
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
                let referer: Option<::hyperlane::RequestHeadersValueItem> = #context.get_request().try_get_header_back(REFERER);
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
pub(crate) fn reject_referer_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_referer: MultiRefererData = parse_macro_input!(attr as MultiRefererData);
    inject(position, item, |context| {
        let statements = multi_referer.referer_values.iter().map(|referer_value| {
            quote! {
                let referer: Option<::hyperlane::RequestHeadersValueItem> = #context.get_request().try_get_header_back(REFERER);
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
# Path: hyperlane-macros/src/referer/struct.rs
```rust
use crate::*;
pub(crate) struct MultiRefererData {
    pub(crate) referer_values: Vec<Expr>,
}
```
# Path: hyperlane-macros/src/version/mod.rs
```rust
mod r#fn;
pub(crate) use r#fn::*;
```
# Path: hyperlane-macros/src/version/fn.rs
```rust
use crate::*;
pub(crate) fn create_version_check(
    version: &proc_macro2::Ident,
) -> impl FnOnce(&Ident) -> TokenStream2 {
    let version_str: String = version.to_string();
    move |context| {
        let check_fn: proc_macro2::Ident = Ident::new(&format!("is_{version_str}"), context.span());
        quote! {
            if !#context.get_request().get_version().#check_fn() {
                return;
            }
        }
    }
}
macro_rules! impl_version_check_macro {
    ($name:ident, $submit_name:ident, $version:ident) => {
        pub(crate) fn $name(item: TokenStream, position: Position) -> TokenStream {
            inject(
                position,
                item,
                create_version_check(&proc_macro2::Ident::new(
                    stringify!($version),
                    proc_macro2::Span::call_site(),
                )),
            )
        }
    };
}
impl_version_check_macro!(http0_9_version_macro, http0_9_version, http0_9);
impl_version_check_macro!(http1_0_version_macro, http1_0_version, http1_0);
impl_version_check_macro!(http1_1_version_macro, http1_1_version, http1_1);
impl_version_check_macro!(http2_version_macro, http2_version, http2);
impl_version_check_macro!(http3_version_macro, http3_version, http3);
impl_version_check_macro!(
    http1_1_or_higher_version_macro,
    http1_1_or_higher_version,
    http1_1_or_higher
);
impl_version_check_macro!(http_version_macro, http_version, http);
impl_version_check_macro!(unknown_version_macro, unknown_version, unknown);
```
# Path: hyperlane-macros/src/inject/mod.rs
```rust
mod r#fn;
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
    for injectable_macro in INJECTABLE_MACROS {
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
# Path: hyperlane-process-guard/README.md
## hyperlane-process-guard
> A process guard service based on Hyperlane web framework for remote script execution and process management.
## Installation
Install `hyperlane-process-guard` via `cargo`:
```bash
cargo install hyperlane-process-guard
```
## Contribution
## Contact
# Path: hyperlane-process-guard/src/main.rs
```rust
use hyperlane::*;
use std::{env, process::Command};
fn decode_output(bytes: &[u8]) -> String {
    if bytes.is_empty() {
        return String::new();
    }
    use encoding::{DecoderTrap, Encoding};
    if cfg!(target_os = "windows") {
        encoding::all::GB18030
            .decode(bytes, DecoderTrap::Replace)
            .unwrap_or_else(|_| String::from_utf8_lossy(bytes).to_string())
    } else {
        String::from_utf8_lossy(bytes).to_string()
    }
}
struct ProcessGuardRoute;
impl ServerHook for ProcessGuardRoute {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &mut Context) {
        let body: RequestBody = ctx.get_request().get_body().clone();
        let script: String = String::from_utf8_lossy(&body).to_string();
        let output: Result<std::process::Output, std::io::Error> = if cfg!(target_os = "windows") {
            Command::new("cmd").args(["/C", &script]).output()
        } else {
            Command::new("sh").arg("-c").arg(&script).output()
        };
        let response_body: String = match output {
            Ok(result) => {
                let stdout: String = decode_output(&result.stdout);
                let stderr: String = decode_output(&result.stderr);
                let exit_code: i32 = result.status.code().unwrap_or(-1);
                format!(
                    "{{\"exit_code\": {}, \"stdout\": {:?}, \"stderr\": {:?}}}",
                    exit_code, stdout, stderr
                )
            }
            Err(error) => {
                format!("{{\"error\": \"Failed to execute script: {}\"}}", error)
            }
        };
        ctx.get_mut_response()
            .set_status_code(200)
            .set_header(CONTENT_TYPE, APPLICATION_JSON)
            .set_body(&response_body);
    }
}
struct RequestMiddleware;
impl ServerHook for RequestMiddleware {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &mut Context) {
        ctx.get_mut_response()
            .set_version(HttpVersion::Http1_1)
            .set_status_code(200)
            .set_header(SERVER, HYPERLANE)
            .set_header(CONNECTION, KEEP_ALIVE);
    }
}
struct ResponseMiddleware;
impl ServerHook for ResponseMiddleware {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &mut Context) {
        let _ = ctx.try_send().await;
    }
}
struct TaskPanicHook;
impl ServerHook for TaskPanicHook {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &mut Context) {
        ctx.get_mut_response()
            .set_version(HttpVersion::Http1_1)
            .set_status_code(500)
            .set_header(CONTENT_TYPE, TEXT_PLAIN)
            .set_body(INTERNAL_SERVER_ERROR);
        let _ = ctx.try_send().await;
    }
}
struct RequestErrorHook;
impl ServerHook for RequestErrorHook {
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    async fn handle(self, ctx: &mut Context) {
        ctx.get_mut_response()
            .set_version(HttpVersion::Http1_1)
            .set_status_code(400)
            .set_header(CONTENT_TYPE, TEXT_PLAIN)
            .set_body(BAD_REQUEST);
        let _ = ctx.try_send().await;
    }
}
#[tokio::main]
async fn main() {
    let mut server: Server = Server::default();
    let mut server_config: ServerConfig = ServerConfig::default();
    if let Ok(address) = env::var("HYPERLANE_PROCESS_GUARD_ADDRESS") {
        server_config.set_address(address);
    } else {
        panic!("HYPERLANE_PROCESS_GUARD_ADDRESS is not set");
    }
    server
        .server_config(server_config)
        .task_panic::<TaskPanicHook>()
        .request_error::<RequestErrorHook>()
        .request_middleware::<RequestMiddleware>()
        .response_middleware::<ResponseMiddleware>()
        .route::<ProcessGuardRoute>("/execute");
    let server_control_hook: ServerControlHook = server.run().await.unwrap_or_default();
    server_control_hook.wait().await;
}
```
# Path: hyperlane-quick-start/README.md
## hyperlane-quick-start
> A lightweight, high-performance, and cross-platform Rust HTTP server library built on Tokio. It simplifies modern web service development by providing built-in support for middleware, WebSocket, Server-Sent Events (SSE), and raw TCP communication. With a unified and ergonomic API across Windows, Linux, and MacOS, it enables developers to build robust, scalable, and event-driven network applications with minimal overhead and maximum flexibility.
## Official Documentation
- [Official Documentation](https://docs.ltpp.vip/hyperlane/)
## Api Docs
- [Api Docs](https://docs.rs/hyperlane/latest/)
## Contact
# Path: hyperlane-quick-start/plugin/README.md
## hyperlane-plugin
> A powerful and extensible plugin system for the hyperlane framework, providing modularity and customization capabilities.
## Official Documentation
- [Official Documentation](https://docs.ltpp.vip/hyperlane/)
## Api Docs
- [Api Docs](https://docs.rs/hyperlane/latest/)
## Contact
# Path: hyperlane-quick-start/plugin/lib.rs
```rust
pub mod common;
pub mod database;
pub mod env;
pub mod logger;
pub mod mysql;
pub mod postgresql;
pub mod process;
pub mod redis;
pub mod shutdown;
use common::*;
use std::{
    collections::HashMap,
    sync::{Arc, OnceLock},
    time::{Duration, Instant},
};
use {
    hyperlane::*,
    hyperlane_utils::{log::*, *},
    sea_orm::{ConnectionTrait, Database, DatabaseBackend, DatabaseConnection, DbErr, Statement},
};
```
# Path: hyperlane-quick-start/plugin/common/trait.rs
```rust
use super::*;
pub trait GetOrInit: Clone + Copy + Default + Send + Sync + 'static {
    type Instance: Send + Sync + 'static;
    fn get_or_init() -> &'static Self::Instance;
}
pub trait DatabaseConnectionPlugin: Clone + Copy + Default + Send + Sync + 'static {
    type InstanceConfig: Clone + Send + Sync + 'static;
    type AutoCreation: DatabaseAutoCreation<InstanceConfig = Self::InstanceConfig>;
    type Connection: Clone + Send + Sync + 'static;
    type ConnectionCache: Send + Sync + 'static;
    fn plugin_type() -> PluginType;
    fn connection_db<I>(
        instance_name: I,
        schema: Option<DatabaseSchema>,
    ) -> impl Future<Output = Result<Self::Connection, String>> + Send
    where
        I: AsRef<str> + Send;
    fn get_connection<I>(
        instance_name: I,
        schema: Option<DatabaseSchema>,
    ) -> impl Future<Output = Result<Self::Connection, String>> + Send
    where
        I: AsRef<str> + Send;
    fn perform_auto_creation(
        instance: &Self::InstanceConfig,
        schema: Option<DatabaseSchema>,
    ) -> impl Future<Output = Result<AutoCreationResult, AutoCreationError>> + Send;
}
pub trait DatabaseAutoCreation: Clone + Send + Sync + 'static {
    type InstanceConfig;
    fn new(instance: Self::InstanceConfig) -> Self;
    fn with_schema(instance: Self::InstanceConfig, schema: DatabaseSchema) -> Self
    where
        Self: Sized;
    fn create_database_if_not_exists(
        &self,
    ) -> impl Future<Output = Result<bool, AutoCreationError>> + Send;
    fn create_tables_if_not_exist(
        &self,
    ) -> impl Future<Output = Result<Vec<String>, AutoCreationError>> + Send;
    fn init_data(&self) -> impl Future<Output = Result<(), AutoCreationError>> + Send;
    fn verify_connection(&self) -> impl Future<Output = Result<(), AutoCreationError>> + Send;
}
```
# Path: hyperlane-quick-start/plugin/common/mod.rs
```rust
mod r#trait;
pub use r#trait::*;
use crate::database::*;
use std::future::Future;
```
# Path: hyperlane-quick-start/plugin/logger/mod.rs
```rust
mod r#impl;
mod r#static;
mod r#struct;
pub use r#struct::*;
use {super::*, r#static::*};
use std::{fmt::Arguments, sync::OnceLock};
use hyperlane::tokio::sync::{RwLock, RwLockReadGuard, RwLockWriteGuard};
```
# Path: hyperlane-quick-start/plugin/logger/impl.rs
```rust
use super::*;
impl GetOrInit for LoggerPlugin {
    type Instance = RwLock<FileLogger>;
    fn get_or_init() -> &'static Self::Instance {
        FILE_LOGGER.get_or_init(|| RwLock::new(FileLogger::default()))
    }
}
impl Log for Logger {
    fn enabled(&self, metadata: &Metadata) -> bool {
        metadata.level() <= max_level()
    }
    fn log(&self, record: &Record) {
        if !self.enabled(record.metadata()) {
            return;
        }
        let now_time: String = time();
        let level: Level = record.level();
        let args: &Arguments<'_> = record.args();
        let file: Option<&str> = record.file();
        let module_path: Option<&str> = record.module_path();
        let target: &str = record.target();
        let line: u32 = record.line().unwrap_or_default();
        let location: &str = file.unwrap_or(module_path.unwrap_or(target));
        let time_text: String = format!("{SPACE}{now_time}{SPACE}");
        let level_text: String = format!("{SPACE}{level}{SPACE}");
        let args_text: String = format!("{args}{SPACE}");
        let location_text: String = format!("{SPACE}{location}{COLON}{line}{SPACE}");
        let write_file_data: String = format!("{level}{location_text}{args}");
        let color: ColorType = match record.level() {
            Level::Trace => ColorType::Use(Color::Magenta),
            Level::Debug => ColorType::Use(Color::Cyan),
            Level::Info => ColorType::Use(Color::Green),
            Level::Warn => ColorType::Use(Color::Yellow),
            Level::Error => ColorType::Use(Color::Red),
        };
        let mut time_output_builder: ColorOutputBuilder<'_> = ColorOutputBuilder::new();
        let mut level_output_builder: ColorOutputBuilder<'_> = ColorOutputBuilder::new();
        let mut location_output_builder: ColorOutputBuilder<'_> = ColorOutputBuilder::new();
        let mut args_output_builder: ColorOutputBuilder<'_> = ColorOutputBuilder::new();
        let time_output: ColorOutput<'_> = time_output_builder
            .text(&time_text)
            .bold(true)
            .color(ColorType::Use(Color::White))
            .bg_color(ColorType::Use(Color::Black))
            .build();
        let level_output: ColorOutput<'_> = level_output_builder
            .text(&level_text)
            .bold(true)
            .color(ColorType::Use(Color::White))
            .bg_color(color)
            .build();
        let location_output: ColorOutput<'_> = location_output_builder
            .text(&location_text)
            .bold(true)
            .color(color)
            .build();
        let args_output: ColorOutput<'_> = args_output_builder
            .text(&args_text)
            .bold(true)
            .color(color)
            .endl(true)
            .build();
        ColorOutputListBuilder::new()
            .add(time_output)
            .add(level_output)
            .add(location_output)
            .add(args_output)
            .run();
        match record.metadata().level() {
            Level::Trace => Self::log_trace(&write_file_data),
            Level::Debug => Self::log_debug(&write_file_data),
            Level::Info => Self::log_info(&write_file_data),
            Level::Warn => Self::log_warn(&write_file_data),
            Level::Error => Self::log_error(&write_file_data),
        }
    }
    fn flush(&self) {
        Server::flush_stdout_and_stderr();
    }
}
impl Logger {
    fn read() -> RwLockReadGuard<'static, FileLogger> {
        LoggerPlugin::get_or_init().try_read().unwrap()
    }
    fn write() -> RwLockWriteGuard<'static, FileLogger> {
        LoggerPlugin::get_or_init().try_write().unwrap()
    }
    pub fn init(level: LevelFilter, file_logger: FileLogger) {
        set_logger(&LOGGER).unwrap();
        set_max_level(level);
        *Self::write() = file_logger;
    }
    pub fn log_trace<T>(data: T)
    where
        T: AsRef<str>,
    {
        Self::read().trace(data, log_handler);
    }
    #[instrument_trace]
    pub fn log_debug<T>(data: T)
    where
        T: AsRef<str>,
    {
        Self::read().debug(data, log_handler);
    }
    #[instrument_trace]
    pub fn log_info<T>(data: T)
    where
        T: AsRef<str>,
    {
        Self::read().info(data, log_handler);
    }
    #[instrument_trace]
    pub fn log_warn<T>(data: T)
    where
        T: AsRef<str>,
    {
        Self::read().warn(data, log_handler);
    }
    #[instrument_trace]
    pub fn log_error<T>(data: T)
    where
        T: AsRef<str>,
    {
        Self::read().error(data, log_handler);
    }
}
```
# Path: hyperlane-quick-start/plugin/logger/struct.rs
```rust
use super::*;
#[derive(Clone, Copy, Data, Debug, Default)]
pub struct LoggerPlugin;
#[derive(Clone, Copy, Data, Debug, Default)]
pub struct Logger;
```
# Path: hyperlane-quick-start/plugin/logger/static.rs
```rust
use super::*;
pub(super) static LOGGER: Logger = Logger;
pub(super) static FILE_LOGGER: OnceLock<RwLock<FileLogger>> = OnceLock::new();
```
# Path: hyperlane-quick-start/plugin/env/const.rs
```rust
pub const ENV_KEY_DB_CONNECTION_TIMEOUT_MILLIS: &str = "DB_CONNECTION_TIMEOUT_MILLIS";
pub const ENV_KEY_DB_RETRY_INTERVAL_MILLIS: &str = "DB_RETRY_INTERVAL_MILLIS";
pub const ENV_KEY_MYSQL: &str = "MYSQL";
pub const ENV_KEY_POSTGRESQL: &str = "POSTGRESQL";
pub const ENV_KEY_REDIS: &str = "REDIS";
pub const ENV_KEY_GPT_API_URL: &str = "GPT_API_URL";
pub const ENV_KEY_GPT_MODEL: &str = "GPT_MODEL";
pub const ENV_KEY_SERVER_PORT: &str = "SERVER_PORT";
pub const ENV_KEY_SERVER_HOST: &str = "SERVER_HOST";
pub const ENV_KEY_SERVER_BUFFER: &str = "SERVER_BUFFER";
pub const ENV_KEY_SERVER_LOG_SIZE: &str = "SERVER_LOG_SIZE";
pub const ENV_KEY_SERVER_LOG_DIR: &str = "SERVER_LOG_DIR";
pub const ENV_KEY_SERVER_INNER_PRINT: &str = "SERVER_INNER_PRINT";
pub const ENV_KEY_SERVER_INNER_LOG: &str = "SERVER_INNER_LOG";
pub const ENV_KEY_SERVER_NODELAY: &str = "SERVER_NODELAY";
pub const ENV_KEY_SERVER_TTI: &str = "SERVER_TTI";
pub const ENV_KEY_SERVER_PID_FILE_PATH: &str = "SERVER_PID_FILE_PATH";
pub const ENV_KEY_SERVER_REQUEST_HTTP_READ_TIMEOUT_MS: &str = "SERVER_REQUEST_HTTP_READ_TIMEOUT_MS";
pub const ENV_KEY_SERVER_REQUEST_MAX_BODY_SIZE: &str = "SERVER_REQUEST_MAX_BODY_SIZE";
pub const DOCKER_YAML_SERVICES: &str = "services";
pub const DOCKER_YAML_ENVIRONMENT: &str = "environment";
pub const DOCKER_YAML_PORTS: &str = "ports";
pub const DOCKER_YAML_COMMAND: &str = "command";
pub const DOCKER_SERVICE_MYSQL: &str = "mysql";
pub const DOCKER_SERVICE_POSTGRESQL: &str = "postgresql";
pub const DOCKER_SERVICE_REDIS: &str = "redis";
pub const DOCKER_MYSQL_DATABASE: &str = "MYSQL_DATABASE";
pub const DOCKER_MYSQL_USER: &str = "MYSQL_USER";
pub const DOCKER_MYSQL_PASSWORD: &str = "MYSQL_PASSWORD";
pub const DOCKER_POSTGRES_DB: &str = "POSTGRES_DB";
pub const DOCKER_POSTGRES_USER: &str = "POSTGRES_USER";
pub const DOCKER_POSTGRES_PASSWORD: &str = "POSTGRES_PASSWORD";
pub const DOCKER_REDIS_PASSWORD_FLAG: &str = "--requirepass";
```
# Path: hyperlane-quick-start/plugin/env/mod.rs
```rust
mod r#const;
mod r#impl;
mod r#static;
mod r#struct;
pub use {r#const::*, r#struct::*};
use {super::*, r#static::*};
use hyperlane_resources::{docker::*, env::*};
use std::{env::var, sync::OnceLock};
```
# Path: hyperlane-quick-start/plugin/env/impl.rs
```rust
use super::*;
impl GetOrInit for EnvPlugin {
    type Instance = EnvConfig;
    #[instrument_trace]
    fn get_or_init() -> &'static Self::Instance {
        GLOBAL_ENV_CONFIG.get_or_init(EnvConfig::default)
    }
}
impl EnvPlugin {
    #[instrument_trace]
    pub fn try_load_config() -> Result<(), String> {
        let config: EnvConfig = EnvConfig::load()?;
        GLOBAL_ENV_CONFIG
            .set(config.clone())
            .map_err(|_| "Failed to initialize global environment configuration".to_string())?;
        Ok(())
    }
}
impl MySqlInstanceConfig {
    pub(crate) fn get_connection_url(&self) -> String {
        format!(
    #[instrument_trace]
    pub(crate) fn load() -> Result<Self, String> {
        dotenvy::from_path(SERVER_ENV_FILE_PATH)
            .map_err(|error: dotenvy::Error| format!("Failed to load env file {error}"))?;
        let get_env_required = |key: &str| -> Result<String, String> {
            var(key).map_err(|_| format!("Environment variable {} is not set", key))
        };
        let get_env_u16 = |key: &str| -> Result<u16, String> {
            var(key)
                .map_err(|_| format!("Environment variable {} is not set", key))?
                .parse()
                .map_err(|_| format!("Environment variable {} must be a valid u16", key))
        };
        let get_env_u32 = |key: &str| -> Result<u32, String> {
            var(key)
                .map_err(|_| format!("Environment variable {} is not set", key))?
                .parse()
                .map_err(|_| format!("Environment variable {} must be a valid u32", key))
        };
        let get_env_u64 = |key: &str| -> Result<u64, String> {
            var(key)
                .map_err(|_| format!("Environment variable {} is not set", key))?
                .parse()
                .map_err(|_| format!("Environment variable {} must be a valid u64", key))
        };
        let get_env_usize = |key: &str| -> Result<usize, String> {
            var(key)
                .map_err(|_| format!("Environment variable {} is not set", key))?
                .parse()
                .map_err(|_| format!("Environment variable {} must be a valid usize", key))
        };
        let get_env_bool = |key: &str| -> Result<bool, String> {
            let value = var(key).map_err(|_| format!("Environment variable {} is not set", key))?;
            if value.eq_ignore_ascii_case("true") || value.eq_ignore_ascii_case("1") {
                Ok(true)
            } else if value.eq_ignore_ascii_case("false") || value.eq_ignore_ascii_case("0") {
                Ok(false)
            } else {
                Err(format!(
                    "Environment variable {} must be true/false or 1/0",
                    key
                ))
            }
        };
        let docker_config: DockerComposeConfig =
            Self::load_from_docker_compose(SERVER_DOCKER_COMPOSE_FILE_PATH).unwrap_or_default();
        let mysql_instances: Vec<MySqlInstanceConfig> =
            Self::parse_mysql_instances(&docker_config)?;
        let postgresql_instances: Vec<PostgreSqlInstanceConfig> =
            Self::parse_postgresql_instances(&docker_config)?;
        let redis_instances: Vec<RedisInstanceConfig> =
            Self::parse_redis_instances(&docker_config)?;
        let config: EnvConfig = EnvConfig {
            db_connection_timeout_millis: get_env_u64(ENV_KEY_DB_CONNECTION_TIMEOUT_MILLIS)?,
            db_retry_interval_millis: get_env_u64(ENV_KEY_DB_RETRY_INTERVAL_MILLIS)?,
            gpt_api_url: var(ENV_KEY_GPT_API_URL).unwrap_or_default(),
            gpt_model: var(ENV_KEY_GPT_MODEL).unwrap_or_default(),
            mysql_instances,
            postgresql_instances,
            redis_instances,
            server_port: get_env_u16(ENV_KEY_SERVER_PORT)?,
            server_host: get_env_required(ENV_KEY_SERVER_HOST)?,
            server_buffer: get_env_usize(ENV_KEY_SERVER_BUFFER)?,
            server_log_size: get_env_usize(ENV_KEY_SERVER_LOG_SIZE)?,
            server_log_dir: get_env_required(ENV_KEY_SERVER_LOG_DIR)?,
            server_inner_print: get_env_bool(ENV_KEY_SERVER_INNER_PRINT)?,
            server_inner_log: get_env_bool(ENV_KEY_SERVER_INNER_LOG)?,
            server_nodelay: Some(get_env_bool(ENV_KEY_SERVER_NODELAY)?),
            server_tti: Some(get_env_u32(ENV_KEY_SERVER_TTI)?),
            server_pid_file_path: get_env_required(ENV_KEY_SERVER_PID_FILE_PATH)?,
            server_request_http_read_timeout_ms: get_env_u64(
                ENV_KEY_SERVER_REQUEST_HTTP_READ_TIMEOUT_MS,
            )?,
            server_request_max_body_size: get_env_usize(ENV_KEY_SERVER_REQUEST_MAX_BODY_SIZE)?,
        };
        Ok(config)
    }
    fn parse_mysql_instances(
        docker_config: &DockerComposeConfig,
    ) -> Result<Vec<MySqlInstanceConfig>, String> {
        let mysql_json: String = var(ENV_KEY_MYSQL)
            .map_err(|_| format!("Environment variable {} is not set", ENV_KEY_MYSQL))?
            .trim_matches('\'')
            .to_string();
        let mut instances: Vec<MySqlInstanceConfig> = serde_json::from_str(&mysql_json)
            .map_err(|error: Error| format!("Failed to parse {}: {}", ENV_KEY_MYSQL, error))?;
        for instance in instances.iter_mut() {
            if instance.get_port() == 0 {
                instance.set_port(docker_config.get_mysql_port().unwrap_or(3306));
            }
        }
        Ok(instances)
    }
    fn parse_postgresql_instances(
        docker_config: &DockerComposeConfig,
    ) -> Result<Vec<PostgreSqlInstanceConfig>, String> {
        let postgresql_json: String = var(ENV_KEY_POSTGRESQL)
            .map_err(|_| format!("Environment variable {} is not set", ENV_KEY_POSTGRESQL))?
            .trim_matches('\'')
            .to_string();
        let mut instances: Vec<PostgreSqlInstanceConfig> = serde_json::from_str(&postgresql_json)
            .map_err(|error: Error| {
            format!("Failed to parse {}: {}", ENV_KEY_POSTGRESQL, error)
        })?;
        for instance in instances.iter_mut() {
            if instance.get_port() == 0 {
                instance.set_port(docker_config.get_postgresql_port().unwrap_or(5432));
            }
        }
        Ok(instances)
    }
    fn parse_redis_instances(
        docker_config: &DockerComposeConfig,
    ) -> Result<Vec<RedisInstanceConfig>, String> {
        let redis_json: String = var(ENV_KEY_REDIS)
            .map_err(|_| format!("Environment variable {} is not set", ENV_KEY_REDIS))?
            .trim_matches('\'')
            .to_string();
        let mut instances: Vec<RedisInstanceConfig> = serde_json::from_str(&redis_json)
            .map_err(|error: Error| format!("Failed to parse {}: {}", ENV_KEY_REDIS, error))?;
        for instance in instances.iter_mut() {
            if instance.get_port() == 0 {
                instance.set_port(docker_config.get_redis_port().unwrap_or(6379));
            }
        }
        Ok(instances)
    }
    #[instrument_trace]
    fn load_from_docker_compose(file_path: &str) -> Result<DockerComposeConfig, String> {
        let docker_compose_content: Vec<u8> =
            read_from_file(file_path).map_err(|error: Box<dyn std::error::Error>| {
                format!("Failed to read docker-compose.yml {error}")
            })?;
        let yaml: serde_yaml::Value = serde_yaml::from_slice(&docker_compose_content).map_err(
            |error: serde_yaml::Error| format!("Failed to parse docker-compose.yml {error}"),
        )?;
        let mut config: DockerComposeConfig = DockerComposeConfig::default();
        if let Some(mysql) = yaml
            .get(DOCKER_YAML_SERVICES)
            .and_then(|services| services.get(DOCKER_SERVICE_MYSQL))
        {
            if let Some(env) = mysql.get(DOCKER_YAML_ENVIRONMENT) {
                if let Some(database) = env
                    .get(DOCKER_MYSQL_DATABASE)
                    .and_then(|value| value.as_str())
                    .map(String::from)
                {
                    config.set_mysql_database(Some(database));
                }
                if let Some(username) = env
                    .get(DOCKER_MYSQL_USER)
                    .and_then(|value| value.as_str())
                    .map(String::from)
                {
                    config.set_mysql_username(Some(username));
                }
                if let Some(password) = env
                    .get(DOCKER_MYSQL_PASSWORD)
                    .and_then(|value| value.as_str())
                    .map(String::from)
                {
                    config.set_mysql_password(Some(password));
                }
            }
            if let Some(ports) = mysql
                .get(DOCKER_YAML_PORTS)
                .and_then(|ports_value| ports_value.as_sequence())
                && let Some(port_mapping) = ports.first().and_then(|port| port.as_str())
                && let Some(host_port) = port_mapping.split(':').next()
                && let Ok(port) = host_port.parse()
            {
                config.set_mysql_port(Some(port));
            }
        }
        if let Some(postgresql) = yaml
            .get(DOCKER_YAML_SERVICES)
            .and_then(|services| services.get(DOCKER_SERVICE_POSTGRESQL))
        {
            if let Some(env) = postgresql.get(DOCKER_YAML_ENVIRONMENT) {
                if let Some(database) = env
                    .get(DOCKER_POSTGRES_DB)
                    .and_then(|value| value.as_str())
                    .map(String::from)
                {
                    config.set_postgresql_database(Some(database));
                }
                if let Some(username) = env
                    .get(DOCKER_POSTGRES_USER)
                    .and_then(|value| value.as_str())
                    .map(String::from)
                {
                    config.set_postgresql_username(Some(username));
                }
                if let Some(password) = env
                    .get(DOCKER_POSTGRES_PASSWORD)
                    .and_then(|value| value.as_str())
                    .map(String::from)
                {
                    config.set_postgresql_password(Some(password));
                }
            }
            if let Some(ports) = postgresql
                .get(DOCKER_YAML_PORTS)
                .and_then(|ports_value| ports_value.as_sequence())
                && let Some(port_mapping) = ports.first().and_then(|port| port.as_str())
                && let Some(host_port) = port_mapping.split(':').next()
                && let Ok(port) = host_port.parse()
            {
                config.set_postgresql_port(Some(port));
            }
        }
        if let Some(redis) = yaml
            .get(DOCKER_YAML_SERVICES)
            .and_then(|services| services.get(DOCKER_SERVICE_REDIS))
        {
            if let Some(command) = redis
                .get(DOCKER_YAML_COMMAND)
                .and_then(|command_value| command_value.as_str())
                && let Some(password_part) = command.split(DOCKER_REDIS_PASSWORD_FLAG).nth(1)
            {
                config.set_redis_password(Some(password_part.trim().to_string()));
            }
            if let Some(ports) = redis
                .get(DOCKER_YAML_PORTS)
                .and_then(|ports_value| ports_value.as_sequence())
                && let Some(port_mapping) = ports.first().and_then(|port| port.as_str())
                && let Some(host_port) = port_mapping.split(':').next()
                && let Ok(port) = host_port.parse()
            {
                config.set_redis_port(Some(port));
            }
        }
        Ok(config)
    }
    #[instrument_trace]
    pub fn log_config() {
        #[cfg(debug_assertions)]
        let is_dev: bool = true;
        #[cfg(not(debug_assertions))]
        let is_dev: bool = false;
        let config: &EnvConfig = EnvPlugin::get_or_init();
        if is_dev {
            info!("Environment Configuration Loaded Successfully");
            info!("Database Configuration:");
            info!(
                "  DB_CONNECTION_TIMEOUT_MILLIS: {}",
                config.get_db_connection_timeout_millis()
            );
            info!(
                "  DB_RETRY_INTERVAL_MILLIS: {}",
                config.get_db_retry_interval_millis()
            );
            info!("GPT Configuration:");
            info!(
                "  GPT_API_URL: {}",
                if config.get_gpt_api_url().is_empty() {
                    "(not set)"
                } else {
                    config.get_gpt_api_url()
                }
            );
            info!(
                "  GPT_MODEL: {}",
                if config.get_gpt_model().is_empty() {
                    "(not set)"
                } else {
                    config.get_gpt_model()
                }
            );
            info!("MySQL Configuration:");
            if config.get_mysql_instances().is_empty() {
                info!("  (no MySQL instances configured)");
            } else {
                for instance in config.get_mysql_instances() {
                    info!("  Instance '{}'", instance.get_name());
                    info!("    Host: {}", instance.get_host());
                    info!("    Port: {}", instance.get_port());
                    info!("    Database: {}", instance.get_database());
                    info!("    Username: {}", instance.get_username());
                    info!("    Password: {}", instance.get_password());
                }
            }
            info!("PostgreSQL Configuration:");
            if config.get_postgresql_instances().is_empty() {
                info!("  (no PostgreSQL instances configured)");
            } else {
                for instance in config.get_postgresql_instances() {
                    info!("  Instance '{}'", instance.get_name());
                    info!("    Host: {}", instance.get_host());
                    info!("    Port: {}", instance.get_port());
                    info!("    Database: {}", instance.get_database());
                    info!("    Username: {}", instance.get_username());
                    info!("    Password: {}", instance.get_password());
                }
            }
            info!("Redis Configuration:");
            if config.get_redis_instances().is_empty() {
                info!("  (no Redis instances configured)");
            } else {
                for instance in config.get_redis_instances() {
                    info!("  Instance '{}'", instance.get_name());
                    info!("    Host: {}", instance.get_host());
                    info!("    Port: {}", instance.get_port());
                    info!(
                        "    Username: {}",
                        if instance.get_username().is_empty() {
                            "(none)"
                        } else {
                            instance.get_username()
                        }
                    );
                    info!("    Password: {}", instance.get_password());
                }
            }
            info!("Server Configuration:");
            info!("  SERVER_PORT: {}", config.get_server_port());
            info!("  SERVER_HOST: {}", config.get_server_host());
            info!("  SERVER_BUFFER: {}", config.get_server_buffer());
            info!("  SERVER_LOG_SIZE: {}", config.get_server_log_size());
            info!("  SERVER_LOG_DIR: {}", config.get_server_log_dir());
            info!("  SERVER_INNER_PRINT: {}", config.get_server_inner_print());
            info!("  SERVER_INNER_LOG: {}", config.get_server_inner_log());
            info!("  SERVER_NODELAY: {:?}", config.get_server_nodelay());
            info!("  SERVER_TTI: {:?}", config.get_server_tti());
            info!(
                "  SERVER_PID_FILE_PATH: {}",
                config.get_server_pid_file_path()
            );
            info!(
                "  SERVER_REQUEST_HTTP_READ_TIMEOUT_MS: {}",
                config.get_server_request_http_read_timeout_ms()
            );
            info!(
                "  SERVER_REQUEST_MAX_BODY_SIZE: {}",
                config.get_server_request_max_body_size()
            );
        } else {
            info!(
                "GPT API URL {}",
                if config.get_gpt_api_url().is_empty() {
                    "(not set)"
                } else {
                    config.get_gpt_api_url()
                }
            );
            info!(
                "GPT Model {}",
                if config.get_gpt_model().is_empty() {
                    "(not set)"
                } else {
                    config.get_gpt_model()
                }
            );
            info!("MySQL Configuration:");
            if config.get_mysql_instances().is_empty() {
                info!("  (no MySQL instances configured)");
            } else {
                for instance in config.get_mysql_instances() {
                    info!(
```
# Path: hyperlane-quick-start/plugin/env/struct.rs
```rust
use super::*;
#[derive(Clone, Copy, Data, Debug, Default)]
pub struct EnvPlugin;
#[derive(Clone, Data, Debug, Default)]
pub struct DockerComposeConfig {
    pub(super) mysql_database: Option<String>,
    pub(super) mysql_password: Option<String>,
    #[get(type(copy))]
    pub(super) mysql_port: Option<usize>,
    pub(super) mysql_username: Option<String>,
    pub(super) postgresql_database: Option<String>,
    pub(super) postgresql_password: Option<String>,
    #[get(type(copy))]
    pub(super) postgresql_port: Option<usize>,
    pub(super) postgresql_username: Option<String>,
    pub(super) redis_password: Option<String>,
    #[get(type(copy))]
    pub(super) redis_port: Option<usize>,
    pub(super) redis_username: Option<String>,
}
#[derive(Clone, Data, Debug, Default)]
pub struct EnvConfig {
    #[get(type(copy))]
    pub(super) db_connection_timeout_millis: u64,
    #[get(type(copy))]
    pub(super) db_retry_interval_millis: u64,
    #[get(pub)]
    pub(super) gpt_api_url: String,
    #[get(pub)]
    pub(super) gpt_model: String,
    pub(super) mysql_instances: Vec<MySqlInstanceConfig>,
    pub(super) postgresql_instances: Vec<PostgreSqlInstanceConfig>,
    pub(super) redis_instances: Vec<RedisInstanceConfig>,
    #[get(type(copy))]
    pub(super) server_port: u16,
    #[get(pub)]
    pub(super) server_host: String,
    #[get(type(copy))]
    pub(super) server_buffer: usize,
    #[get(type(copy))]
    pub(super) server_log_size: usize,
    #[get(pub)]
    pub(super) server_log_dir: String,
    #[get(type(copy))]
    pub(super) server_inner_print: bool,
    #[get(type(copy))]
    pub(super) server_inner_log: bool,
    #[get(type(copy))]
    pub(super) server_nodelay: Option<bool>,
    #[get(type(copy))]
    pub(super) server_tti: Option<u32>,
    #[get(pub)]
    pub(super) server_pid_file_path: String,
    #[get(type(copy))]
    pub(super) server_request_http_read_timeout_ms: u64,
    #[get(type(copy))]
    pub(super) server_request_max_body_size: usize,
}
#[derive(Clone, Debug, Default, serde::Deserialize, Data)]
pub struct MySqlInstanceConfig {
    #[serde(rename = "name")]
    pub(super) name: String,
    #[serde(rename = "host")]
    pub(super) host: String,
    #[get(type(copy))]
    #[serde(default, rename = "port")]
    pub(super) port: usize,
    #[serde(rename = "database")]
    pub(super) database: String,
    #[serde(rename = "username")]
    pub(super) username: String,
    #[serde(rename = "password")]
    pub(super) password: String,
}
#[derive(Clone, Debug, Default, serde::Deserialize, Data)]
pub struct PostgreSqlInstanceConfig {
    #[serde(rename = "name")]
    pub(super) name: String,
    #[serde(rename = "host")]
    pub(super) host: String,
    #[get(type(copy))]
    #[serde(default, rename = "port")]
    pub(super) port: usize,
    #[serde(rename = "database")]
    pub(super) database: String,
    #[serde(rename = "username")]
    pub(super) username: String,
    #[serde(rename = "password")]
    pub(super) password: String,
}
#[derive(Clone, Debug, Default, serde::Deserialize, Data)]
pub struct RedisInstanceConfig {
    #[serde(rename = "name")]
    pub(super) name: String,
    #[serde(rename = "host")]
    pub(super) host: String,
    #[get(type(copy))]
    #[serde(default, rename = "port")]
    pub(super) port: usize,
    #[serde(default, rename = "username")]
    pub(super) username: String,
    #[serde(rename = "password")]
    pub(super) password: String,
}
```
# Path: hyperlane-quick-start/plugin/env/static.rs
```rust
use super::*;
pub static GLOBAL_ENV_CONFIG: OnceLock<EnvConfig> = OnceLock::new();
```
# Path: hyperlane-quick-start/plugin/redis/const.rs
```rust
pub const DEFAULT_REDIS_INSTANCE_NAME: &str = "redis_default";
```
# Path: hyperlane-quick-start/plugin/redis/mod.rs
```rust
mod r#const;
mod r#impl;
mod r#static;
mod r#struct;
mod r#type;
pub use {r#const::*, r#struct::*, r#type::*};
use {super::*, database::*, env::*, r#static::*};
use {
    hyperlane_utils::redis::*,
    tokio::{
        spawn,
        sync::{RwLock, RwLockWriteGuard},
        task::{JoinHandle, spawn_blocking},
        time::timeout,
    },
};
```
# Path: hyperlane-quick-start/plugin/redis/impl.rs
```rust
use super::*;
impl GetOrInit for RedisPlugin {
    type Instance = RwLock<RedisConnectionMap>;
    #[instrument_trace]
    fn get_or_init() -> &'static Self::Instance {
        REDIS_CONNECTIONS.get_or_init(|| RwLock::new(HashMap::new()))
    }
}
impl DatabaseConnectionPlugin for RedisPlugin {
    type InstanceConfig = RedisInstanceConfig;
    type AutoCreation = RedisAutoCreation;
    type Connection = ArcRwLock<Connection>;
    type ConnectionCache = RwLock<RedisConnectionMap>;
    #[instrument_trace]
    fn plugin_type() -> PluginType {
        PluginType::Redis
    }
    #[instrument_trace]
    async fn connection_db<I>(
        instance_name: I,
        _schema: Option<DatabaseSchema>,
    ) -> Result<Self::Connection, String>
    where
        I: AsRef<str> + Send,
    {
        let instance_name_str: &str = instance_name.as_ref();
        let env: &'static EnvConfig = EnvPlugin::get_or_init();
        let instance: &RedisInstanceConfig = env
            .get_redis_instance(instance_name_str)
            .ok_or_else(|| format!("Redis instance '{instance_name_str}' not found"))?;
        match Self::perform_auto_creation(instance, _schema).await {
            Ok(result) => {
                if result.has_changes() {
                    AutoCreationLogger::log_auto_creation_complete(
                        database::PluginType::Redis,
                        &result,
                    )
                    .await;
                }
            }
            Err(error) => {
                AutoCreationLogger::log_auto_creation_error(
                    &error,
                    "Auto-creation process",
                    database::PluginType::Redis,
                    Some(instance.get_name().as_str()),
                )
                .await;
                if !error.should_continue() {
                    return Err(error.to_string());
                }
            }
        }
        let db_url: String = instance.get_connection_url();
        let client: Client = Client::open(db_url).map_err(|error: redis::RedisError| {
            let error_msg: String = error.to_string();
            let instance_name_clone: String = instance_name_str.to_string();
            let error_msg_clone: String = error_msg.clone();
            spawn(async move {
                AutoCreationLogger::log_connection_verification(
                    database::PluginType::Redis,
                    &instance_name_clone,
                    false,
                    Some(&error_msg_clone),
                )
                .await;
            });
            error_msg
        })?;
        let timeout_duration: Duration = DatabasePlugin::get_connection_timeout_duration();
        let timeout_seconds: u64 = timeout_duration.as_secs();
        let connection_task: JoinHandle<Result<Connection, RedisError>> =
            spawn_blocking(move || client.get_connection());
        let connection: Connection = match timeout(timeout_duration, connection_task).await {
            Ok(join_result) => match join_result {
                Ok(result) => result.map_err(|error: redis::RedisError| {
                    let error_msg: String = error.to_string();
                    let instance_name_clone: String = instance_name_str.to_string();
                    let error_msg_clone: String = error_msg.clone();
                    spawn(async move {
                        AutoCreationLogger::log_connection_verification(
                            database::PluginType::Redis,
                            &instance_name_clone,
                            false,
                            Some(&error_msg_clone),
                        )
                        .await;
                    });
                    error_msg
                })?,
                Err(_) => {
                    let error_msg: String = "Redis connection task failed".to_string();
                    let instance_name_clone: String = instance_name_str.to_string();
                    let error_msg_clone: String = error_msg.clone();
                    spawn(async move {
                        AutoCreationLogger::log_connection_verification(
                            database::PluginType::Redis,
                            &instance_name_clone,
                            false,
                            Some(&error_msg_clone),
                        )
                        .await;
                    });
                    return Err(error_msg);
                }
            },
            Err(_) => {
                let error_msg: String =
                    format!("Redis connection timeout after {timeout_seconds} seconds");
                let instance_name_clone: String = instance_name_str.to_string();
                let error_msg_clone: String = error_msg.clone();
                spawn(async move {
                    AutoCreationLogger::log_connection_verification(
                        database::PluginType::Redis,
                        &instance_name_clone,
                        false,
                        Some(&error_msg_clone),
                    )
                    .await;
                });
                return Err(error_msg);
            }
        };
        Ok(arc_rwlock(connection))
    }
    #[instrument_trace]
    async fn get_connection<I>(
        instance_name: I,
        schema: Option<DatabaseSchema>,
    ) -> Result<Self::Connection, String>
    where
        I: AsRef<str> + Send,
    {
        let instance_name_str: &str = instance_name.as_ref();
        let duration: Duration = DatabasePlugin::get_retry_duration();
        {
            if let Some(cache) = Self::get_or_init().read().await.get(instance_name_str) {
                match cache.try_get_result() {
                    Ok(conn) => return Ok(conn.clone()),
                    Err(error) => {
                        if !cache.is_expired(duration) {
                            return Err(error.clone());
                        }
                    }
                }
            }
        }
        let mut connections: RwLockWriteGuard<'_, RedisConnectionMap> =
            Self::get_or_init().write().await;
        if let Some(cache) = connections.get(instance_name_str) {
            match cache.try_get_result() {
                Ok(conn) => return Ok(conn.clone()),
                Err(error) => {
                    if !cache.is_expired(duration) {
                        return Err(error.clone());
                    }
                }
            }
        }
        connections.remove(instance_name_str);
        drop(connections);
        let new_connection: Result<ArcRwLock<Connection>, String> =
            Self::connection_db(instance_name_str, schema).await;
        let mut connections: RwLockWriteGuard<'_, RedisConnectionMap> =
            Self::get_or_init().write().await;
        connections.insert(
            instance_name_str.to_string(),
            ConnectionCache::new(new_connection.clone()),
        );
        new_connection
    }
    #[instrument_trace]
    async fn perform_auto_creation(
        instance: &Self::InstanceConfig,
        schema: Option<DatabaseSchema>,
    ) -> Result<AutoCreationResult, AutoCreationError> {
        let start_time: Instant = Instant::now();
        let mut result: AutoCreationResult = AutoCreationResult::default();
        AutoCreationLogger::log_auto_creation_start(
            database::PluginType::Redis,
            instance.get_name(),
        )
        .await;
        let auto_creator: RedisAutoCreation = match schema {
            Some(s) => RedisAutoCreation::with_schema(instance.clone(), s),
            None => RedisAutoCreation::new(instance.clone()),
        };
        match auto_creator.create_database_if_not_exists().await {
            Ok(created) => {
                result.set_database_created(created);
            }
            Err(error) => {
                AutoCreationLogger::log_auto_creation_error(
                    &error,
                    "Database validation",
                    database::PluginType::Redis,
                    Some(instance.get_name().as_str()),
                )
                .await;
                if !error.should_continue() {
                    result.set_duration(start_time.elapsed());
                    return Err(error);
                }
                result.get_mut_errors().push(error.to_string());
            }
        }
        match auto_creator.create_tables_if_not_exist().await {
            Ok(operations) => {
                result.set_tables_created(operations);
            }
            Err(error) => {
                AutoCreationLogger::log_auto_creation_error(
                    &error,
                    "Namespace setup",
                    database::PluginType::Redis,
                    Some(instance.get_name().as_str()),
                )
                .await;
                result.get_mut_errors().push(error.to_string());
            }
        }
        if let Err(error) = auto_creator.verify_connection().await {
            AutoCreationLogger::log_auto_creation_error(
                &error,
                "Connection verification",
                database::PluginType::Redis,
                Some(instance.get_name().as_str()),
            )
            .await;
            if !error.should_continue() {
                result.set_duration(start_time.elapsed());
                return Err(error);
            }
            result.get_mut_errors().push(error.to_string());
        }
        result.set_duration(start_time.elapsed());
        AutoCreationLogger::log_auto_creation_complete(database::PluginType::Redis, &result).await;
        Ok(result)
    }
}
impl Default for RedisAutoCreation {
    #[instrument_trace]
    fn default() -> Self {
        if let Some(instance) = EnvPlugin::get_or_init().get_default_redis_instance() {
            Self::new(instance.clone())
        } else {
            let default_instance: RedisInstanceConfig = RedisInstanceConfig::default();
            Self::new(default_instance)
        }
    }
}
impl RedisAutoCreation {
    #[instrument_trace]
    async fn create_mutable_connection(&self) -> Result<Connection, AutoCreationError> {
        let db_url: String = self.instance.get_connection_url();
        let client: Client = Client::open(db_url).map_err(|error: RedisError| {
            let error_msg: String = error.to_string();
            if error_msg.contains("authentication failed") || error_msg.contains("NOAUTH") {
                AutoCreationError::InsufficientPermissions(format!(
                    "Redis authentication failed {error_msg}"
                ))
            } else if error_msg.contains("Connection refused") || error_msg.contains("timeout") {
                AutoCreationError::ConnectionFailed(format!(
                    "Cannot connect to Redis server {error_msg}"
                ))
            } else {
                AutoCreationError::DatabaseError(format!("Redis connection error {error_msg}"))
            }
        })?;
        let timeout_duration: Duration = DatabasePlugin::get_connection_timeout_duration();
        let timeout_seconds: u64 = timeout_duration.as_secs();
        let connection_task: JoinHandle<Result<Connection, RedisError>> =
            spawn_blocking(move || client.get_connection());
        let connection: Connection = match timeout(timeout_duration, connection_task).await {
            Ok(join_result) => match join_result {
                Ok(result) => result.map_err(|error: RedisError| {
                    let error_msg: String = error.to_string();
                    if error_msg.contains("authentication failed") || error_msg.contains("NOAUTH") {
                        AutoCreationError::InsufficientPermissions(format!(
                            "Redis authentication failed {error_msg}"
                        ))
                    } else if error_msg.contains("Connection refused")
                        || error_msg.contains("timeout")
                    {
                        AutoCreationError::ConnectionFailed(format!(
                            "Cannot connect to Redis server {error_msg}"
                        ))
                    } else {
                        AutoCreationError::DatabaseError(format!(
                            "Redis connection error {error_msg}"
                        ))
                    }
                })?,
                Err(_) => {
                    return Err(AutoCreationError::ConnectionFailed(
                        "Redis connection task failed".to_string(),
                    ));
                }
            },
            Err(_) => {
                return Err(AutoCreationError::Timeout(format!(
                    "Redis connection timeout after {timeout_seconds} seconds"
                )));
            }
        };
        Ok(connection)
    }
    #[instrument_trace]
    async fn validate_redis_server(&self) -> Result<(), AutoCreationError> {
        let mut conn: Connection = self.create_mutable_connection().await?;
        let pong: String = redis::cmd("PING")
            .query(&mut conn)
            .map_err(|error: RedisError| {
                AutoCreationError::ConnectionFailed(format!("Redis PING failed {error}"))
            })?;
        if pong != "PONG" {
            return Err(AutoCreationError::ConnectionFailed(
                "Redis PING returned unexpected response".to_string(),
            ));
        }
        let info: String =
            redis::cmd("INFO")
                .arg("server")
                .query(&mut conn)
                .map_err(|error: RedisError| {
                    AutoCreationError::DatabaseError(format!(
                        "Failed to get Redis server info {error}"
                    ))
                })?;
        if info.contains("redis_version:") {
            AutoCreationLogger::log_connection_verification(
                database::PluginType::Redis,
                self.instance.get_name().as_str(),
                true,
                None,
            )
            .await;
        }
        Ok(())
    }
    #[instrument_trace]
    async fn setup_redis_namespace(&self) -> Result<Vec<String>, AutoCreationError> {
        let mut setup_operations: Vec<String> = Vec::new();
        let mut conn: Connection = self.create_mutable_connection().await?;
        let app_key: String = format!("{}:initialized", self.instance.get_name());
        let exists: i32 = redis::cmd("EXISTS")
            .arg(&app_key)
            .query(&mut conn)
            .map_err(|error: RedisError| {
                AutoCreationError::DatabaseError(format!(
                    "Failed to check Redis key existence {error}"
                ))
            })?;
        if exists == 0 {
            let _: () = redis::cmd("SET")
                .arg(&app_key)
                .arg("true")
                .query(&mut conn)
                .map_err(|error: RedisError| {
                    AutoCreationError::DatabaseError(format!(
                        "Failed to set Redis initialization key {error}"
                    ))
                })?;
            setup_operations.push(app_key.clone());
            let config_key: String = format!("{}:config:version", self.instance.get_name());
            let _: () = redis::cmd("SET")
                .arg(&config_key)
                .arg("1.0.0")
                .query(&mut conn)
                .map_err(|error: RedisError| {
                    AutoCreationError::DatabaseError(format!(
                        "Failed to set Redis config key {error}"
                    ))
                })?;
            setup_operations.push(config_key);
        }
        Ok(setup_operations)
    }
}
impl DatabaseAutoCreation for RedisAutoCreation {
    type InstanceConfig = RedisInstanceConfig;
    #[instrument_trace]
    fn new(instance: Self::InstanceConfig) -> Self {
        Self {
            instance,
            schema: DatabaseSchema::default(),
        }
    }
    #[instrument_trace]
    fn with_schema(instance: Self::InstanceConfig, schema: DatabaseSchema) -> Self
    where
        Self: Sized,
    {
        Self { instance, schema }
    }
    #[instrument_trace]
    async fn create_database_if_not_exists(&self) -> Result<bool, AutoCreationError> {
        self.validate_redis_server().await?;
        AutoCreationLogger::log_database_exists(
            self.instance.get_name().as_str(),
            database::PluginType::Redis,
        )
        .await;
        Ok(false)
    }
    #[instrument_trace]
    async fn create_tables_if_not_exist(&self) -> Result<Vec<String>, AutoCreationError> {
        let setup_operations: Vec<String> = self.setup_redis_namespace().await?;
        if !setup_operations.is_empty() {
            AutoCreationLogger::log_tables_created(
                &setup_operations,
                self.instance.get_name().as_str(),
                database::PluginType::Redis,
            )
            .await;
        } else {
            AutoCreationLogger::log_tables_created(
                &[],
                self.instance.get_name().as_str(),
                database::PluginType::Redis,
            )
            .await;
        }
        Ok(setup_operations)
    }
    #[instrument_trace]
    async fn init_data(&self) -> Result<(), AutoCreationError> {
        Ok(())
    }
    #[instrument_trace]
    async fn verify_connection(&self) -> Result<(), AutoCreationError> {
        match self.validate_redis_server().await {
            Ok(_) => {
                AutoCreationLogger::log_connection_verification(
                    database::PluginType::Redis,
                    self.instance.get_name().as_str(),
                    true,
                    None,
                )
                .await;
                Ok(())
            }
            Err(error) => {
                AutoCreationLogger::log_connection_verification(
                    database::PluginType::Redis,
                    self.instance.get_name().as_str(),
                    false,
                    Some(&error.to_string()),
                )
                .await;
                Err(error)
            }
        }
    }
}
```
# Path: hyperlane-quick-start/plugin/redis/struct.rs
```rust
use super::*;
#[derive(Clone, Copy, Data, Debug, Default)]
pub struct RedisPlugin;
#[derive(Clone, Data, Debug, New)]
pub struct RedisAutoCreation {
    pub(super) instance: RedisInstanceConfig,
    #[new(skip)]
    pub(super) schema: DatabaseSchema,
}
```
# Path: hyperlane-quick-start/plugin/redis/type.rs
```rust
use super::*;
pub type RedisConnectionMap = HashMap<String, ConnectionCache<ArcRwLock<Connection>>>;
```
# Path: hyperlane-quick-start/plugin/redis/static.rs
```rust
use super::*;
pub static REDIS_CONNECTIONS: OnceLock<RwLock<RedisConnectionMap>> = OnceLock::new();
```
# Path: hyperlane-quick-start/plugin/mysql/const.rs
```rust
pub const DEFAULT_MYSQL_INSTANCE_NAME: &str = "mysql_default";
```
# Path: hyperlane-quick-start/plugin/mysql/mod.rs
```rust
mod r#const;
mod r#impl;
mod r#static;
mod r#struct;
pub use {r#const::*, r#struct::*};
use {super::*, database::*, env::*, r#static::*};
use tokio::{
    spawn,
    sync::{RwLock, RwLockWriteGuard},
    time::timeout,
};
```
# Path: hyperlane-quick-start/plugin/mysql/impl.rs
```rust
use super::*;
impl GetOrInit for MySqlPlugin {
    type Instance = RwLock<HashMap<String, ConnectionCache<DatabaseConnection>>>;
    #[instrument_trace]
    fn get_or_init() -> &'static Self::Instance {
        MYSQL_CONNECTIONS.get_or_init(|| RwLock::new(HashMap::new()))
    }
}
impl DatabaseConnectionPlugin for MySqlPlugin {
    type InstanceConfig = MySqlInstanceConfig;
    type AutoCreation = MySqlAutoCreation;
    type Connection = DatabaseConnection;
    type ConnectionCache = RwLock<HashMap<String, ConnectionCache<Self::Connection>>>;
    #[instrument_trace]
    fn plugin_type() -> PluginType {
        PluginType::MySQL
    }
    #[instrument_trace]
    async fn connection_db<I>(
        instance_name: I,
        schema: Option<DatabaseSchema>,
    ) -> Result<Self::Connection, String>
    where
        I: AsRef<str> + Send,
    {
        let instance_name_str: &str = instance_name.as_ref();
        let env: &'static EnvConfig = EnvPlugin::get_or_init();
        let instance: &MySqlInstanceConfig = env
            .get_mysql_instance(instance_name_str)
            .ok_or_else(|| format!("MySQL instance '{instance_name_str}' not found"))?;
        match Self::perform_auto_creation(instance, schema.clone()).await {
            Ok(result) => {
                if result.has_changes() {
                    AutoCreationLogger::log_auto_creation_complete(PluginType::MySQL, &result)
                        .await;
                }
            }
            Err(error) => {
                AutoCreationLogger::log_auto_creation_error(
                    &error,
                    "Auto-creation process",
                    PluginType::MySQL,
                    Some(instance.get_database().as_str()),
                )
                .await;
                if !error.should_continue() {
                    return Err(error.to_string());
                }
            }
        }
        let db_url: String = instance.get_connection_url();
        let timeout_duration: Duration = DatabasePlugin::get_connection_timeout_duration();
        let timeout_seconds: u64 = timeout_duration.as_secs();
        let connection_result: Result<DatabaseConnection, DbErr> =
            match timeout(timeout_duration, Database::connect(&db_url)).await {
                Ok(result) => result,
                Err(_) => Err(DbErr::Custom(format!(
                    "MySQL connection timeout after {timeout_seconds} seconds"
                ))),
            };
        connection_result.map_err(|error: DbErr| {
            let error_msg: String = error.to_string();
            let database_name: String = instance.get_database().clone();
            let error_msg_clone: String = error_msg.clone();
            spawn(async move {
                AutoCreationLogger::log_connection_verification(
                    PluginType::MySQL,
                    &database_name,
                    false,
                    Some(&error_msg_clone),
                )
                .await;
            });
            error_msg
        })
    }
    #[instrument_trace]
    async fn get_connection<I>(
        instance_name: I,
        schema: Option<DatabaseSchema>,
    ) -> Result<Self::Connection, String>
    where
        I: AsRef<str> + Send,
    {
        let instance_name_str: &str = instance_name.as_ref();
        let duration: Duration = DatabasePlugin::get_retry_duration();
        {
            if let Some(cache) = Self::get_or_init().read().await.get(instance_name_str) {
                match cache.try_get_result() {
                    Ok(conn) => return Ok(conn.clone()),
                    Err(error) => {
                        if !cache.is_expired(duration) {
                            return Err(error.clone());
                        }
                    }
                }
            }
        }
        let mut connections: RwLockWriteGuard<
            '_,
            HashMap<String, ConnectionCache<DatabaseConnection>>,
        > = Self::get_or_init().write().await;
        if let Some(cache) = connections.get(instance_name_str) {
            match cache.try_get_result() {
                Ok(conn) => return Ok(conn.clone()),
                Err(error) => {
                    if !cache.is_expired(duration) {
                        return Err(error.clone());
                    }
                }
            }
        }
        connections.remove(instance_name_str);
        drop(connections);
        let new_connection: Result<DatabaseConnection, String> =
            Self::connection_db(instance_name_str, schema).await;
        let mut connections: RwLockWriteGuard<
            '_,
            HashMap<String, ConnectionCache<DatabaseConnection>>,
        > = Self::get_or_init().write().await;
        connections.insert(
            instance_name_str.to_string(),
            ConnectionCache::new(new_connection.clone()),
        );
        new_connection
    }
    #[instrument_trace]
    async fn perform_auto_creation(
        instance: &Self::InstanceConfig,
        schema: Option<DatabaseSchema>,
    ) -> Result<AutoCreationResult, AutoCreationError> {
        let start_time: Instant = Instant::now();
        let mut result: AutoCreationResult = AutoCreationResult::default();
        AutoCreationLogger::log_auto_creation_start(PluginType::MySQL, instance.get_database())
            .await;
        let auto_creator: MySqlAutoCreation = match schema {
            Some(s) => MySqlAutoCreation::with_schema(instance.clone(), s),
            None => MySqlAutoCreation::new(instance.clone()),
        };
        match auto_creator.create_database_if_not_exists().await {
            Ok(created) => {
                result.set_database_created(created);
            }
            Err(error) => {
                AutoCreationLogger::log_auto_creation_error(
                    &error,
                    "Database creation",
                    PluginType::MySQL,
                    Some(instance.get_database()),
                )
                .await;
                if !error.should_continue() {
                    result.set_duration(start_time.elapsed());
                    return Err(error);
                }
                result.get_mut_errors().push(error.to_string());
            }
        }
        match auto_creator.create_tables_if_not_exist().await {
            Ok(tables) => {
                result.set_tables_created(tables);
            }
            Err(error) => {
                AutoCreationLogger::log_auto_creation_error(
                    &error,
                    "Table creation",
                    PluginType::MySQL,
                    Some(instance.get_database().as_str()),
                )
                .await;
                result.get_mut_errors().push(error.to_string());
            }
        }
        if let Err(error) = auto_creator.create_indexes().await {
            AutoCreationLogger::log_auto_creation_error(
                &error,
                "Index creation",
                PluginType::MySQL,
                Some(instance.get_database().as_str()),
            )
            .await;
            result.get_mut_errors().push(error.to_string());
        }
        if let Err(error) = auto_creator.init_data().await {
            AutoCreationLogger::log_auto_creation_error(
                &error,
                "Init data",
                PluginType::MySQL,
                Some(instance.get_database().as_str()),
            )
            .await;
            result.get_mut_errors().push(error.to_string());
        }
        if let Err(error) = auto_creator.verify_connection().await {
            AutoCreationLogger::log_auto_creation_error(
                &error,
                "Connection verification",
                PluginType::MySQL,
                Some(instance.get_database().as_str()),
            )
            .await;
            if !error.should_continue() {
                result.set_duration(start_time.elapsed());
                return Err(error);
            }
            result.get_mut_errors().push(error.to_string());
        }
        result.set_duration(start_time.elapsed());
        AutoCreationLogger::log_auto_creation_complete(PluginType::MySQL, &result).await;
        Ok(result)
    }
}
impl Default for MySqlAutoCreation {
    #[instrument_trace]
    fn default() -> Self {
        let env: &'static EnvConfig = EnvPlugin::get_or_init();
        if let Some(instance) = env.get_default_mysql_instance() {
            Self::new(instance.clone())
        } else {
            let default_instance: MySqlInstanceConfig = MySqlInstanceConfig::default();
            Self::new(default_instance)
        }
    }
}
impl MySqlAutoCreation {
    #[instrument_trace]
    async fn create_admin_connection(&self) -> Result<DatabaseConnection, AutoCreationError> {
        let admin_url: String = self.instance.get_admin_url();
        let timeout_duration: Duration = DatabasePlugin::get_connection_timeout_duration();
        let timeout_seconds: u64 = timeout_duration.as_secs();
        let connection_result: Result<DatabaseConnection, DbErr> =
            match timeout(timeout_duration, Database::connect(&admin_url)).await {
                Ok(result) => result,
                Err(_) => {
                    return Err(AutoCreationError::Timeout(format!(
                        "MySQL admin connection timeout after {timeout_seconds} seconds"
                    )));
                }
            };
        connection_result.map_err(|error: DbErr| {
            let error_msg: String = error.to_string();
            if error_msg.contains("Access denied") || error_msg.contains("permission") {
                AutoCreationError::InsufficientPermissions(format!(
                    "Cannot connect to MySQL server for database creation {error_msg}"
                ))
            } else if error_msg.contains("timeout") || error_msg.contains("Connection refused") {
                AutoCreationError::ConnectionFailed(format!(
                    "Cannot connect to MySQL server {error_msg}"
                ))
            } else {
                AutoCreationError::DatabaseError(format!("MySQL connection error {error_msg}"))
            }
        })
    }
    #[instrument_trace]
    async fn database_exists(
        &self,
        connection: &DatabaseConnection,
    ) -> Result<bool, AutoCreationError> {
        let query: String = format!(
            "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{}'",
            self.instance.get_database()
        );
        let statement: Statement = Statement::from_string(DatabaseBackend::MySql, query);
        match connection.query_all(statement).await {
            Ok(results) => Ok(!results.is_empty()),
            Err(error) => Err(AutoCreationError::DatabaseError(format!(
                "Failed to check if database exists {error}"
            ))),
        }
    }
    #[instrument_trace]
    async fn create_database(
        &self,
        connection: &DatabaseConnection,
    ) -> Result<bool, AutoCreationError> {
        if self.database_exists(connection).await? {
            AutoCreationLogger::log_database_exists(
                self.instance.get_database().as_str(),
                PluginType::MySQL,
            )
            .await;
            return Ok(false);
        }
        let create_query: String = format!(
            "CREATE DATABASE IF NOT EXISTS `{}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci",
            self.instance.get_database()
        );
        let statement: Statement = Statement::from_string(DatabaseBackend::MySql, create_query);
        match connection.execute(statement).await {
            Ok(_) => {
                AutoCreationLogger::log_database_created(
                    self.instance.get_database().as_str(),
                    PluginType::MySQL,
                )
                .await;
                Ok(true)
            }
            Err(error) => {
                let error_msg: String = error.to_string();
                if error_msg.contains("Access denied") || error_msg.contains("permission") {
                    Err(AutoCreationError::InsufficientPermissions(format!(
                        "Cannot create MySQL database '{}' {}",
                        self.instance.get_database().as_str(),
                        error_msg
                    )))
                } else {
                    Err(AutoCreationError::DatabaseError(format!(
                        "Failed to create MySQL database '{}' {}",
                        self.instance.get_database().as_str(),
                        error_msg
                    )))
                }
            }
        }
    }
    #[instrument_trace]
    async fn create_target_connection(&self) -> Result<DatabaseConnection, AutoCreationError> {
        let db_url: String = self.instance.get_connection_url();
        let timeout_duration: Duration = DatabasePlugin::get_connection_timeout_duration();
        let timeout_seconds: u64 = timeout_duration.as_secs();
        let connection_result: Result<DatabaseConnection, DbErr> =
            match timeout(timeout_duration, Database::connect(&db_url)).await {
                Ok(result) => result,
                Err(_) => {
                    return Err(AutoCreationError::Timeout(format!(
                        "MySQL database connection timeout after {timeout_seconds} seconds {}",
                        self.instance.get_database()
                    )));
                }
            };
        connection_result.map_err(|error: DbErr| {
            AutoCreationError::ConnectionFailed(format!(
                "Cannot connect to MySQL database '{}' {}",
                self.instance.get_database().as_str(),
                error
            ))
        })
    }
    #[instrument_trace]
    async fn table_exists<T>(
        &self,
        connection: &DatabaseConnection,
        table_name: T,
    ) -> Result<bool, AutoCreationError>
    where
        T: AsRef<str>,
    {
        let table_name_str: &str = table_name.as_ref();
        let query: String = format!(
            "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '{}' AND TABLE_NAME = '{table_name_str}'",
            self.instance.get_database()
        );
        let statement: Statement = Statement::from_string(DatabaseBackend::MySql, query);
        match connection.query_all(statement).await {
            Ok(results) => Ok(!results.is_empty()),
            Err(error) => Err(AutoCreationError::DatabaseError(format!(
                "Failed to check if table '{table_name_str}' exists {error}"
            ))),
        }
    }
    #[instrument_trace]
    async fn create_table(
        &self,
        connection: &DatabaseConnection,
        table: &TableSchema,
    ) -> Result<(), AutoCreationError> {
        let statement: Statement =
            Statement::from_string(DatabaseBackend::MySql, table.get_sql().clone());
        match connection.execute(statement).await {
            Ok(_) => Ok(()),
            Err(error) => {
                let error_msg: String = error.to_string();
                if error_msg.contains("Access denied") || error_msg.contains("permission") {
                    Err(AutoCreationError::InsufficientPermissions(format!(
                        "Cannot create MySQL table '{}' {}",
                        table.get_name(),
                        error_msg
                    )))
                } else {
                    Err(AutoCreationError::SchemaError(format!(
                        "Failed to create MySQL table '{}' {}",
                        table.get_name(),
                        error_msg
                    )))
                }
            }
        }
    }
    #[instrument_trace]
    async fn execute_sql<S>(
        &self,
        connection: &DatabaseConnection,
        sql: S,
    ) -> Result<(), AutoCreationError>
    where
        S: AsRef<str>,
    {
        let statement: Statement = Statement::from_string(DatabaseBackend::MySql, sql.as_ref());
        match connection.execute(statement).await {
            Ok(_) => Ok(()),
            Err(error) => Err(AutoCreationError::DatabaseError(format!(
                "Failed to execute SQL {error}"
            ))),
        }
    }
    #[instrument_trace]
    fn get_database_schema(&self) -> &DatabaseSchema {
        &self.schema
    }
    #[instrument_trace]
    async fn create_indexes(&self) -> Result<(), AutoCreationError> {
        let connection: DatabaseConnection = self.create_target_connection().await?;
        let schema: &DatabaseSchema = self.get_database_schema();
        for index_sql in schema.get_indexes() {
            if let Err(error) = self.execute_sql(&connection, index_sql).await {
                AutoCreationLogger::log_auto_creation_error(
                    &error,
                    "Index creation",
                    PluginType::MySQL,
                    Some(self.instance.get_database().as_str()),
                )
                .await;
            }
        }
        for constraint_sql in schema.get_constraints() {
            if let Err(error) = self.execute_sql(&connection, constraint_sql).await {
                AutoCreationLogger::log_auto_creation_error(
                    &error,
                    "Constraint creation",
                    PluginType::MySQL,
                    Some(self.instance.get_database().as_str()),
                )
                .await;
            }
        }
        let _: Result<(), DbErr> = connection.close().await;
        Ok(())
    }
}
impl DatabaseAutoCreation for MySqlAutoCreation {
    type InstanceConfig = MySqlInstanceConfig;
    #[instrument_trace]
    fn new(instance: Self::InstanceConfig) -> Self {
        Self {
            instance,
            schema: DatabaseSchema::default(),
        }
    }
    #[instrument_trace]
    fn with_schema(instance: Self::InstanceConfig, schema: DatabaseSchema) -> Self
    where
        Self: Sized,
    {
        Self { instance, schema }
    }
    #[instrument_trace]
    async fn create_database_if_not_exists(&self) -> Result<bool, AutoCreationError> {
        let admin_connection: DatabaseConnection = self.create_admin_connection().await?;
        let result: Result<bool, AutoCreationError> = self.create_database(&admin_connection).await;
        let _: Result<(), DbErr> = admin_connection.close().await;
        result
    }
    #[instrument_trace]
    async fn create_tables_if_not_exist(&self) -> Result<Vec<String>, AutoCreationError> {
        let connection: DatabaseConnection = self.create_target_connection().await?;
        let schema: &DatabaseSchema = self.get_database_schema();
        let mut created_tables: Vec<String> = Vec::new();
        for table in schema.ordered_tables() {
            if !self.table_exists(&connection, table.get_name()).await? {
                self.create_table(&connection, table).await?;
                created_tables.push(table.get_name().clone());
                AutoCreationLogger::log_table_created(
                    table.get_name(),
                    self.instance.get_database().as_str(),
                    PluginType::MySQL,
                )
                .await;
            } else {
                AutoCreationLogger::log_table_exists(
                    table.get_name(),
                    self.instance.get_database().as_str(),
                    PluginType::MySQL,
                )
                .await;
            }
        }
        let _: Result<(), DbErr> = connection.close().await;
        AutoCreationLogger::log_tables_created(
            &created_tables,
            self.instance.get_database().as_str(),
            PluginType::MySQL,
        )
        .await;
        Ok(created_tables)
    }
    #[instrument_trace]
    async fn init_data(&self) -> Result<(), AutoCreationError> {
        let connection: DatabaseConnection = self.create_target_connection().await?;
        let schema: &DatabaseSchema = self.get_database_schema();
        for init_data_sql in schema.get_init_data() {
            if let Err(error) = self.execute_sql(&connection, init_data_sql).await {
                AutoCreationLogger::log_auto_creation_error(
                    &error,
                    "Init data insertion",
                    PluginType::MySQL,
                    Some(self.instance.get_database().as_str()),
                )
                .await;
            }
        }
        let _: Result<(), DbErr> = connection.close().await;
        Ok(())
    }
    #[instrument_trace]
    async fn verify_connection(&self) -> Result<(), AutoCreationError> {
        let db_url: String = self.instance.get_connection_url();
        let timeout_duration: Duration = DatabasePlugin::get_connection_timeout_duration();
        let timeout_seconds: u64 = timeout_duration.as_secs();
        let connection_result: Result<DatabaseConnection, DbErr> =
            match timeout(timeout_duration, Database::connect(&db_url)).await {
                Ok(result) => result,
                Err(_) => {
                    return Err(AutoCreationError::Timeout(format!(
                        "Failed to verify MySQL connection within {timeout_seconds} seconds"
                    )));
                }
            };
        let connection: DatabaseConnection = connection_result.map_err(|error: DbErr| {
            AutoCreationError::ConnectionFailed(format!(
                "Failed to verify MySQL connection {error}"
            ))
        })?;
        let statement: Statement =
            Statement::from_string(DatabaseBackend::MySql, "SELECT 1".to_string());
        match connection.query_all(statement).await {
            Ok(_) => {
                let _: Result<(), DbErr> = connection.close().await;
                AutoCreationLogger::log_connection_verification(
                    PluginType::MySQL,
                    self.instance.get_database().as_str(),
                    true,
                    None,
                )
                .await;
                Ok(())
            }
            Err(error) => {
                let _: Result<(), DbErr> = connection.close().await;
                let error_msg: String = error.to_string();
                AutoCreationLogger::log_connection_verification(
                    PluginType::MySQL,
                    self.instance.get_database().as_str(),
                    false,
                    Some(&error_msg),
                )
                .await;
                Err(AutoCreationError::ConnectionFailed(format!(
                    "MySQL connection verification failed {error_msg}"
                )))
            }
        }
    }
}
```
# Path: hyperlane-quick-start/plugin/mysql/struct.rs
```rust
use super::*;
#[derive(Clone, Copy, Data, Debug, Default)]
pub struct MySqlPlugin;
#[derive(Clone, Data, Debug, New)]
pub struct MySqlAutoCreation {
    pub(super) instance: MySqlInstanceConfig,
    #[new(skip)]
    pub(super) schema: DatabaseSchema,
}
```
# Path: hyperlane-quick-start/plugin/mysql/static.rs
```rust
use super::*;
pub static MYSQL_CONNECTIONS: OnceLock<
    RwLock<HashMap<String, ConnectionCache<DatabaseConnection>>>,
> = OnceLock::new();
```
# Path: hyperlane-quick-start/plugin/postgresql/const.rs
```rust
pub const DEFAULT_POSTGRESQL_INSTANCE_NAME: &str = "postgres_default";
```
# Path: hyperlane-quick-start/plugin/postgresql/mod.rs
```rust
mod r#const;
mod r#impl;
mod r#static;
mod r#struct;
pub use {r#const::*, r#struct::*};
use {super::*, database::*, env::*, r#static::*};
use {
    sea_orm::{ConnectionTrait, Database, DatabaseBackend, DatabaseConnection, DbErr, Statement},
    tokio::{
        spawn,
        sync::{RwLock, RwLockWriteGuard},
        time::timeout,
    },
};
```
# Path: hyperlane-quick-start/plugin/postgresql/impl.rs
```rust
use super::*;
impl GetOrInit for PostgreSqlPlugin {
    type Instance = RwLock<HashMap<String, ConnectionCache<DatabaseConnection>>>;
    #[instrument_trace]
    fn get_or_init() -> &'static Self::Instance {
        POSTGRESQL_CONNECTIONS.get_or_init(|| RwLock::new(HashMap::new()))
    }
}
impl DatabaseConnectionPlugin for PostgreSqlPlugin {
    type InstanceConfig = PostgreSqlInstanceConfig;
    type AutoCreation = PostgreSqlAutoCreation;
    type Connection = DatabaseConnection;
    type ConnectionCache = RwLock<HashMap<String, ConnectionCache<Self::Connection>>>;
    #[instrument_trace]
    fn plugin_type() -> PluginType {
        PluginType::PostgreSQL
    }
    #[instrument_trace]
    async fn connection_db<I>(
        instance_name: I,
        schema: Option<DatabaseSchema>,
    ) -> Result<Self::Connection, String>
    where
        I: AsRef<str> + Send,
    {
        let instance_name_str: &str = instance_name.as_ref();
        let env: &'static EnvConfig = EnvPlugin::get_or_init();
        let instance: &PostgreSqlInstanceConfig = env
            .get_postgresql_instance(instance_name_str)
            .ok_or_else(|| format!("PostgreSQL instance '{instance_name_str}' not found"))?;
        match Self::perform_auto_creation(instance, schema.clone()).await {
            Ok(result) => {
                if result.has_changes() {
                    AutoCreationLogger::log_auto_creation_complete(PluginType::PostgreSQL, &result)
                        .await;
                }
            }
            Err(error) => {
                AutoCreationLogger::log_auto_creation_error(
                    &error,
                    "Auto-creation process",
                    PluginType::PostgreSQL,
                    Some(instance.get_database().as_str()),
                )
                .await;
                if !error.should_continue() {
                    return Err(error.to_string());
                }
            }
        }
        let db_url: String = instance.get_connection_url();
        let timeout_duration: Duration = DatabasePlugin::get_connection_timeout_duration();
        let timeout_seconds: u64 = timeout_duration.as_secs();
        let connection_result: Result<DatabaseConnection, DbErr> =
            match timeout(timeout_duration, Database::connect(&db_url)).await {
                Ok(result) => result,
                Err(_) => Err(DbErr::Custom(format!(
                    "PostgreSQL connection timeout after {timeout_seconds} seconds"
                ))),
            };
        connection_result.map_err(|error: DbErr| {
            let error_msg: String = error.to_string();
            let database_name: String = instance.get_database().clone();
            let error_msg_clone: String = error_msg.clone();
            spawn(async move {
                AutoCreationLogger::log_connection_verification(
                    PluginType::PostgreSQL,
                    &database_name,
                    false,
                    Some(&error_msg_clone),
                )
                .await;
            });
            error_msg
        })
    }
    #[instrument_trace]
    async fn get_connection<I>(
        instance_name: I,
        schema: Option<DatabaseSchema>,
    ) -> Result<Self::Connection, String>
    where
        I: AsRef<str> + Send,
    {
        let instance_name_str: &str = instance_name.as_ref();
        let duration: Duration = DatabasePlugin::get_retry_duration();
        {
            if let Some(cache) = Self::get_or_init().read().await.get(instance_name_str) {
                match cache.try_get_result() {
                    Ok(conn) => return Ok(conn.clone()),
                    Err(error) => {
                        if !cache.is_expired(duration) {
                            return Err(error.clone());
                        }
                    }
                }
            }
        }
        let mut connections: RwLockWriteGuard<
            '_,
            HashMap<String, ConnectionCache<DatabaseConnection>>,
        > = Self::get_or_init().write().await;
        if let Some(cache) = connections.get(instance_name_str) {
            match cache.try_get_result() {
                Ok(conn) => return Ok(conn.clone()),
                Err(error) => {
                    if !cache.is_expired(duration) {
                        return Err(error.clone());
                    }
                }
            }
        }
        connections.remove(instance_name_str);
        drop(connections);
        let new_connection: Result<DatabaseConnection, String> =
            Self::connection_db(instance_name_str, schema).await;
        let mut connections: RwLockWriteGuard<
            '_,
            HashMap<String, ConnectionCache<DatabaseConnection>>,
        > = Self::get_or_init().write().await;
        connections.insert(
            instance_name_str.to_string(),
            ConnectionCache::new(new_connection.clone()),
        );
        new_connection
    }
    #[instrument_trace]
    async fn perform_auto_creation(
        instance: &Self::InstanceConfig,
        schema: Option<DatabaseSchema>,
    ) -> Result<AutoCreationResult, AutoCreationError> {
        let start_time: Instant = Instant::now();
        let mut result: AutoCreationResult = AutoCreationResult::default();
        AutoCreationLogger::log_auto_creation_start(
            PluginType::PostgreSQL,
            instance.get_database(),
        )
        .await;
        let auto_creator: PostgreSqlAutoCreation = match schema {
            Some(s) => PostgreSqlAutoCreation::with_schema(instance.clone(), s),
            None => PostgreSqlAutoCreation::new(instance.clone()),
        };
        match auto_creator.create_database_if_not_exists().await {
            Ok(created) => {
                result.set_database_created(created);
            }
            Err(error) => {
                AutoCreationLogger::log_auto_creation_error(
                    &error,
                    "Database creation",
                    PluginType::PostgreSQL,
                    Some(instance.get_database().as_str()),
                )
                .await;
                if !error.should_continue() {
                    result.set_duration(start_time.elapsed());
                    return Err(error);
                }
                result.get_mut_errors().push(error.to_string());
            }
        }
        match auto_creator.create_tables_if_not_exist().await {
            Ok(tables) => {
                result.set_tables_created(tables);
            }
            Err(error) => {
                AutoCreationLogger::log_auto_creation_error(
                    &error,
                    "Table creation",
                    PluginType::PostgreSQL,
                    Some(instance.get_database().as_str()),
                )
                .await;
                result.get_mut_errors().push(error.to_string());
            }
        }
        if let Err(error) = auto_creator.create_indexes().await {
            AutoCreationLogger::log_auto_creation_error(
                &error,
                "Index creation",
                PluginType::PostgreSQL,
                Some(instance.get_database().as_str()),
            )
            .await;
            result.get_mut_errors().push(error.to_string());
        }
        if let Err(error) = auto_creator.init_data().await {
            AutoCreationLogger::log_auto_creation_error(
                &error,
                "Init data",
                PluginType::PostgreSQL,
                Some(instance.get_database().as_str()),
            )
            .await;
            result.get_mut_errors().push(error.to_string());
        }
        if let Err(error) = auto_creator.verify_connection().await {
            AutoCreationLogger::log_auto_creation_error(
                &error,
                "Connection verification",
                PluginType::PostgreSQL,
                Some(instance.get_database().as_str()),
            )
            .await;
            if !error.should_continue() {
                result.set_duration(start_time.elapsed());
                return Err(error);
            }
            result.get_mut_errors().push(error.to_string());
        }
        result.set_duration(start_time.elapsed());
        AutoCreationLogger::log_auto_creation_complete(PluginType::PostgreSQL, &result).await;
        Ok(result)
    }
}
impl Default for PostgreSqlAutoCreation {
    #[instrument_trace]
    fn default() -> Self {
        let env: &'static EnvConfig = EnvPlugin::get_or_init();
        if let Some(instance) = env.get_default_postgresql_instance() {
            Self::new(instance.clone())
        } else {
            let default_instance: PostgreSqlInstanceConfig = PostgreSqlInstanceConfig::default();
            Self::new(default_instance)
        }
    }
}
impl PostgreSqlAutoCreation {
    #[instrument_trace]
    async fn create_admin_connection(&self) -> Result<DatabaseConnection, AutoCreationError> {
        let admin_url: String = self.instance.get_admin_url();
        let timeout_duration: Duration = DatabasePlugin::get_connection_timeout_duration();
        let timeout_seconds: u64 = timeout_duration.as_secs();
        let connection_result: Result<DatabaseConnection, DbErr> =
            match timeout(timeout_duration, Database::connect(&admin_url)).await {
                Ok(result) => result,
                Err(_) => {
                    return Err(AutoCreationError::Timeout(format!(
                        "PostgreSQL admin connection timeout after {timeout_seconds} seconds"
                    )));
                }
            };
        connection_result.map_err(|error: DbErr| {
            let error_msg: String = error.to_string();
            if error_msg.contains("authentication failed") || error_msg.contains("permission") {
                AutoCreationError::InsufficientPermissions(format!(
                    "Cannot connect to PostgreSQL server for database creation {error_msg}"
                ))
            } else if error_msg.contains("timeout") || error_msg.contains("Connection refused") {
                AutoCreationError::ConnectionFailed(format!(
                    "Cannot connect to PostgreSQL server {error_msg}"
                ))
            } else {
                AutoCreationError::DatabaseError(format!("PostgreSQL connection error {error_msg}"))
            }
        })
    }
    #[instrument_trace]
    async fn create_target_connection(&self) -> Result<DatabaseConnection, AutoCreationError> {
        let db_url: String = self.instance.get_connection_url();
        let timeout_duration: Duration = DatabasePlugin::get_connection_timeout_duration();
        let timeout_seconds: u64 = timeout_duration.as_secs();
        let connection_result: Result<DatabaseConnection, DbErr> =
            match timeout(timeout_duration, Database::connect(&db_url)).await {
                Ok(result) => result,
                Err(_) => {
                    return Err(AutoCreationError::Timeout(format!(
                        "PostgreSQL database connection timeout after {timeout_seconds} seconds {}",
                        self.instance.get_database().as_str()
                    )));
                }
            };
        connection_result.map_err(|error: DbErr| {
            AutoCreationError::ConnectionFailed(format!(
                "Cannot connect to PostgreSQL database '{}' {error}",
                self.instance.get_database().as_str(),
            ))
        })
    }
    #[instrument_trace]
    async fn database_exists(
        &self,
        connection: &DatabaseConnection,
    ) -> Result<bool, AutoCreationError> {
        let query: String = format!(
            "SELECT 1 FROM pg_database WHERE datname = '{}'",
            self.instance.get_database().as_str()
        );
        let statement: Statement = Statement::from_string(DatabaseBackend::Postgres, query);
        match connection.query_all(statement).await {
            Ok(results) => Ok(!results.is_empty()),
            Err(error) => Err(AutoCreationError::DatabaseError(format!(
                "Failed to check if database exists {error}"
            ))),
        }
    }
    #[instrument_trace]
    async fn create_database(
        &self,
        connection: &DatabaseConnection,
    ) -> Result<bool, AutoCreationError> {
        if self.database_exists(connection).await? {
            AutoCreationLogger::log_database_exists(
                self.instance.get_database().as_str(),
                PluginType::PostgreSQL,
            )
            .await;
            return Ok(false);
        }
        let create_query: String = format!(
            "CREATE DATABASE \"{}\" WITH ENCODING='UTF8' LC_COLLATE='en_US.UTF-8' LC_CTYPE='en_US.UTF-8'",
            self.instance.get_database().as_str()
        );
        let statement: Statement = Statement::from_string(DatabaseBackend::Postgres, create_query);
        match connection.execute(statement).await {
            Ok(_) => {
                AutoCreationLogger::log_database_created(
                    self.instance.get_database().as_str(),
                    PluginType::PostgreSQL,
                )
                .await;
                Ok(true)
            }
            Err(error) => {
                let error_msg: String = error.to_string();
                if error_msg.contains("permission denied") || error_msg.contains("must be owner") {
                    Err(AutoCreationError::InsufficientPermissions(format!(
                        "Cannot create PostgreSQL database '{}' {}",
                        self.instance.get_database().as_str(),
                        error_msg
                    )))
                } else if error_msg.contains("already exists") {
                    AutoCreationLogger::log_database_exists(
                        self.instance.get_database().as_str(),
                        PluginType::PostgreSQL,
                    )
                    .await;
                    Ok(false)
                } else {
                    Err(AutoCreationError::DatabaseError(format!(
                        "Failed to create PostgreSQL database '{}' {}",
                        self.instance.get_database().as_str(),
                        error_msg
                    )))
                }
            }
        }
    }
    #[instrument_trace]
    async fn table_exists<T>(
        &self,
        connection: &DatabaseConnection,
        table_name: T,
    ) -> Result<bool, AutoCreationError>
    where
        T: AsRef<str>,
    {
        let table_name_str: &str = table_name.as_ref();
        let query: String = format!(
            "SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '{table_name_str}'"
        );
        let statement: Statement = Statement::from_string(DatabaseBackend::Postgres, query);
        match connection.query_all(statement).await {
            Ok(results) => Ok(!results.is_empty()),
            Err(error) => Err(AutoCreationError::DatabaseError(format!(
                "Failed to check if table '{table_name_str}' exists {error}"
            ))),
        }
    }
    #[instrument_trace]
    async fn create_table(
        &self,
        connection: &DatabaseConnection,
        table: &TableSchema,
    ) -> Result<(), AutoCreationError> {
        let statement: Statement =
            Statement::from_string(DatabaseBackend::Postgres, table.get_sql().clone());
        match connection.execute(statement).await {
            Ok(_) => Ok(()),
            Err(error) => {
                let error_msg: String = error.to_string();
                if error_msg.contains("permission denied") {
                    Err(AutoCreationError::InsufficientPermissions(format!(
                        "Cannot create PostgreSQL table '{}' {}",
                        table.get_name(),
                        error_msg
                    )))
                } else {
                    Err(AutoCreationError::SchemaError(format!(
                        "Failed to create PostgreSQL table '{}' {}",
                        table.get_name(),
                        error_msg
                    )))
                }
            }
        }
    }
    #[instrument_trace]
    async fn execute_sql<S>(
        &self,
        connection: &DatabaseConnection,
        sql: S,
    ) -> Result<(), AutoCreationError>
    where
        S: AsRef<str>,
    {
        let statement: Statement = Statement::from_string(DatabaseBackend::Postgres, sql.as_ref());
        match connection.execute(statement).await {
            Ok(_) => Ok(()),
            Err(error) => Err(AutoCreationError::DatabaseError(format!(
                "Failed to execute SQL {error}"
            ))),
        }
    }
    #[instrument_trace]
    fn get_database_schema(&self) -> &DatabaseSchema {
        &self.schema
    }
    #[instrument_trace]
    async fn create_indexes(&self) -> Result<(), AutoCreationError> {
        let connection: DatabaseConnection = self.create_target_connection().await?;
        let schema: &DatabaseSchema = self.get_database_schema();
        for index_sql in schema.get_indexes() {
            if let Err(error) = self.execute_sql(&connection, index_sql).await {
                AutoCreationLogger::log_auto_creation_error(
                    &error,
                    "Index creation",
                    PluginType::PostgreSQL,
                    Some(self.instance.get_database().as_str()),
                )
                .await;
            }
        }
        for constraint_sql in schema.get_constraints() {
            if let Err(error) = self.execute_sql(&connection, constraint_sql).await {
                AutoCreationLogger::log_auto_creation_error(
                    &error,
                    "Constraint creation",
                    PluginType::PostgreSQL,
                    Some(self.instance.get_database().as_str()),
                )
                .await;
            }
        }
        let _: Result<(), DbErr> = connection.close().await;
        Ok(())
    }
}
impl DatabaseAutoCreation for PostgreSqlAutoCreation {
    type InstanceConfig = PostgreSqlInstanceConfig;
    #[instrument_trace]
    fn new(instance: Self::InstanceConfig) -> Self {
        Self {
            instance,
            schema: DatabaseSchema::default(),
        }
    }
    #[instrument_trace]
    fn with_schema(instance: Self::InstanceConfig, schema: DatabaseSchema) -> Self
    where
        Self: Sized,
    {
        Self { instance, schema }
    }
    #[instrument_trace]
    async fn create_database_if_not_exists(&self) -> Result<bool, AutoCreationError> {
        let admin_connection: DatabaseConnection = self.create_admin_connection().await?;
        let result: Result<bool, AutoCreationError> = self.create_database(&admin_connection).await;
        let _: Result<(), DbErr> = admin_connection.close().await;
        result
    }
    #[instrument_trace]
    async fn create_tables_if_not_exist(&self) -> Result<Vec<String>, AutoCreationError> {
        let connection: DatabaseConnection = self.create_target_connection().await?;
        let schema: &DatabaseSchema = self.get_database_schema();
        let mut created_tables: Vec<String> = Vec::new();
        for table in schema.ordered_tables() {
            if !self.table_exists(&connection, table.get_name()).await? {
                self.create_table(&connection, table).await?;
                created_tables.push(table.get_name().clone());
                AutoCreationLogger::log_table_created(
                    table.get_name(),
                    self.instance.get_database().as_str(),
                    PluginType::PostgreSQL,
                )
                .await;
            } else {
                AutoCreationLogger::log_table_exists(
                    table.get_name(),
                    self.instance.get_database().as_str(),
                    PluginType::PostgreSQL,
                )
                .await;
            }
        }
        let _: Result<(), DbErr> = connection.close().await;
        AutoCreationLogger::log_tables_created(
            &created_tables,
            self.instance.get_database().as_str(),
            PluginType::PostgreSQL,
        )
        .await;
        Ok(created_tables)
    }
    #[instrument_trace]
    async fn init_data(&self) -> Result<(), AutoCreationError> {
        let connection: DatabaseConnection = self.create_target_connection().await?;
        let schema: &DatabaseSchema = self.get_database_schema();
        for init_data_sql in schema.get_init_data() {
            if let Err(error) = self.execute_sql(&connection, init_data_sql).await {
                AutoCreationLogger::log_auto_creation_error(
                    &error,
                    "Init data insertion",
                    PluginType::PostgreSQL,
                    Some(self.instance.get_database().as_str()),
                )
                .await;
            }
        }
        let _: Result<(), DbErr> = connection.close().await;
        Ok(())
    }
    #[instrument_trace]
    async fn verify_connection(&self) -> Result<(), AutoCreationError> {
        let connection: DatabaseConnection = self.create_target_connection().await?;
        let statement: Statement =
            Statement::from_string(DatabaseBackend::Postgres, "SELECT 1".to_string());
        match connection.query_all(statement).await {
            Ok(_) => {
                let _: Result<(), DbErr> = connection.close().await;
                AutoCreationLogger::log_connection_verification(
                    PluginType::PostgreSQL,
                    self.instance.get_database().as_str(),
                    true,
                    None,
                )
                .await;
                Ok(())
            }
            Err(error) => {
                let _: Result<(), DbErr> = connection.close().await;
                let error_msg: String = error.to_string();
                AutoCreationLogger::log_connection_verification(
                    PluginType::PostgreSQL,
                    self.instance.get_database().as_str(),
                    false,
                    Some(&error_msg),
                )
                .await;
                Err(AutoCreationError::ConnectionFailed(format!(
                    "PostgreSQL connection verification failed {error_msg}"
                )))
            }
        }
    }
}
```
# Path: hyperlane-quick-start/plugin/postgresql/struct.rs
```rust
use super::*;
#[derive(Clone, Copy, Data, Debug, Default)]
pub struct PostgreSqlPlugin;
#[derive(Clone, Data, Debug, New)]
pub struct PostgreSqlAutoCreation {
    pub(super) instance: PostgreSqlInstanceConfig,
    #[new(skip)]
    pub(super) schema: DatabaseSchema,
}
```
# Path: hyperlane-quick-start/plugin/postgresql/static.rs
```rust
use super::*;
pub static POSTGRESQL_CONNECTIONS: OnceLock<
    RwLock<HashMap<String, ConnectionCache<DatabaseConnection>>>,
> = OnceLock::new();
```
# Path: hyperlane-quick-start/plugin/process/const.rs
```rust
pub const CMD_STOP: &str = "stop";
pub const CMD_RESTART: &str = "restart";
pub const DAEMON_FLAG: &str = "-d";
```
# Path: hyperlane-quick-start/plugin/process/mod.rs
```rust
mod r#const;
mod r#impl;
mod r#struct;
pub use r#struct::*;
use {super::*, r#const::*};
use std::{env::args, future::Future};
```
# Path: hyperlane-quick-start/plugin/process/impl.rs
```rust
use super::*;
impl ProcessPlugin {
    #[instrument_trace]
    pub async fn create<P, F, Fut>(pid_path: P, server_hook: F)
    where
        P: AsRef<str>,
        F: Fn() -> Fut + Send + Sync + 'static,
        Fut: Future<Output = ()> + Send + 'static,
    {
        let args: Vec<String> = args().collect();
        debug!("Process create args {args:?}");
        trace!("Pid file path: {}", pid_path.as_ref());
        let mut manager: ServerManager = ServerManager::new();
        manager
            .set_pid_file(pid_path.as_ref())
            .set_server_hook(server_hook);
        let is_daemon: bool = args.len() >= 3 && args[2].to_lowercase() == DAEMON_FLAG;
        let start_server = || async {
            if is_daemon {
                match manager.start_daemon().await {
                    Ok(_) => info!("Server started in background successfully"),
                    Err(error) => {
                        error!("Error starting server in background {error}")
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
                Err(error) => error!("Error stopping server {error}"),
            };
        };
        let restart_server = || async {
            stop_server().await;
            start_server().await;
        };
        if args.len() < 2 {
            warn!("No additional command-line parameters, default startup");
            start_server().await;
            return;
        }
        let command: String = args[1].to_lowercase();
        match command.as_str() {
            CMD_STOP => stop_server().await,
            CMD_RESTART => restart_server().await,
            _ => {
                error!("Invalid command {command}");
            }
        }
    }
}
```
# Path: hyperlane-quick-start/plugin/process/struct.rs
```rust
use super::*;
#[derive(Clone, Copy, Data, Debug, Default)]
pub struct ProcessPlugin;
```
# Path: hyperlane-quick-start/plugin/shutdown/mod.rs
```rust
mod r#impl;
mod r#static;
mod r#struct;
pub use r#struct::*;
use {super::*, r#static::*};
```
# Path: hyperlane-quick-start/plugin/shutdown/impl.rs
```rust
use super::*;
impl GetOrInit for ShutdownPlugin {
    type Instance = ServerControlHookHandler<()>;
    fn get_or_init() -> &'static Self::Instance {
        SHUTDOWN.get_or_init(Self::get_init)
    }
}
impl ShutdownPlugin {
    #[instrument_trace]
    pub fn get_init() -> ServerControlHookHandler<()> {
        Arc::new(|| {
            Box::pin(async {
                warn!("Not set shutdown, using default");
            })
        })
    }
    #[instrument_trace]
    pub fn set(shutdown: &ServerControlHookHandler<()>) {
        drop(SHUTDOWN.set(shutdown.clone()));
    }
}
```
# Path: hyperlane-quick-start/plugin/shutdown/struct.rs
```rust
use super::*;
#[derive(Clone, Copy, Data, Debug, Default)]
pub struct ShutdownPlugin;
```
# Path: hyperlane-quick-start/plugin/shutdown/static.rs
```rust
use super::*;
pub(super) static SHUTDOWN: OnceLock<ServerControlHookHandler<()>> = OnceLock::new();
```
# Path: hyperlane-quick-start/plugin/database/const.rs
```rust
pub const MYSQL_DISPLAY_NAME: &str = "MySQL";
pub const POSTGRESQL_DISPLAY_NAME: &str = "PostgreSQL";
pub const REDIS_DISPLAY_NAME: &str = "Redis";
```
# Path: hyperlane-quick-start/plugin/database/mod.rs
```rust
mod r#const;
mod r#enum;
mod r#impl;
mod r#struct;
pub use {r#const::*, r#enum::*, r#struct::*};
use {super::*, env::*, mysql::*, postgresql::*, redis::*};
use std::{
    env::var,
    fmt,
    str::FromStr,
    time::{Duration, Instant},
};
```
# Path: hyperlane-quick-start/plugin/database/impl.rs
```rust
use super::*;
impl fmt::Display for PluginType {
    #[instrument_trace]
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::MySQL => write!(f, "{}", MYSQL_DISPLAY_NAME),
            Self::PostgreSQL => write!(f, "{}", POSTGRESQL_DISPLAY_NAME),
            Self::Redis => write!(f, "{}", REDIS_DISPLAY_NAME),
        }
    }
}
impl FromStr for PluginType {
    type Err = ();
    #[instrument_trace]
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s {
            MYSQL_DISPLAY_NAME => Ok(Self::MySQL),
            POSTGRESQL_DISPLAY_NAME => Ok(Self::PostgreSQL),
            REDIS_DISPLAY_NAME => Ok(Self::Redis),
            _ => Err(()),
        }
    }
}
impl std::fmt::Display for AutoCreationError {
    #[instrument_trace]
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::InsufficientPermissions(msg) => {
                write!(f, "Insufficient permissions {msg}")
            }
            Self::ConnectionFailed(msg) => write!(f, "Connection failed {msg}"),
            Self::SchemaError(msg) => write!(f, "Schema error {msg}"),
            Self::Timeout(msg) => write!(f, "Timeout {msg}"),
            Self::DatabaseError(msg) => write!(f, "Database error {msg}"),
        }
    }
}
impl std::error::Error for AutoCreationError {}
impl AutoCreationError {
    #[instrument_trace]
    pub fn should_continue(&self) -> bool {
        match self {
            Self::InsufficientPermissions(_) => true,
            Self::ConnectionFailed(_) => false,
            Self::SchemaError(_) => true,
            Self::Timeout(_) => true,
            Self::DatabaseError(_) => true,
        }
    }
    #[instrument_trace]
    pub fn user_message(&self) -> &str {
        match self {
            Self::InsufficientPermissions(msg) => msg,
            Self::ConnectionFailed(msg) => msg,
            Self::SchemaError(msg) => msg,
            Self::Timeout(msg) => msg,
            Self::DatabaseError(msg) => msg,
        }
    }
}
impl TableSchema {
    #[instrument_trace]
    pub fn with_dependency(mut self, dependency: String) -> Self {
        self.get_mut_dependencies().push(dependency);
        self
    }
}
impl DatabasePlugin {
    #[instrument_trace]
    pub fn get_connection_timeout_duration() -> Duration {
        let timeout_millis: u64 = var(ENV_KEY_DB_CONNECTION_TIMEOUT_MILLIS)
            .ok()
            .and_then(|value: String| value.parse::<u64>().ok())
            .unwrap_or_else(|| {
                panic!(
                    "Environment variable {} is not set or invalid",
                    ENV_KEY_DB_CONNECTION_TIMEOUT_MILLIS
                )
            });
        Duration::from_millis(timeout_millis)
    }
    #[instrument_trace]
    pub fn get_retry_duration() -> Duration {
        let millis: u64 = var(ENV_KEY_DB_RETRY_INTERVAL_MILLIS)
            .ok()
            .and_then(|value: String| value.parse::<u64>().ok())
            .unwrap_or_else(|| {
                panic!(
                    "Environment variable {} is not set or invalid",
                    ENV_KEY_DB_RETRY_INTERVAL_MILLIS
                )
            });
        Duration::from_millis(millis)
    }
    #[instrument_trace]
    pub async fn initialize_auto_creation() -> Result<(), String> {
        Self::initialize_auto_creation_with_schema(None, None, None).await
    }
    #[instrument_trace]
    pub async fn initialize_auto_creation_with_schema(
        mysql_schema: Option<DatabaseSchema>,
        postgresql_schema: Option<DatabaseSchema>,
        _redis_schema: Option<()>,
    ) -> Result<(), String> {
        if let Err(error) = AutoCreationConfig::validate() {
            return Err(format!(
                "Auto-creation configuration validation failed {error}"
            ));
        }
        let env: &'static EnvConfig = EnvPlugin::get_or_init();
        let mut initialization_results: Vec<String> = Vec::new();
        for instance in env.get_mysql_instances() {
            match MySqlPlugin::perform_auto_creation(instance, mysql_schema.clone()).await {
                Ok(result) => {
                    initialization_results.push(format!(
                        "MySQL ({})  {}",
                        instance.get_name(),
                        if result.has_changes() {
                            "initialized with changes"
                        } else {
                            "verified"
                        }
                    ));
                }
                Err(error) => {
                    if !error.should_continue() {
                        return Err(format!(
                            "MySQL ({}) auto-creation failed {error}",
                            instance.get_name()
                        ));
                    }
                    initialization_results.push(format!(
                        "MySQL ({}) : failed but continuing ({error})",
                        instance.get_name()
                    ));
                }
            }
        }
        for instance in env.get_postgresql_instances() {
            match PostgreSqlPlugin::perform_auto_creation(instance, postgresql_schema.clone()).await
            {
                Ok(result) => {
                    initialization_results.push(format!(
                        "PostgreSQL ({})  {}",
                        instance.get_name(),
                        if result.has_changes() {
                            "initialized with changes"
                        } else {
                            "verified"
                        }
                    ));
                }
                Err(error) => {
                    if !error.should_continue() {
                        return Err(format!(
                            "PostgreSQL ({}) auto-creation failed {error}",
                            instance.get_name()
                        ));
                    }
                    initialization_results.push(format!(
                        "PostgreSQL ({}) : failed but continuing ({error})",
                        instance.get_name()
                    ));
                }
            }
        }
        for instance in env.get_redis_instances() {
            match RedisPlugin::perform_auto_creation(instance, None).await {
                Ok(result) => {
                    initialization_results.push(format!(
                        "Redis ({})  {}",
                        instance.get_name(),
                        if result.has_changes() {
                            "initialized with changes"
                        } else {
                            "verified"
                        }
                    ));
                }
                Err(error) => {
                    if !error.should_continue() {
                        return Err(format!(
                            "Redis ({}) auto-creation failed {error}",
                            instance.get_name()
                        ));
                    }
                    initialization_results.push(format!(
                        "Redis ({}) : failed but continuing ({error})",
                        instance.get_name()
                    ));
                }
            }
        }
        if initialization_results.is_empty() {
            info!("[AUTO-CREATION] No plugins enabled for auto-creation");
        } else {
            let results_summary: String = initialization_results.join(", ");
            info!("[AUTO-CREATION] Initialization complete {results_summary}");
        }
        Ok(())
    }
}
impl<T: Clone> ConnectionCache<T> {
    #[instrument_trace]
    pub fn new(result: Result<T, String>) -> Self {
        Self {
            result,
            last_attempt: Instant::now(),
        }
    }
    #[instrument_trace]
    pub fn is_expired(&self, duration: Duration) -> bool {
        self.get_last_attempt().elapsed() >= duration
    }
    #[instrument_trace]
    pub fn should_retry(&self, duration: Duration) -> bool {
        self.try_get_result().is_err() && self.is_expired(duration)
    }
}
impl AutoCreationResult {
    #[instrument_trace]
    pub fn has_changes(&self) -> bool {
        self.get_database_created() || !self.get_tables_created().is_empty()
    }
    #[instrument_trace]
    pub fn has_errors(&self) -> bool {
        !self.get_errors().is_empty()
    }
}
impl DatabaseSchema {
    #[instrument_trace]
    pub fn add_table(mut self, table: TableSchema) -> Self {
        self.get_mut_tables().push(table);
        self
    }
    #[instrument_trace]
    pub fn add_index(mut self, index: String) -> Self {
        self.get_mut_indexes().push(index);
        self
    }
    #[instrument_trace]
    pub fn add_constraint(mut self, constraint: String) -> Self {
        self.get_mut_constraints().push(constraint);
        self
    }
    #[instrument_trace]
    pub fn add_init_data(mut self, init_data: String) -> Self {
        self.get_mut_init_data().push(init_data);
        self
    }
    #[instrument_trace]
    pub fn ordered_tables(&self) -> Vec<&TableSchema> {
        let mut ordered: Vec<&TableSchema> = Vec::new();
        let mut remaining: Vec<&TableSchema> = self.get_tables().iter().collect();
        while !remaining.is_empty() {
            let mut added_any: bool = false;
            remaining.retain(|table: &&TableSchema| {
                let dependencies_satisfied: bool =
                    table.get_dependencies().iter().all(|dep: &String| {
                        ordered.iter().any(|ordered_table: &&TableSchema| {
                            ordered_table.get_name().as_str() == dep.as_str()
                        })
                    });
                if dependencies_satisfied {
                    ordered.push(table);
                    added_any = true;
                    false
                } else {
                    true
                }
            });
            if !added_any && !remaining.is_empty() {
                for table in remaining {
                    ordered.push(table);
                }
                break;
            }
        }
        ordered
    }
}
impl AutoCreationConfig {
    #[instrument_trace]
    pub fn validate() -> Result<(), String> {
        let env: &'static EnvConfig = EnvPlugin::get_or_init();
        if env.get_mysql_instances().is_empty() {
            return Err("At least one MySQL instance is required".to_string());
        }
        if env.get_postgresql_instances().is_empty() {
            return Err("At least one PostgreSQL instance is required".to_string());
        }
        if env.get_redis_instances().is_empty() {
            return Err("At least one Redis instance is required".to_string());
        }
        Ok(())
    }
    #[instrument_trace]
    pub fn for_plugin(plugin_name: &str) -> PluginAutoCreationConfig {
        PluginAutoCreationConfig {
            plugin_name: plugin_name.to_string(),
        }
    }
}
impl PluginAutoCreationConfig {
    #[instrument_trace]
    pub fn is_plugin_enabled(&self) -> bool {
        PluginType::from_str(self.get_plugin_name()).is_ok()
    }
    #[instrument_trace]
    pub fn get_database_name(&self) -> String {
        let env: &'static EnvConfig = EnvPlugin::get_or_init();
        if let Ok(plugin_type) = PluginType::from_str(self.get_plugin_name()) {
            match plugin_type {
                PluginType::MySQL => {
                    if let Some(instance) = env.get_default_mysql_instance() {
                        instance.get_database().clone()
                    } else {
                        "unknown".to_string()
                    }
                }
                PluginType::PostgreSQL => {
                    if let Some(instance) = env.get_default_postgresql_instance() {
                        instance.get_database().clone()
                    } else {
                        "unknown".to_string()
                    }
                }
                PluginType::Redis => "default".to_string(),
            }
        } else {
            "unknown".to_string()
        }
    }
    #[instrument_trace]
    pub fn get_connection_info(&self) -> String {
        let env: &'static EnvConfig = EnvPlugin::get_or_init();
        if let Ok(plugin_type) = PluginType::from_str(self.get_plugin_name()) {
            match plugin_type {
                PluginType::MySQL => {
                    if let Some(instance) = env.get_default_mysql_instance() {
                        format!(
                            "{}:{}:{}",
                            instance.get_host(),
                            instance.get_port(),
                            instance.get_database()
                        )
                    } else {
                        "unknown".to_string()
                    }
                }
                PluginType::PostgreSQL => {
                    if let Some(instance) = env.get_default_postgresql_instance() {
                        format!(
                            "{}:{}:{}",
                            instance.get_host(),
                            instance.get_port(),
                            instance.get_database()
                        )
                    } else {
                        "unknown".to_string()
                    }
                }
                PluginType::Redis => {
                    if let Some(instance) = env.get_default_redis_instance() {
                        format!("{}:{}", instance.get_host(), instance.get_port())
                    } else {
                        "unknown".to_string()
                    }
                }
            }
        } else {
            "unknown".to_string()
        }
    }
}
impl AutoCreationLogger {
    #[instrument_trace]
    pub async fn log_auto_creation_start(plugin_type: PluginType, database_name: &str) {
        info!(
            "[AUTO-CREATION] Starting auto-creation for {plugin_type} database '{database_name}'"
        );
    }
    #[instrument_trace]
    pub async fn log_auto_creation_complete(plugin_type: PluginType, result: &AutoCreationResult) {
        if result.has_errors() {
            info!(
                "[AUTO-CREATION] Auto-creation completed for {plugin_type} with warnings {}",
                result.get_errors().join(", ")
            );
        } else {
            info!("[AUTO-CREATION] Auto-creation completed successfully for {plugin_type}");
        }
    }
    #[instrument_trace]
    pub async fn log_auto_creation_error(
        error: &AutoCreationError,
        operation: &str,
        plugin_type: PluginType,
        database_name: Option<&str>,
    ) {
        error!(
            "[AUTO-CREATION] {operation} failed for {plugin_type} database '{}' {error}",
            database_name.unwrap_or("unknown")
        );
    }
    #[instrument_trace]
    pub async fn log_connection_verification(
        plugin_type: PluginType,
        database_name: &str,
        success: bool,
        error: Option<&str>,
    ) {
        if success {
            info!(
                "[AUTO-CREATION] Connection verification successful for {plugin_type} database '{database_name}'"
            );
        } else {
            error!(
                "[AUTO-CREATION] Connection verification failed for {plugin_type} database '{database_name}' {}",
                error.unwrap_or("Unknown error")
            );
        };
    }
    #[instrument_trace]
    pub async fn log_database_created(database_name: &str, plugin_type: PluginType) {
        info!(
            "[AUTO-CREATION] Successfully created database '{database_name}' for {plugin_type} plugin"
        );
    }
    #[instrument_trace]
    pub async fn log_database_exists(database_name: &str, plugin_type: PluginType) {
        info!("[AUTO-CREATION] Database '{database_name}' already exists for {plugin_type} plugin");
    }
    #[instrument_trace]
    pub async fn log_table_created(table_name: &str, database_name: &str, plugin_type: PluginType) {
        info!(
            "[AUTO-CREATION] Successfully created table '{table_name}' in database '{database_name}' for {plugin_type} plugin"
        );
    }
    #[instrument_trace]
    pub async fn log_table_exists(table_name: &str, database_name: &str, plugin_type: PluginType) {
        info!(
            "[AUTO-CREATION] Table '{table_name}' already exists in database '{database_name}' for {plugin_type} plugin"
        );
    }
    #[instrument_trace]
    pub async fn log_tables_created(
        tables: &[String],
        database_name: &str,
        plugin_type: PluginType,
    ) {
        if tables.is_empty() {
            info!(
                "[AUTO-CREATION] No new tables created in database '{database_name}' for {plugin_type} plugin"
            );
        } else {
            info!(
                "[AUTO-CREATION] Created tables [{}] in database '{database_name}' for {plugin_type} plugin",
                tables.join(", ")
            );
        }
    }
}
```
# Path: hyperlane-quick-start/plugin/database/struct.rs
```rust
use super::*;
#[derive(Clone, Copy, Data, Debug, Default)]
pub struct DatabasePlugin;
#[derive(Clone, Data, Debug)]
pub struct ConnectionCache<T: Clone> {
    #[get(type(copy))]
    pub(super) last_attempt: Instant,
    pub(super) result: Result<T, String>,
}
#[derive(Clone, Copy, Data, Debug, Default)]
pub struct AutoCreationErrorHandler;
#[derive(Clone, Data, Debug, Default)]
pub struct AutoCreationResult {
    #[get(type(copy))]
    pub(super) database_created: bool,
    pub(super) duration: Duration,
    pub(super) errors: Vec<String>,
    pub(super) tables_created: Vec<String>,
}
#[derive(Clone, Data, Debug, New)]
pub struct TableSchema {
    pub(super) dependencies: Vec<String>,
    pub(super) name: String,
    pub(super) sql: String,
}
#[derive(Clone, Data, Debug, Default)]
pub struct DatabaseSchema {
    pub(super) constraints: Vec<String>,
    pub(super) indexes: Vec<String>,
    pub(super) init_data: Vec<String>,
    pub(super) tables: Vec<TableSchema>,
}
#[derive(Clone, Copy, Data, Debug, Default)]
pub struct AutoCreationConfig;
#[derive(Clone, Data, Debug, Default)]
pub struct PluginAutoCreationConfig {
    pub(super) plugin_name: String,
}
#[derive(Clone, Copy, Data, Debug, Default)]
pub struct AutoCreationLogger;
```
# Path: hyperlane-quick-start/plugin/database/enum.rs
```rust
#[derive(Clone, Debug)]
pub enum AutoCreationError {
    InsufficientPermissions(String),
    ConnectionFailed(String),
    SchemaError(String),
    Timeout(String),
    DatabaseError(String),
}
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum PluginType {
    MySQL,
    PostgreSQL,
    Redis,
}
```
# Path: hyperlane-quick-start/config/README.md
## hyperlane-config
> Hyperlane configuration module providing comprehensive configuration management capabilities for the framework.
## Official Documentation
- [Official Documentation](https://docs.ltpp.vip/hyperlane/)
## Api Docs
- [Api Docs](https://docs.rs/hyperlane/latest/)
## Contact
# Path: hyperlane-quick-start/config/lib.rs
```rust
pub mod application;
pub mod framework;
use hyperlane_utils::log::*;
```
# Path: hyperlane-quick-start/config/application/mod.rs
```rust
pub mod logger;
pub mod logo_img;
use super::*;
```
# Path: hyperlane-quick-start/config/application/logger/const.rs
```rust
use super::*;
#[cfg(debug_assertions)]
pub const LOG_LEVEL_FILTER: LevelFilter = LevelFilter::Trace;
#[cfg(not(debug_assertions))]
pub const LOG_LEVEL_FILTER: LevelFilter = LevelFilter::Info;
```
# Path: hyperlane-quick-start/config/application/logger/mod.rs
```rust
mod r#const;
pub use r#const::*;
use super::*;
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
# Path: hyperlane-quick-start/config/framework/const.rs
```rust
pub const CACHE_CONTROL_STATIC_ASSETS: &str = "public, max-age=31536000, immutable";
pub const CACHE_CONTROL_SHORT_TERM: &str = "public, max-age=3600";
pub const EXPIRES_FAR_FUTURE: &str = "Wed, 1 Apr 8888 00:00:00 GMT";
```
# Path: hyperlane-quick-start/config/framework/mod.rs
```rust
mod r#const;
pub use r#const::*;
```
# Path: hyperlane-quick-start/application/README.md
## hyperlane-application
> Hyperlane application module containing core application logic, controllers, services, and middleware components.
## Official Documentation
- [Official Documentation](https://docs.ltpp.vip/hyperlane/)
## Api Docs
- [Api Docs](https://docs.rs/hyperlane/latest/)
## Contact
# Path: hyperlane-quick-start/application/lib.rs
```rust
pub mod controller;
pub mod domain;
pub mod exception;
pub mod mapper;
pub mod middleware;
pub mod model;
pub mod repository;
pub mod service;
pub mod utils;
pub mod view;
use {
    chrono::Utc,
    hyperlane::*,
    hyperlane_utils::{log::*, *},
    serde::{Deserialize, Serialize},
    serde_with::skip_serializing_none,
    utoipa::ToSchema,
};
```
# Path: hyperlane-quick-start/application/exception/mod.rs
```rust
mod r#impl;
mod r#struct;
pub use r#struct::*;
use {super::*, model::response::common::*};
```
# Path: hyperlane-quick-start/application/exception/impl.rs
```rust
use super::*;
impl ServerHook for TaskPanicHook {
    #[task_panic_data(task_panic_data)]
    #[instrument_trace]
    async fn new(ctx: &mut Context) -> Self {
        Self {
            content_type: ContentType::format_content_type_with_charset(APPLICATION_JSON, UTF8),
            response_body: task_panic_data.to_string(),
        }
    }
    #[prologue_macros(
        response_version(HttpVersion::Http1_1),
        response_status_code(500),
        clear_response_headers,
        response_header(SERVER => HYPERLANE),
        response_header(CONTENT_TYPE, &self.content_type),
    )]
    #[epilogue_macros(response_body(&response_body), try_send)]
    #[instrument_trace]
    async fn handle(self, ctx: &mut Context) {
        debug!("TaskPanicHook request => {}", ctx.get_request());
        error!("TaskPanicHook => {}", self.get_response_body());
        let api_response: ApiResponse<()> =
            ApiResponse::error_with_code(ResponseCode::InternalError, self.get_response_body());
        let response_body: Vec<u8> = api_response.to_json_bytes();
    }
}
impl ServerHook for RequestErrorHook {
    #[request_error_data(request_error_data)]
    #[instrument_trace]
    async fn new(_ctx: &mut Context) -> Self {
        Self {
            response_status_code: request_error_data.get_http_status_code(),
            content_type: ContentType::format_content_type_with_charset(APPLICATION_JSON, UTF8),
            response_body: request_error_data.to_string(),
        }
    }
    #[prologue_macros(
        response_version(HttpVersion::Http1_1),
        response_status_code(self.get_response_status_code()),
        clear_response_headers,
        response_header(SERVER => HYPERLANE),
        response_header(CONTENT_TYPE, &self.content_type),
        response_header(TRACE => uuid::Uuid::new_v4().to_string()),
    )]
    #[epilogue_macros(response_body(&response_body), try_send)]
    #[instrument_trace]
    async fn handle(self, ctx: &mut Context) {
        if self.get_response_status_code() == HttpStatus::BadRequest.code() {
            ctx.set_aborted(true);
            debug!("Context aborted");
            return;
        }
        if self.get_response_status_code() != HttpStatus::RequestTimeout.code() {
            debug!("RequestErrorHook request => {}", ctx.get_request());
            error!("RequestErrorHook => {}", self.get_response_body());
        }
        let api_response: ApiResponse<()> =
            ApiResponse::error_with_code(ResponseCode::InternalError, self.get_response_body());
        let response_body: Vec<u8> = api_response.to_json_bytes();
    }
}
```
# Path: hyperlane-quick-start/application/exception/struct.rs
```rust
use super::*;
#[task_panic]
#[derive(Clone, Data, Debug, Default)]
pub struct TaskPanicHook {
    pub(super) content_type: String,
    pub(super) response_body: String,
}
#[request_error]
#[derive(Clone, Data, Debug, Default)]
pub struct RequestErrorHook {
    #[get(type(copy))]
    pub(super) response_status_code: ResponseStatusCode,
    pub(super) content_type: String,
    pub(super) response_body: String,
}
```
# Path: hyperlane-quick-start/application/middleware/mod.rs
```rust
pub mod request;
pub mod response;
use {super::*, utils::json::*};
```
# Path: hyperlane-quick-start/application/middleware/request/mod.rs
```rust
mod r#impl;
mod r#struct;
pub use r#struct::*;
use super::*;
use hyperlane_resources::templates::*;
```
# Path: hyperlane-quick-start/application/middleware/request/impl.rs
```rust
use super::*;
impl ServerHook for HttpRequestMiddleware {
    #[instrument_trace]
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        reject(ctx.get_request().get_version().is_http()),
        send,
    )]
    #[instrument_trace]
    async fn handle(self, ctx: &mut Context) {
        ctx.set_closed(true);
    }
}
impl ServerHook for CrossMiddleware {
    #[instrument_trace]
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[response_version(HttpVersion::Http1_1)]
    #[response_header(ACCESS_CONTROL_ALLOW_ORIGIN => WILDCARD_ANY)]
    #[response_header(ACCESS_CONTROL_ALLOW_METHODS => ALL_METHODS)]
    #[response_header(ACCESS_CONTROL_ALLOW_HEADERS => WILDCARD_ANY)]
    #[instrument_trace]
    async fn handle(self, ctx: &mut Context) {}
}
impl ServerHook for ResponseHeaderMiddleware {
    #[instrument_trace]
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[response_header(DATE => gmt())]
    #[response_header(SERVER => HYPERLANE)]
    #[response_header(CONNECTION => KEEP_ALIVE)]
    #[response_header(TRACE => uuid::Uuid::new_v4().to_string())]
    #[epilogue_macros(response_header(CONTENT_TYPE => content_type))]
    #[instrument_trace]
    async fn handle(self, ctx: &mut Context) {
        let content_type: String = ContentType::format_content_type_with_charset(TEXT_HTML, UTF8);
    }
}
impl ServerHook for ResponseStatusCodeMiddleware {
    #[instrument_trace]
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[response_status_code(200)]
    #[instrument_trace]
    async fn handle(self, ctx: &mut Context) {}
}
impl ServerHook for ResponseBodyMiddleware {
    #[instrument_trace]
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[epilogue_macros(response_body(TEMPLATES_INDEX_HTML.replace("{{ time }}", &time())))]
    #[instrument_trace]
    async fn handle(self, ctx: &mut Context) {}
}
impl ServerHook for OptionMethodMiddleware {
    #[instrument_trace]
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        filter(ctx.get_request().get_method().is_options()),
        send
    )]
    #[instrument_trace]
    async fn handle(self, ctx: &mut Context) {
        ctx.set_aborted(true);
    }
}
impl ServerHook for UpgradeMiddleware {
    #[instrument_trace]
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        ws_upgrade_type,
        response_version(HttpVersion::Http1_1),
        response_status_code(101),
        response_body(&vec![]),
        response_header(UPGRADE => WEBSOCKET),
        response_header(CONNECTION => UPGRADE),
        response_header(SEC_WEBSOCKET_ACCEPT => WebSocketFrame::generate_accept_key(ctx.get_request().get_header_back(SEC_WEBSOCKET_KEY))),
        send
    )]
    #[instrument_trace]
    async fn handle(self, ctx: &mut Context) {}
}
```
# Path: hyperlane-quick-start/application/middleware/request/struct.rs
```rust
use super::*;
#[request_middleware(1)]
#[derive(Clone, Copy, Data, Debug, Default)]
pub struct HttpRequestMiddleware;
#[request_middleware(2)]
#[derive(Clone, Copy, Data, Debug, Default)]
pub struct CrossMiddleware;
#[request_middleware(3)]
#[derive(Clone, Copy, Data, Debug, Default)]
pub struct ResponseHeaderMiddleware;
#[request_middleware(4)]
#[derive(Clone, Copy, Data, Debug, Default)]
pub struct ResponseStatusCodeMiddleware;
#[request_middleware(5)]
#[derive(Clone, Copy, Data, Debug, Default)]
pub struct ResponseBodyMiddleware;
#[request_middleware(6)]
#[derive(Clone, Copy, Data, Debug, Default)]
pub struct OptionMethodMiddleware;
#[request_middleware(7)]
#[derive(Clone, Copy, Data, Debug, Default)]
pub struct UpgradeMiddleware;
```
# Path: hyperlane-quick-start/application/middleware/response/mod.rs
```rust
mod r#impl;
mod r#struct;
pub use r#struct::*;
use super::*;
```
# Path: hyperlane-quick-start/application/middleware/response/impl.rs
```rust
use super::*;
impl ServerHook for SendMiddleware {
    #[instrument_trace]
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        reject(ctx.get_request().is_ws_upgrade_type()),
        try_send
    )]
    #[instrument_trace]
    async fn handle(self, ctx: &mut Context) {}
}
impl ServerHook for LogMiddleware {
    #[instrument_trace]
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[instrument_trace]
    async fn handle(self, ctx: &mut Context) {
        let request_json: String = get_request_json(ctx).await;
        let response_json: String = get_response_json(ctx).await;
        info!("{request_json}");
        info!("{response_json}");
    }
}
```
# Path: hyperlane-quick-start/application/middleware/response/struct.rs
```rust
use super::*;
#[response_middleware(1)]
#[derive(Clone, Copy, Data, Debug, Default)]
pub struct SendMiddleware;
#[response_middleware(2)]
#[derive(Clone, Copy, Data, Debug, Default)]
pub struct LogMiddleware;
```
# Path: hyperlane-quick-start/application/utils/mod.rs
```rust
pub mod json;
pub mod send;
use super::*;
```
# Path: hyperlane-quick-start/application/utils/send/mod.rs
```rust
mod r#fn;
pub use r#fn::*;
use super::*;
```
# Path: hyperlane-quick-start/application/utils/send/fn.rs
```rust
use super::*;
#[instrument_trace]
pub async fn try_send_body_hook(ctx: &mut Context) -> Result<(), ResponseError> {
    let send_result: Result<(), ResponseError> = if ctx.get_request().is_ws_upgrade_type() {
        let body: &ResponseBody = ctx.get_response().get_body();
        let frame_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(body);
        ctx.try_send_body_list_with_data(&frame_list).await
    } else {
        ctx.try_send_body().await
    };
    if send_result.is_err() {
        ctx.set_aborted(true).set_closed(true);
    }
    send_result
}
#[instrument_trace]
pub async fn send_body_hook(ctx: &mut Context) {
    try_send_body_hook(ctx).await.unwrap()
}
```
# Path: hyperlane-quick-start/application/utils/json/mod.rs
```rust
mod r#fn;
pub use r#fn::*;
use super::*;
```
# Path: hyperlane-quick-start/application/utils/json/fn.rs
```rust
use super::*;
#[instrument_trace]
pub async fn get_request_json(ctx: &Context) -> String {
    let mut request: Request = ctx.get_request().clone();
    request.set_body(request.get_body().len().to_string().into_bytes());
    serde_json::to_string(&request).unwrap_or(request.to_string())
}
#[instrument_trace]
pub async fn get_response_json(ctx: &Context) -> String {
    let mut response: Response = ctx.get_response().clone();
    response.set_body(response.get_body().len().to_string().into_bytes());
    serde_json::to_string(&response).unwrap_or(response.to_string())
}
```
# Path: hyperlane-quick-start/application/view/mod.rs
```rust
mod favicon;
use super::*;
```
# Path: hyperlane-quick-start/application/view/favicon/mod.rs
```rust
mod r#impl;
mod r#struct;
pub use r#struct::*;
use super::*;
use hyperlane_config::application::logo_img::*;
```
# Path: hyperlane-quick-start/application/view/favicon/impl.rs
```rust
use super::*;
impl ServerHook for FaviconRoute {
    #[instrument_trace]
    async fn new(_ctx: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        get_method,
        response_status_code(302),
        response_header(LOCATION => LOGO_IMG_URL)
    )]
    #[instrument_trace]
    async fn handle(self, ctx: &mut Context) {}
}
```
# Path: hyperlane-quick-start/application/view/favicon/struct.rs
```rust
use super::*;
#[route("/favicon.ico")]
#[derive(Clone, Copy, Data, Debug, Default)]
pub struct FaviconRoute;
```
# Path: hyperlane-quick-start/application/model/mod.rs
```rust
pub mod request;
pub mod response;
use super::*;
```
# Path: hyperlane-quick-start/application/model/response/mod.rs
```rust
pub mod common;
use super::*;
```
# Path: hyperlane-quick-start/application/model/response/common/mod.rs
```rust
mod r#enum;
mod r#impl;
mod r#struct;
pub use {r#enum::*, r#struct::*};
use super::*;
```
# Path: hyperlane-quick-start/application/model/response/common/impl.rs
```rust
use super::*;
impl ResponseCode {
    #[instrument_trace]
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
    T: Clone + Default + Serialize,
{
    #[instrument_trace]
    pub fn default_success() -> Self {
        let mut instance: ApiResponse<T> = Self::default();
        instance
            .set_code(ResponseCode::Success as i32)
            .set_message("Success".to_string())
            .set_data(None)
            .set_timestamp(Some(Utc::now().timestamp_millis()));
        instance
    }
    #[instrument_trace]
    pub fn success(data: T) -> Self {
        let mut instance: ApiResponse<T> = Self::default();
        instance
            .set_code(ResponseCode::Success as i32)
            .set_message("Success".to_string())
            .set_data(Some(data))
            .set_timestamp(Some(Utc::now().timestamp_millis()));
        instance
    }
    #[instrument_trace]
    pub fn success_with_message(data: T, message: impl Into<String>) -> Self {
        let mut instance: ApiResponse<T> = Self::default();
        instance
            .set_code(ResponseCode::Success as i32)
            .set_message(message.into())
            .set_data(Some(data))
            .set_timestamp(Some(Utc::now().timestamp_millis()));
        instance
    }
    #[instrument_trace]
    pub fn default_error() -> Self {
        let mut instance: ApiResponse<T> = Self::default();
        instance
            .set_code(ResponseCode::InternalError as i32)
            .set_message("Internal server error".to_string())
            .set_data(None)
            .set_timestamp(Some(Utc::now().timestamp_millis()));
        instance
    }
    #[instrument_trace]
    pub fn error(message: impl Into<String>) -> Self {
        let mut instance: ApiResponse<T> = Self::default();
        instance
            .set_code(ResponseCode::InternalError as i32)
            .set_message(message.into())
            .set_data(None)
            .set_timestamp(Some(Utc::now().timestamp_millis()));
        instance
    }
    #[instrument_trace]
    pub fn error_with_code(code: ResponseCode, message: impl ToString) -> Self {
        let mut instance: ApiResponse<T> = Self::default();
        instance
            .set_code(code as i32)
            .set_message(message.to_string())
            .set_data(None)
            .set_timestamp(Some(Utc::now().timestamp_millis()));
        instance
    }
    #[instrument_trace]
    pub fn to_json_bytes(&self) -> Vec<u8> {
        serde_json::to_vec(self).unwrap_or_default()
    }
}
impl ApiResponse<()> {
    #[instrument_trace]
    pub fn success_without_data(message: impl Into<String>) -> Self {
        let mut instance: ApiResponse<()> = Self::default();
        instance
            .set_code(ResponseCode::Success as i32)
            .set_message(message.into())
            .set_data(None)
            .set_timestamp(Some(Utc::now().timestamp_millis()));
        instance
    }
}
```
# Path: hyperlane-quick-start/application/model/response/common/struct.rs
```rust
use super::*;
#[skip_serializing_none]
#[derive(Clone, Data, Debug, Default, Deserialize, Serialize, ToSchema)]
pub struct ApiResponse<T>
where
    T: Clone + Default + Serialize,
{
    #[get(type(copy))]
    pub(super) code: i32,
    pub(super) message: String,
    pub(super) data: Option<T>,
    #[get(type(copy))]
    pub(super) timestamp: Option<i64>,
}
```
# Path: hyperlane-quick-start/application/model/response/common/enum.rs
```rust
use super::*;
#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize, ToSchema)]
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
# Path: hyperlane-quick-start/src/main.rs
```rust
use {
    hyperlane_bootstrap::{
        application::{db::*, env::*, logger::*},
        common::*,
        framework::{runtime::*, server::*},
    },
    hyperlane_plugin::{common::GetOrInit, env::*, process::*},
};
use hyperlane_utils::log::*;
fn main() {
    EnvBootstrap::init();
    LoggerBootstrap::init();
    EnvConfig::log_config();
    info!("Environment configuration loaded successfully");
    let env_config: &EnvConfig = EnvPlugin::get_or_init();
    RuntimeBootstrap::init().get_runtime().block_on(async move {
        DbBootstrap::init().await;
        ProcessPlugin::create(env_config.get_server_pid_file_path(), || async {
            ServerBootstrap::init().await;
        })
        .await;
    });
}
```
# Path: hyperlane-quick-start/bootstrap/README.md
## hyperlane-bootstrap
> Hyperlane bootstrap crate providing application initialization and framework lifecycle management.
## Official Documentation
- [Official Documentation](https://docs.ltpp.vip/hyperlane/)
## Api Docs
- [Api Docs](https://docs.rs/hyperlane/latest/)
## Contact
# Path: hyperlane-quick-start/bootstrap/lib.rs
```rust
pub mod application;
pub mod common;
pub mod framework;
use common::*;
use {
    hyperlane::*,
    hyperlane_utils::{log::*, *},
};
```
# Path: hyperlane-quick-start/bootstrap/common/trait.rs
```rust
pub trait BootstrapSyncInit {
    fn init() -> Self;
}
pub trait BootstrapAsyncInit {
    fn init() -> impl Future<Output = Self> + Send;
}
```
# Path: hyperlane-quick-start/bootstrap/common/mod.rs
```rust
mod r#trait;
pub use r#trait::*;
```
# Path: hyperlane-quick-start/bootstrap/application/mod.rs
```rust
pub mod db;
pub mod env;
pub mod logger;
use super::*;
```
# Path: hyperlane-quick-start/bootstrap/application/logger/mod.rs
```rust
mod r#impl;
mod r#struct;
pub use r#struct::*;
use super::*;
use {
    hyperlane_config::application::logger::*,
    hyperlane_plugin::{common::*, env::*, logger::*},
};
```
# Path: hyperlane-quick-start/bootstrap/application/logger/impl.rs
```rust
use super::*;
impl BootstrapSyncInit for LoggerBootstrap {
    fn init() -> Self {
        let env_config: &EnvConfig = EnvPlugin::get_or_init();
        let mut file_logger: FileLogger = FileLogger::default();
        file_logger.set_path(env_config.get_server_log_dir());
        file_logger.set_limit_file_size(env_config.get_server_log_size());
        Logger::init(LOG_LEVEL_FILTER, file_logger);
        Self
    }
}
```
# Path: hyperlane-quick-start/bootstrap/application/logger/struct.rs
```rust
use super::*;
#[derive(Clone, Copy, Data, Debug, Default)]
pub struct LoggerBootstrap;
```
# Path: hyperlane-quick-start/bootstrap/application/env/mod.rs
```rust
mod r#impl;
mod r#struct;
pub use r#struct::*;
use super::*;
use hyperlane_plugin::env::*;
```
# Path: hyperlane-quick-start/bootstrap/application/env/impl.rs
```rust
use super::*;
impl BootstrapSyncInit for EnvBootstrap {
    fn init() -> Self {
        if let Err(error) = EnvPlugin::try_load_config() {
            panic!("{error}");
        }
        Self
    }
}
```
# Path: hyperlane-quick-start/bootstrap/application/env/struct.rs
```rust
use super::*;
#[derive(Clone, Copy, Data, Debug, Default)]
pub struct EnvBootstrap;
```
# Path: hyperlane-quick-start/bootstrap/application/db/mod.rs
```rust
mod r#impl;
mod r#struct;
pub use r#struct::*;
use super::*;
use hyperlane_plugin::{common::*, database::*, mysql::*, postgresql::*, redis::*};
use {redis::Connection, sea_orm::DatabaseConnection};
```
# Path: hyperlane-quick-start/bootstrap/application/db/impl.rs
```rust
use super::*;
impl BootstrapAsyncInit for DbBootstrap {
    async fn init() -> Self {
        let _: Result<DatabaseConnection, String> =
            MySqlPlugin::connection_db(DEFAULT_MYSQL_INSTANCE_NAME, None).await;
        let _: Result<DatabaseConnection, String> =
            PostgreSqlPlugin::connection_db(DEFAULT_POSTGRESQL_INSTANCE_NAME, None).await;
        let _: Result<ArcRwLock<Connection>, String> =
            RedisPlugin::connection_db(DEFAULT_REDIS_INSTANCE_NAME, None).await;
        match DatabasePlugin::initialize_auto_creation().await {
            Ok(_) => {
                info!("Auto-creation initialization successful");
            }
            Err(error) => {
                error!("Auto-creation initialization failed {error}");
            }
        };
        Self
    }
}
```
# Path: hyperlane-quick-start/bootstrap/application/db/struct.rs
```rust
use super::*;
#[derive(Clone, Copy, Data, Debug, Default)]
pub struct DbBootstrap;
```
# Path: hyperlane-quick-start/bootstrap/framework/mod.rs
```rust
pub mod config;
pub mod runtime;
pub mod server;
use super::*;
```
# Path: hyperlane-quick-start/bootstrap/framework/config/mod.rs
```rust
mod r#impl;
mod r#struct;
pub use r#struct::*;
use super::*;
use hyperlane_plugin::{common::*, env::*};
```
# Path: hyperlane-quick-start/bootstrap/framework/config/impl.rs
```rust
use super::*;
impl BootstrapAsyncInit for ConfigBootstrap {
    #[hyperlane(server_config: ServerConfig)]
    async fn init() -> Self {
        let env_config: &EnvConfig = EnvPlugin::get_or_init();
        let mut request_config: RequestConfig = RequestConfig::default();
        request_config
            .set_max_body_size(env_config.get_server_request_max_body_size())
            .set_read_timeout_ms(env_config.get_server_request_http_read_timeout_ms());
        server_config.set_address(Server::format_bind_address(
            env_config.get_server_host(),
            env_config.get_server_port(),
        ));
        server_config.set_ttl(env_config.get_server_tti());
        server_config.set_nodelay(env_config.get_server_nodelay());
        debug!("Server config {server_config:?}");
        info!("Server initialization successful");
        Self {
            server_config,
            request_config,
        }
    }
}
```
# Path: hyperlane-quick-start/bootstrap/framework/config/struct.rs
```rust
use super::*;
#[derive(Clone, Data, Debug, Default)]
pub struct ConfigBootstrap {
    pub(super) server_config: ServerConfig,
    pub(super) request_config: RequestConfig,
}
```
# Path: hyperlane-quick-start/bootstrap/framework/server/mod.rs
```rust
mod r#impl;
mod r#struct;
pub use r#struct::*;
use {super::*, config::*};
#[allow(unused_imports)]
use {hyperlane_application::*, hyperlane_plugin::env::*, hyperlane_plugin::shutdown::*};
```
# Path: hyperlane-quick-start/bootstrap/framework/server/impl.rs
```rust
use hyperlane_plugin::{common::GetOrInit, env::EnvPlugin};
use super::*;
impl ServerBootstrap {
    async fn print_route_matcher(server: &Server) {
        let route_matcher: &RouteMatcher = server.get_route_matcher();
        for key in route_matcher.get_static_route().keys() {
            info!("Static route {key}");
        }
        for value in route_matcher.get_dynamic_route().values() {
            for (route_pattern, _) in value {
                info!("Dynamic route {route_pattern}");
            }
        }
        for value in route_matcher.get_regex_route().values() {
            for (route_pattern, _) in value {
                info!("Regex route {route_pattern}");
            }
        }
    }
}
impl BootstrapAsyncInit for ServerBootstrap {
    #[hyperlane(server: Server)]
    async fn init() -> Self {
        let config: ConfigBootstrap = ConfigBootstrap::init().await;
        server
            .request_config(*config.get_request_config())
            .server_config(config.get_server_config().clone());
        match server.run().await {
            Ok(server_hook) => {
                let env_config: &EnvConfig = EnvPlugin::get_or_init();
                let host_port: String = format!(
                    "{}{COLON}{}",
                    env_config.get_server_host(),
                    env_config.get_server_port()
                );
                Self::print_route_matcher(&server).await;
                info!("Server listen in {host_port}");
                ShutdownPlugin::set(server_hook.get_shutdown_hook());
                server_hook.wait().await;
            }
            Err(server_error) => error!("Server run error {server_error}"),
        }
        Self
    }
}
```
# Path: hyperlane-quick-start/bootstrap/framework/server/struct.rs
```rust
use super::*;
#[derive(Clone, Copy, Data, Debug, Default)]
pub struct ServerBootstrap;
```
# Path: hyperlane-quick-start/bootstrap/framework/runtime/mod.rs
```rust
mod r#impl;
mod r#struct;
pub use r#struct::*;
use super::*;
use tokio::runtime::{Builder, Runtime};
```
# Path: hyperlane-quick-start/bootstrap/framework/runtime/impl.rs
```rust
use super::*;
impl BootstrapSyncInit for RuntimeBootstrap {
    fn init() -> Self {
        let runtime: Runtime = Builder::new_multi_thread()
            .worker_threads(num_cpus::get_physical() << 1)
            .thread_stack_size(1_048_576)
            .max_blocking_threads(2_048)
            .max_io_events_per_tick(1_024)
            .enable_all()
            .build()
            .unwrap();
        Self { runtime }
    }
}
```
# Path: hyperlane-quick-start/bootstrap/framework/runtime/struct.rs
```rust
use super::*;
#[derive(Data, Debug)]
pub struct RuntimeBootstrap {
    pub(super) runtime: Runtime,
}
```
# Path: hyperlane-quick-start/resources/README.md
## hyperlane-resources
> Hyperlane resources module containing various resources and utilities used by the framework.
## Official Documentation
- [Official Documentation](https://docs.ltpp.vip/hyperlane/)
## Api Docs
- [Api Docs](https://docs.rs/hyperlane/latest/)
## Contact
# Path: hyperlane-quick-start/resources/lib.rs
```rust
pub mod docker;
pub mod env;
pub mod sql;
pub mod r#static;
pub mod templates;
```
# Path: hyperlane-quick-start/resources/env/const.rs
```rust
#[cfg(debug_assertions)]
pub const SERVER_ENV_FILE_PATH: &str = "./resources/env/dev/server.env";
#[cfg(not(debug_assertions))]
pub const SERVER_ENV_FILE_PATH: &str = "./resources/env/release/server.env";
```
# Path: hyperlane-quick-start/resources/env/mod.rs
```rust
mod r#const;
pub use r#const::*;
```
# Path: hyperlane-quick-start/resources/env/release/server.env
```env
DOCKER_COMPOSE_FILE_PATH=./resources/docker/release/server_docker_compose.yml
DB_CONNECTION_TIMEOUT_MILLIS=1000
DB_RETRY_INTERVAL_MILLIS=30000
GPT_API_URL=http://hyperlane:1234/v1/chat/completions
GPT_MODEL=qwen2.5-coder-1.5b-instruct
MYSQL='[{"name":"mysql_default","host":"hyperlane","port":3306,"database":"hyperlane","username":"hyperlane","password":"hyperlane"}]'
POSTGRESQL='[{"name":"postgres_default","host":"hyperlane","port":5432,"database":"hyperlane","username":"hyperlane","password":"hyperlane"}]'
REDIS='[{"name":"redis_default","host":"hyperlane","port":6379,"username":"","password":"hyperlane"}]'
SERVER_PORT=65002
SERVER_HOST=0.0.0.0
SERVER_BUFFER=8192
SERVER_LOG_SIZE=100024000
SERVER_LOG_DIR=./data/release/logs
SERVER_INNER_PRINT=true
SERVER_INNER_LOG=true
SERVER_NODELAY=false
SERVER_TTI=128
SERVER_PID_FILE_PATH=./data/release/process/hyperlane.pid
SERVER_REQUEST_HTTP_READ_TIMEOUT_MS=60000
SERVER_REQUEST_MAX_BODY_SIZE=104857600
```
# Path: hyperlane-quick-start/resources/env/dev/server.env
```env
DOCKER_COMPOSE_FILE_PATH=./resources/docker/dev/server_docker_compose.yml
DB_CONNECTION_TIMEOUT_MILLIS=1000
DB_RETRY_INTERVAL_MILLIS=30000
GPT_API_URL=http://hyperlane:1234/v1/chat/completions
GPT_MODEL=qwen2.5-coder-1.5b-instruct
MYSQL='[{"name":"mysql_default","host":"hyperlane","port":3306,"database":"hyperlane","username":"hyperlane","password":"hyperlane"}]'
POSTGRESQL='[{"name":"postgres_default","host":"hyperlane","port":5432,"database":"hyperlane","username":"hyperlane","password":"hyperlane"}]'
REDIS='[{"name":"redis_default","host":"hyperlane","port":6379,"username":"","password":"hyperlane"}]'
SERVER_PORT=60000
SERVER_HOST=0.0.0.0
SERVER_BUFFER=60000
SERVER_LOG_SIZE=100024000
SERVER_LOG_DIR=./data/dev/logs
SERVER_INNER_PRINT=true
SERVER_INNER_LOG=true
SERVER_NODELAY=false
SERVER_TTI=128
SERVER_PID_FILE_PATH=./data/dev/process/hyperlane.pid
SERVER_REQUEST_HTTP_READ_TIMEOUT_MS=60000
SERVER_REQUEST_MAX_BODY_SIZE=104857600
```
# Path: hyperlane-quick-start/resources/templates/const.rs
```rust
pub const TEMPLATES_INDEX_HTML: &str = include_str!("./index/index.html");
```
# Path: hyperlane-quick-start/resources/templates/mod.rs
```rust
mod r#const;
pub use r#const::*;
```
# Path: hyperlane-quick-start/resources/templates/index/index.html
```html
<!doctype html>
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
        transition:
          color 0.3s,
          border-bottom-color 0.3s;
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
# Path: hyperlane-quick-start/resources/docker/const.rs
```rust
#[cfg(debug_assertions)]
pub const SERVER_DOCKER_COMPOSE_FILE_PATH: &str =
    "./resources/docker/dev/server_docker_compose.yml";
#[cfg(not(debug_assertions))]
pub const SERVER_DOCKER_COMPOSE_FILE_PATH: &str =
    "./resources/docker/release/server_docker_compose.yml";
#[cfg(debug_assertions)]
pub const SERVER_DOCKERFILE_PATH: &str = "./resources/docker/dev/server.dockerfile";
#[cfg(not(debug_assertions))]
pub const SERVER_DOCKERFILE_PATH: &str = "./resources/docker/release/server.dockerfile";
```
# Path: hyperlane-quick-start/resources/docker/mod.rs
```rust
mod r#const;
pub use r#const::*;
```
# Path: hyperlane-quick-start/resources/docker/release/server.dockerfile
```dockerfile
FROM rust:1.93-bookworm
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update -yqq && \
    apt-get install -yqq cmake g++ binutils lld
WORKDIR /hyperlane-quick-start
COPY . .
RUN RUSTFLAGS='-C target-feature=-crt-static' cargo build --release --target x86_64-unknown-linux-gnu && \
    cp -f /hyperlane-quick-start/target/x86_64-unknown-linux-gnu/release/hyperlane-quick-start /hyperlane-quick-start/hyperlane-quick-start && \
    rm -rf /hyperlane-quick-start/target
EXPOSE 65002
CMD ["/hyperlane-quick-start/hyperlane-quick-start"]
```
# Path: hyperlane-quick-start/resources/docker/dev/server.dockerfile
```dockerfile
FROM rust:1.93-bookworm
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update -yqq && \
    apt-get install -yqq cmake g++ binutils lld
WORKDIR /hyperlane-quick-start
COPY . .
RUN cargo build && \
    cp -f /hyperlane-quick-start/target/debug/hyperlane-quick-start /hyperlane-quick-start/hyperlane-quick-start && \
    rm -rf /hyperlane-quick-start/target
EXPOSE 60000
CMD ["/hyperlane-quick-start/hyperlane-quick-start"]
```
# Path: hyperlane-quick-start/resources/static/not_found/index.html
```html
<!doctype html>
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
        transition:
          color 0.3s,
          border-bottom-color 0.3s;
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
# Path: hyperlane-cli/README.md
# hyperlane-cli
[Official Documentation](https://docs.ltpp.vip/hyperlane-cli/)
[Api Docs](https://docs.rs/hyperlane-cli/latest/)
## Description
> A command-line tool for Hyperlane framework.
## Installation
To install `hyperlane-cli` run cmd:
```shell
cargo add hyperlane-cli
```
## Contact
# Path: hyperlane-cli/src/main.rs
```rust
mod bump;
mod command;
mod config;
mod fmt;
mod help;
mod new;
mod publish;
mod template;
mod version;
mod watch;
pub(crate) use {
    bump::*, command::*, config::*, fmt::*, help::*, new::*, publish::*, template::*, version::*,
    watch::*,
};
pub(crate) use std::{
    collections::{HashMap, VecDeque},
    env::args,
    fs::{create_dir_all, read_to_string, write},
    path::{Path, PathBuf},
    process::{ExitStatus, Stdio, exit},
    str::FromStr,
    sync::{Arc, LazyLock},
};
pub(crate) use {
    regex::{Captures, Regex},
    tokio::{process::Command, sync::Mutex},
};
#[tokio::main]
async fn main() {
    let args: Args = parse_args();
    match args.command {
        CommandType::Fmt => {
            if let Err(error) = execute_fmt(&args).await {
                eprintln!("fmt failed: {error}");
                exit(1);
            }
        }
        CommandType::Watch => {
            if let Err(error) = execute_watch().await {
                eprintln!("watch failed: {error}");
                exit(1);
            }
        }
        CommandType::Bump => {
            let manifest_path: String = args
                .manifest_path
                .unwrap_or_else(|| "Cargo.toml".to_string());
            let bump_type: BumpVersionType = args.bump_type.unwrap_or(BumpVersionType::Patch);
            match execute_bump(&manifest_path, &bump_type) {
                Ok(new_version) => {
                    println!("Version bumped to {new_version}");
                }
                Err(error) => {
                    eprintln!("bump failed: {error}");
                    exit(1);
                }
            }
        }
        CommandType::Publish => {
            let manifest_path: String = args
                .manifest_path
                .unwrap_or_else(|| "Cargo.toml".to_string());
            let max_retries: u32 = args.max_retries;
            match execute_publish(&manifest_path, max_retries).await {
                Ok(results) => {
                    let failed_count: usize = results
                        .iter()
                        .filter(|r: &&PublishResult| !r.success)
                        .count();
                    if failed_count > 0 {
                        eprintln!("Publish completed with {failed_count} failures");
                        exit(1);
                    } else {
                        println!("All packages published successfully");
                    }
                }
                Err(error) => {
                    eprintln!("publish failed: {error}");
                    exit(1);
                }
            }
        }
        CommandType::New => {
            if let Some(project_name) = args.project_name {
                if let Err(error) = execute_new(&project_name).await {
                    eprintln!("new failed: {error}");
                    exit(1);
                }
            } else {
                eprintln!(
                    "Error: Project name is required. Usage: hyperlane-cli new <PROJECT_NAME>"
                );
                exit(1);
            }
        }
        CommandType::Template => {
            let template_type: TemplateType = match args.template_type {
                Some(tt) => tt,
                None => {
                    eprintln!(
                        "Error: Template type is required. Usage: hyperlane-cli template <TYPE> [SUBTYPE] <NAME>"
                    );
                    exit(1);
                }
            };
            let component_name: String = match args.component_name {
                Some(cn) => cn,
                None => {
                    eprintln!(
                        "Error: Component name is required. Usage: hyperlane-cli template <TYPE> [SUBTYPE] <NAME>"
                    );
                    exit(1);
                }
            };
            if template_type == TemplateType::Model && args.model_sub_type.is_none() {
                eprintln!("Error: Model type requires subtype (application|request|response)");
                exit(1);
            }
            if let Err(error) =
                execute_template(template_type, &component_name, args.model_sub_type).await
            {
                eprintln!("template failed: {error}");
                exit(1);
            }
        }
        CommandType::Help => print_help(),
        CommandType::Version => print_version(),
    }
}
```
# Path: hyperlane-cli/src/fmt/mod.rs
```rust
mod r#fn;
mod r#static;
#[cfg(test)]
mod test;
pub(crate) use {r#fn::*, r#static::*};
```
# Path: hyperlane-cli/src/fmt/fn.rs
```rust
use crate::*;
fn sort_derive_in_line(line: &str) -> Option<String> {
    let captures: Captures<'_> = DERIVE_REGEX.captures(line)?;
    let derive_content: &str = captures.get(1)?.as_str();
    let mut traits: Vec<String> = derive_content
        .split(',')
        .map(|s: &str| s.trim().to_string())
        .filter(|s: &String| !s.is_empty())
        .collect();
    traits.sort_by_key(|a| a.to_lowercase());
    let sorted_traits: String = traits.join(", ");
    let result: String = line.replace(derive_content, &sorted_traits);
    Some(result)
}
async fn format_derive_in_file(file_path: &Path) -> Result<bool, std::io::Error> {
    let content: String = read_to_string(file_path)?;
    let lines: std::str::Lines<'_> = content.lines();
    let mut modified: bool = false;
    let mut new_content: String = String::new();
    for line in lines {
        let trimmed: &str = line.trim();
        let new_line: String = if trimmed.starts_with("#[derive(") {
            if let Some(sorted) = sort_derive_in_line(line) {
                if sorted != line {
                    modified = true;
                }
                sorted
            } else {
                line.to_string()
            }
        } else {
            line.to_string()
        };
        new_content.push_str(&new_line);
        new_content.push('\n');
    }
    if modified {
        write(file_path, new_content)?;
    }
    Ok(modified)
}
async fn find_rust_files(manifest_path: &Path) -> Result<Vec<PathBuf>, std::io::Error> {
    let mut files: Vec<PathBuf> = Vec::new();
    let workspace_root: &Path = manifest_path.parent().unwrap_or(Path::new("."));
    let src_dir: PathBuf = workspace_root.join("src");
    if src_dir.exists() {
        find_rust_files_in_dir(&src_dir, &mut files).await?;
    }
    let content: String = read_to_string(manifest_path)?;
    if let Ok(doc) = toml::from_str::<toml::Value>(&content)
        && let Some(workspace) = doc.get("workspace")
            && let Some(members) = workspace
                .get("members")
                .and_then(|m: &toml::Value| m.as_array())
            {
                for member in members {
                    if let Some(pattern) = member.as_str() {
                        let member_src: PathBuf = workspace_root.join(pattern).join("src");
                        if member_src.exists() {
                            find_rust_files_in_dir(&member_src, &mut files).await?;
                        }
                    }
                }
            }
    Ok(files)
}
async fn find_rust_files_in_dir(
    dir: &Path,
    files: &mut Vec<PathBuf>,
) -> Result<(), std::io::Error> {
    let mut entries = tokio::fs::read_dir(dir).await?;
    while let Some(entry) = entries.next_entry().await? {
        let path: PathBuf = entry.path();
        if path.is_file()
            && path
                .extension()
                .is_some_and(|ext: &std::ffi::OsStr| ext == "rs")
        {
            files.push(path);
        } else if path.is_dir() {
            Box::pin(find_rust_files_in_dir(&path, files)).await?;
        }
    }
    Ok(())
}
async fn format_derive_attributes(manifest_path: &str) -> Result<(), std::io::Error> {
    let path: &Path = Path::new(manifest_path);
    let files: Vec<PathBuf> = find_rust_files(path).await?;
    let modified_count: Arc<Mutex<usize>> = Arc::new(Mutex::new(0));
    let mut handles: Vec<tokio::task::JoinHandle<Result<(), std::io::Error>>> = Vec::new();
    for file in files {
        let counter: Arc<Mutex<usize>> = Arc::clone(&modified_count);
        let handle: tokio::task::JoinHandle<Result<(), std::io::Error>> =
            tokio::spawn(async move {
                if format_derive_in_file(&file).await? {
                    let mut count: tokio::sync::MutexGuard<'_, usize> = counter.lock().await;
                    *count += 1;
                }
                Ok(())
            });
        handles.push(handle);
    }
    for handle in handles {
        handle.await??;
    }
    let count: usize = *modified_count.lock().await;
    if count > 0 {
        println!("Sorted derive attributes in {count} files");
    }
    Ok(())
}
async fn is_cargo_clippy_installed() -> bool {
    Command::new("cargo")
        .arg("clippy")
        .arg("--version")
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status()
        .await
        .is_ok_and(|status: ExitStatus| status.success())
}
async fn install_cargo_clippy() -> Result<(), std::io::Error> {
    println!("cargo-clippy not found, installing...");
    let mut cmd: Command = Command::new("rustup");
    cmd.arg("component").arg("add").arg("clippy");
    cmd.stdout(Stdio::inherit()).stderr(Stdio::inherit());
    let status: ExitStatus = cmd.status().await?;
    if !status.success() {
        return Err(std::io::Error::other("failed to install cargo-clippy"));
    }
    Ok(())
}
async fn execute_clippy_fix(args: &Args) -> Result<(), std::io::Error> {
    if !is_cargo_clippy_installed().await {
        install_cargo_clippy().await?;
    }
    let mut cmd: Command = Command::new("cargo");
    cmd.arg("clippy")
        .arg("--fix")
        .arg("--workspace")
        .arg("--all-targets")
        .arg("--allow-dirty");
    if let Some(ref manifest_path) = args.manifest_path {
        cmd.arg("--manifest-path").arg(manifest_path);
    }
    cmd.stdout(Stdio::inherit()).stderr(Stdio::inherit());
    let status: ExitStatus = cmd.status().await?;
    if !status.success() {
        return Err(std::io::Error::other("cargo clippy --fix failed"));
    }
    Ok(())
}
pub(crate) async fn execute_fmt(args: &Args) -> Result<(), std::io::Error> {
    let manifest_path: String = args
        .manifest_path
        .clone()
        .unwrap_or_else(|| "Cargo.toml".to_string());
    if !args.check {
        format_derive_attributes(&manifest_path).await?;
    }
    let mut cmd: Command = Command::new("cargo");
    cmd.arg("fmt");
    if args.check {
        cmd.arg("--check");
    }
    if let Some(ref manifest_path) = args.manifest_path {
        cmd.arg("--manifest-path").arg(manifest_path);
    }
    cmd.stdout(Stdio::inherit()).stderr(Stdio::inherit());
    let status: ExitStatus = cmd.status().await?;
    if !status.success() {
        return Err(std::io::Error::other("cargo fmt failed"));
    }
    if !args.check {
        execute_clippy_fix(args).await?;
    }
    Ok(())
}
pub(crate) async fn format_path(path: &std::path::Path) -> Result<(), std::io::Error> {
    let mut cmd: Command = Command::new("cargo");
    cmd.arg("fmt").arg("--").arg(path);
    cmd.stdout(Stdio::null()).stderr(Stdio::null());
    cmd.status().await?;
    Ok(())
}
```
# Path: hyperlane-cli/src/fmt/static.rs
```rust
use crate::*;
pub(crate) static DERIVE_REGEX: LazyLock<Regex> = LazyLock::new(|| {
    regex::Regex::new(r"#\[derive\s*\(([^)]+)\)\]").expect("Invalid regex pattern")
});
```
# Path: hyperlane-cli/src/fmt/test.rs
```rust
use crate::*;
#[test]
fn test_format_path_integration() {
    use std::path::PathBuf;
    let tmp_dir: PathBuf = PathBuf::from("./tmp/test_fmt");
    let _ = std::fs::create_dir_all(&tmp_dir);
    let test_file: PathBuf = tmp_dir.join("test.rs");
    std::fs::write(&test_file, "fn main() {\n    println!(\"hello\");\n}\n").unwrap();
    let rt: tokio::runtime::Runtime = tokio::runtime::Runtime::new().unwrap();
    let result: Result<(), std::io::Error> = rt.block_on(format_path(&tmp_dir));
    assert!(result.is_ok());
}
```
# Path: hyperlane-cli/src/template/mod.rs
```rust
mod r#enum;
mod r#fn;
mod r#impl;
mod r#struct;
#[cfg(test)]
mod test;
pub(crate) use {r#enum::*, r#fn::*, r#struct::*};
```
# Path: hyperlane-cli/src/template/fn.rs
```rust
use crate::*;
fn get_directory_name(template_type: &TemplateType) -> String {
    match template_type {
        TemplateType::Controller => "controller".to_string(),
        TemplateType::Domain => "domain".to_string(),
        TemplateType::Exception => "exception".to_string(),
        TemplateType::Mapper => "mapper".to_string(),
        TemplateType::Model => "model".to_string(),
        TemplateType::Repository => "repository".to_string(),
        TemplateType::Service => "service".to_string(),
        TemplateType::Utils => "utils".to_string(),
        TemplateType::View => "view".to_string(),
    }
}
fn get_model_sub_type_name(sub_type: &ModelSubType) -> String {
    match sub_type {
        ModelSubType::Application => "application".to_string(),
        ModelSubType::Request => "request".to_string(),
        ModelSubType::Response => "response".to_string(),
    }
}
fn ensure_directory(path: &Path) -> Result<(), TemplateError> {
    if !path.exists() {
        create_dir_all(path)?;
    }
    Ok(())
}
fn write_mod_rs(path: &Path, modules: &[&str]) -> Result<(), TemplateError> {
    let mut content: String = String::new();
    for module in modules {
        let mod_name: String = if module.starts_with("r#") {
            module.to_string()
        } else {
            format!("r#{module}")
        };
        content.push_str(&format!("mod {mod_name};\n"));
    }
    content.push('\n');
    let mut pub_use_parts: Vec<String> = Vec::new();
    for module in modules {
        let raw_name: &str = if let Some(stripped) = module.strip_prefix("r#") {
            stripped
        } else {
            module
        };
        let mod_name: String = if module.starts_with("r#") {
            module.to_string()
        } else {
            format!("r#{module}")
        };
        if raw_name == "const" || raw_name == "static" {
            pub_use_parts.push(mod_name);
        } else if raw_name == "enum" || raw_name == "fn" {
            pub_use_parts.push(format!("{mod_name}::*"));
        } else if raw_name == "struct" {
            pub_use_parts.push(mod_name);
        }
    }
    if !pub_use_parts.is_empty() {
        content.push_str("pub use {");
        content.push_str(&pub_use_parts.join(", "));
        content.push_str("};\n");
    }
    content.push('\n');
    content.push_str("use super::*;\n");
    write(path, content)?;
    Ok(())
}
fn write_empty_mod_rs(path: &Path) -> Result<(), TemplateError> {
    write(path, "\n")?;
    Ok(())
}
fn create_controller_template(
    target_dir: &Path,
    _component_name: &str,
) -> Result<(), TemplateError> {
    ensure_directory(target_dir)?;
    let mod_rs: PathBuf = target_dir.join("mod.rs");
    write_mod_rs(&mod_rs, &["fn", "impl", "struct"])?;
    let fn_rs: PathBuf = target_dir.join("fn.rs");
    write(&fn_rs, "use super::*;\n")?;
    let impl_rs: PathBuf = target_dir.join("impl.rs");
    write(&impl_rs, "use super::*;\n")?;
    let struct_rs: PathBuf = target_dir.join("struct.rs");
    write(&struct_rs, "use super::*;\n")?;
    Ok(())
}
fn create_view_template(target_dir: &Path, _component_name: &str) -> Result<(), TemplateError> {
    ensure_directory(target_dir)?;
    let mod_rs: PathBuf = target_dir.join("mod.rs");
    write_mod_rs(&mod_rs, &["fn", "impl", "struct"])?;
    let fn_rs: PathBuf = target_dir.join("fn.rs");
    write(&fn_rs, "use super::*;\n")?;
    let impl_rs: PathBuf = target_dir.join("impl.rs");
    write(&impl_rs, "use super::*;\n")?;
    let struct_rs: PathBuf = target_dir.join("struct.rs");
    write(&struct_rs, "use super::*;\n")?;
    Ok(())
}
fn create_service_template(target_dir: &Path, _component_name: &str) -> Result<(), TemplateError> {
    ensure_directory(target_dir)?;
    let mod_rs: PathBuf = target_dir.join("mod.rs");
    write_mod_rs(&mod_rs, &["impl", "struct"])?;
    let impl_rs: PathBuf = target_dir.join("impl.rs");
    write(&impl_rs, "use super::*;\n")?;
    let struct_rs: PathBuf = target_dir.join("struct.rs");
    write(&struct_rs, "use super::*;\n")?;
    Ok(())
}
fn create_domain_template(target_dir: &Path, _component_name: &str) -> Result<(), TemplateError> {
    ensure_directory(target_dir)?;
    let mod_rs: PathBuf = target_dir.join("mod.rs");
    write_mod_rs(&mod_rs, &["impl", "struct"])?;
    let impl_rs: PathBuf = target_dir.join("impl.rs");
    write(&impl_rs, "use super::*;\n")?;
    let struct_rs: PathBuf = target_dir.join("struct.rs");
    write(&struct_rs, "use super::*;\n")?;
    Ok(())
}
fn create_mapper_template(target_dir: &Path, _component_name: &str) -> Result<(), TemplateError> {
    ensure_directory(target_dir)?;
    let mod_rs: PathBuf = target_dir.join("mod.rs");
    write_mod_rs(
        &mod_rs,
        &["const", "enum", "fn", "impl", "static", "struct"],
    )?;
    let const_rs: PathBuf = target_dir.join("const.rs");
    write(&const_rs, "use super::*;\n")?;
    let enum_rs: PathBuf = target_dir.join("enum.rs");
    write(&enum_rs, "use super::*;\n")?;
    let fn_rs: PathBuf = target_dir.join("fn.rs");
    write(&fn_rs, "use super::*;\n")?;
    let impl_rs: PathBuf = target_dir.join("impl.rs");
    write(&impl_rs, "use super::*;\n")?;
    let static_rs: PathBuf = target_dir.join("static.rs");
    write(&static_rs, "use super::*;\n")?;
    let struct_rs: PathBuf = target_dir.join("struct.rs");
    write(&struct_rs, "use super::*;\n")?;
    Ok(())
}
fn create_utils_template(target_dir: &Path, _component_name: &str) -> Result<(), TemplateError> {
    ensure_directory(target_dir)?;
    let mod_rs: PathBuf = target_dir.join("mod.rs");
    write_mod_rs(&mod_rs, &["fn"])?;
    let fn_rs: PathBuf = target_dir.join("fn.rs");
    write(&fn_rs, "use super::*;\n")?;
    Ok(())
}
fn create_exception_template(
    target_dir: &Path,
    _component_name: &str,
) -> Result<(), TemplateError> {
    ensure_directory(target_dir)?;
    let mod_rs: PathBuf = target_dir.join("mod.rs");
    write_empty_mod_rs(&mod_rs)?;
    Ok(())
}
fn create_repository_template(
    target_dir: &Path,
    _component_name: &str,
) -> Result<(), TemplateError> {
    ensure_directory(target_dir)?;
    let mod_rs: PathBuf = target_dir.join("mod.rs");
    write_mod_rs(&mod_rs, &["impl", "struct"])?;
    let impl_rs: PathBuf = target_dir.join("impl.rs");
    write(&impl_rs, "use super::*;\n")?;
    let struct_rs: PathBuf = target_dir.join("struct.rs");
    write(&struct_rs, "use super::*;\n")?;
    Ok(())
}
fn create_model_template(
    target_dir: &Path,
    _component_name: &str,
    sub_type: &ModelSubType,
) -> Result<(), TemplateError> {
    let sub_type_name: String = get_model_sub_type_name(sub_type);
    let model_dir: PathBuf = target_dir.join(&sub_type_name);
    ensure_directory(&model_dir)?;
    let mod_rs: PathBuf = model_dir.join("mod.rs");
    write_mod_rs(&mod_rs, &["struct"])?;
    let struct_rs: PathBuf = model_dir.join("struct.rs");
    write(&struct_rs, "use super::*;\n")?;
    Ok(())
}
pub(crate) async fn execute_template(
    template_type: TemplateType,
    component_name: &str,
    model_sub_type: Option<ModelSubType>,
) -> Result<(), TemplateError> {
    let config: TemplateConfig =
        TemplateConfig::new(template_type, component_name.to_string(), model_sub_type);
    let base_path: PathBuf = PathBuf::from(&config.base_directory);
    let dir_name: String = get_directory_name(&config.template_type);
    let type_dir: PathBuf = base_path.join(&dir_name);
    let target_dir: PathBuf = type_dir.join(&config.component_name);
    if target_dir.exists() {
        return Err(TemplateError::DirectoryExists(
            target_dir.to_string_lossy().to_string(),
        ));
    }
    ensure_directory(&type_dir)?;
    match config.template_type {
        TemplateType::Controller => {
            create_controller_template(&target_dir, &config.component_name)?
        }
        TemplateType::View => create_view_template(&target_dir, &config.component_name)?,
        TemplateType::Service => create_service_template(&target_dir, &config.component_name)?,
        TemplateType::Domain => create_domain_template(&target_dir, &config.component_name)?,
        TemplateType::Mapper => create_mapper_template(&target_dir, &config.component_name)?,
        TemplateType::Utils => create_utils_template(&target_dir, &config.component_name)?,
        TemplateType::Exception => create_exception_template(&target_dir, &config.component_name)?,
        TemplateType::Repository => {
            create_repository_template(&target_dir, &config.component_name)?
        }
        TemplateType::Model => {
            let sub_type: ModelSubType = config.model_sub_type.ok_or_else(|| {
                TemplateError::InvalidModelSubType("Missing model subtype".to_string())
            })?;
            create_model_template(&target_dir, &config.component_name, &sub_type)?;
        }
    }
    let _: Result<(), std::io::Error> = crate::fmt::format_path(&target_dir).await;
    println!(
        "Created {} '{}' at {}",
        dir_name,
        config.component_name,
        target_dir.display()
    );
    Ok(())
}
```
# Path: hyperlane-cli/src/template/impl.rs
```rust
use crate::*;
impl FromStr for TemplateType {
    type Err = TemplateError;
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "controller" => Ok(Self::Controller),
            "domain" => Ok(Self::Domain),
            "exception" => Ok(Self::Exception),
            "mapper" => Ok(Self::Mapper),
            "model" => Ok(Self::Model),
            "repository" => Ok(Self::Repository),
            "service" => Ok(Self::Service),
            "utils" => Ok(Self::Utils),
            "view" => Ok(Self::View),
            _ => Err(TemplateError::InvalidTemplateType(s.to_string())),
        }
    }
}
impl TemplateConfig {
    pub(crate) fn new(
        template_type: TemplateType,
        component_name: String,
        model_sub_type: Option<ModelSubType>,
    ) -> Self {
        Self {
            template_type,
            component_name,
            model_sub_type,
            base_directory: "./application".to_string(),
        }
    }
}
impl FromStr for ModelSubType {
    type Err = TemplateError;
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "application" => Ok(Self::Application),
            "request" => Ok(Self::Request),
            "response" => Ok(Self::Response),
            _ => Err(TemplateError::InvalidModelSubType(s.to_string())),
        }
    }
}
```
# Path: hyperlane-cli/src/template/struct.rs
```rust
use crate::*;
#[derive(Clone, Debug)]
pub(crate) struct TemplateConfig {
    pub template_type: TemplateType,
    pub component_name: String,
    pub model_sub_type: Option<ModelSubType>,
    pub base_directory: String,
}
```
# Path: hyperlane-cli/src/template/test.rs
```rust
use std::str::FromStr;
use crate::*;
#[test]
fn test_template_config_new() {
    let config: TemplateConfig =
        TemplateConfig::new(TemplateType::Controller, "test".to_string(), None);
    assert_eq!(config.template_type, TemplateType::Controller);
    assert_eq!(config.component_name, "test");
    assert_eq!(config.model_sub_type, None);
    assert_eq!(config.base_directory, "./application");
}
#[test]
fn test_template_config_with_model_sub_type() {
    let config: TemplateConfig = TemplateConfig::new(
        TemplateType::Model,
        "test".to_string(),
        Some(ModelSubType::Request),
    );
    assert_eq!(config.template_type, TemplateType::Model);
    assert_eq!(config.model_sub_type, Some(ModelSubType::Request));
}
#[test]
fn test_template_config_clone() {
    let config: TemplateConfig =
        TemplateConfig::new(TemplateType::Service, "test".to_string(), None);
    let cloned: TemplateConfig = config.clone();
    assert_eq!(cloned.template_type, config.template_type);
    assert_eq!(cloned.component_name, config.component_name);
    assert_eq!(cloned.model_sub_type, config.model_sub_type);
    assert_eq!(cloned.base_directory, config.base_directory);
}
#[test]
fn test_template_config_debug() {
    let config: TemplateConfig =
        TemplateConfig::new(TemplateType::Controller, "test".to_string(), None);
    let debug_str: String = format!("{config:?}");
    assert!(debug_str.contains("Controller"));
    assert!(debug_str.contains("test"));
}
#[test]
fn test_template_error_display() {
    let error1: TemplateError = TemplateError::InvalidModelSubType("bad".to_string());
    assert!(error1.to_string().contains("bad"));
    let error2: TemplateError = TemplateError::DirectoryExists("/path".to_string());
    assert!(error2.to_string().contains("/path"));
}
#[test]
fn test_template_error_from_io() {
    let io_error: std::io::Error = std::io::Error::new(std::io::ErrorKind::NotFound, "test");
    let template_error: TemplateError = TemplateError::from(io_error);
    assert!(template_error.to_string().contains("IO error"));
}
#[test]
fn test_template_error_debug() {
    let error: TemplateError = TemplateError::InvalidModelSubType("test".to_string());
    let debug_str: String = format!("{error:?}");
    assert!(debug_str.contains("InvalidModelSubType"));
}
#[test]
fn test_template_type_equality() {
    assert_eq!(TemplateType::Controller, TemplateType::Controller);
    assert_ne!(TemplateType::Controller, TemplateType::Service);
}
#[test]
fn test_model_sub_type_equality() {
    assert_eq!(ModelSubType::Request, ModelSubType::Request);
    assert_ne!(ModelSubType::Request, ModelSubType::Response);
}
#[test]
fn test_template_type_debug() {
    let ty: TemplateType = TemplateType::Controller;
    let debug_str: String = format!("{ty:?}");
    assert_eq!(debug_str, "Controller");
}
#[test]
fn test_model_sub_type_debug() {
    let ty: ModelSubType = ModelSubType::Application;
    let debug_str: String = format!("{ty:?}");
    assert_eq!(debug_str, "Application");
}
#[test]
fn test_all_template_types() {
    let _ = TemplateType::Controller;
    let _ = TemplateType::Domain;
    let _ = TemplateType::Exception;
    let _ = TemplateType::Mapper;
    let _ = TemplateType::Model;
    let _ = TemplateType::Repository;
    let _ = TemplateType::Service;
    let _ = TemplateType::Utils;
    let _ = TemplateType::View;
}
#[test]
fn test_all_model_sub_types() {
    let _ = ModelSubType::Application;
    let _ = ModelSubType::Request;
    let _ = ModelSubType::Response;
}
#[test]
fn test_parse_template_type_valid() {
    assert_eq!(
        TemplateType::from_str("controller").ok(),
        Some(TemplateType::Controller)
    );
    assert_eq!(
        TemplateType::from_str("Controller").ok(),
        Some(TemplateType::Controller)
    );
    assert_eq!(
        TemplateType::from_str("CONTROLLER").ok(),
        Some(TemplateType::Controller)
    );
    assert_eq!(
        TemplateType::from_str("domain").ok(),
        Some(TemplateType::Domain)
    );
    assert_eq!(
        TemplateType::from_str("exception").ok(),
        Some(TemplateType::Exception)
    );
    assert_eq!(
        TemplateType::from_str("mapper").ok(),
        Some(TemplateType::Mapper)
    );
    assert_eq!(
        TemplateType::from_str("model").ok(),
        Some(TemplateType::Model)
    );
    assert_eq!(
        TemplateType::from_str("repository").ok(),
        Some(TemplateType::Repository)
    );
    assert_eq!(
        TemplateType::from_str("service").ok(),
        Some(TemplateType::Service)
    );
    assert_eq!(
        TemplateType::from_str("utils").ok(),
        Some(TemplateType::Utils)
    );
    assert_eq!(
        TemplateType::from_str("view").ok(),
        Some(TemplateType::View)
    );
}
#[test]
fn test_parse_template_type_invalid() {
    assert_eq!(TemplateType::from_str("invalid").ok(), None);
    assert_eq!(TemplateType::from_str("").ok(), None);
    assert_eq!(TemplateType::from_str("unknown").ok(), None);
}
#[test]
fn test_parse_model_sub_type_valid() {
    assert_eq!(
        ModelSubType::from_str("application").ok(),
        Some(ModelSubType::Application)
    );
    assert_eq!(
        ModelSubType::from_str("Application").ok(),
        Some(ModelSubType::Application)
    );
    assert_eq!(
        ModelSubType::from_str("APPLICATION").ok(),
        Some(ModelSubType::Application)
    );
    assert_eq!(
        ModelSubType::from_str("request").ok(),
        Some(ModelSubType::Request)
    );
    assert_eq!(
        ModelSubType::from_str("response").ok(),
        Some(ModelSubType::Response)
    );
}
#[test]
fn test_parse_model_sub_type_invalid() {
    assert_eq!(ModelSubType::from_str("invalid").ok(), None);
    assert_eq!(ModelSubType::from_str("").ok(), None);
    assert_eq!(ModelSubType::from_str("unknown").ok(), None);
}
```
# Path: hyperlane-cli/src/template/enum.rs
```rust
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) enum TemplateType {
    Controller,
    Domain,
    Exception,
    Mapper,
    Model,
    Repository,
    Service,
    Utils,
    View,
}
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) enum ModelSubType {
    Application,
    Request,
    Response,
}
#[derive(Debug, thiserror::Error)]
pub(crate) enum TemplateError {
    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),
    #[error("Invalid template type: {0}")]
    InvalidTemplateType(String),
    #[error("Invalid model subtype: {0}")]
    InvalidModelSubType(String),
    #[error("Directory '{0}' already exists")]
    DirectoryExists(String),
}
```
# Path: hyperlane-cli/src/new/mod.rs
```rust
mod r#enum;
mod r#fn;
mod r#impl;
mod r#struct;
#[cfg(test)]
mod test;
pub(crate) use {r#enum::*, r#fn::*, r#struct::*};
```
# Path: hyperlane-cli/src/new/fn.rs
```rust
use crate::*;
fn validate_project_name(name: &str) -> Result<(), NewError> {
    if name.is_empty() {
        return Err(NewError::InvalidName(
            "Project name cannot be empty".to_string(),
        ));
    }
    if name.contains('/') || name.contains('\\') || name.contains(':') {
        return Err(NewError::InvalidName(
            "Project name contains invalid characters".to_string(),
        ));
    }
    if name.starts_with('.') || name.starts_with('-') {
        return Err(NewError::InvalidName(
            "Project name cannot start with '.' or '-'".to_string(),
        ));
    }
    Ok(())
}
async fn check_git_available() -> Result<(), NewError> {
    let output: std::process::Output = Command::new("git")
        .arg("--version")
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .output()
        .await
        .map_err(|_| NewError::GitNotFound)?;
    if output.status.success() {
        Ok(())
    } else {
        Err(NewError::GitNotFound)
    }
}
async fn git_clone(config: &NewProjectConfig) -> Result<(), NewError> {
    let project_path: PathBuf = PathBuf::from(&config.project_name);
    if project_path.exists() {
        return Err(NewError::ProjectExists(config.project_name.clone()));
    }
    let output: std::process::Output = Command::new("git")
        .arg("clone")
        .arg(&config.template_url)
        .arg(&config.project_name)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .output()
        .await
        .map_err(NewError::IoError)?;
    if output.status.success() {
        Ok(())
    } else {
        let stderr: String = String::from_utf8_lossy(&output.stderr).to_string();
        Err(NewError::CloneFailed(stderr))
    }
}
pub(crate) async fn execute_new(project_name: &str) -> Result<(), NewError> {
    validate_project_name(project_name)?;
    check_git_available().await?;
    let config: NewProjectConfig = NewProjectConfig::new(project_name.to_string());
    println!(
        "Creating new project '{}' from template...",
        config.project_name
    );
    git_clone(&config).await?;
    println!("Successfully created project '{}'", config.project_name);
    println!("  cd {}", config.project_name);
    println!("  cargo build");
    Ok(())
}
```
# Path: hyperlane-cli/src/new/impl.rs
```rust
use crate::*;
impl NewProjectConfig {
    pub(crate) fn new(project_name: String) -> Self {
        Self {
            project_name,
            template_url: "https://github.com/hyperlane-dev/hyperlane-quick-start".to_string(),
        }
    }
}
```
# Path: hyperlane-cli/src/new/struct.rs
```rust
#[derive(Clone, Debug)]
pub(crate) struct NewProjectConfig {
    pub project_name: String,
    pub template_url: String,
}
```
# Path: hyperlane-cli/src/new/test.rs
```rust
use crate::*;
#[test]
fn test_new_project_config_creation() {
    let config: NewProjectConfig = NewProjectConfig::new("test-project".to_string());
    assert_eq!(config.project_name, "test-project");
    assert_eq!(
        config.template_url,
        "https://github.com/hyperlane-dev/hyperlane-quick-start"
    );
}
#[test]
fn test_new_error_display() {
    let error1: NewError = NewError::GitNotFound;
    assert!(error1.to_string().contains("Git is not installed"));
    let error2: NewError = NewError::ProjectExists("test".to_string());
    assert!(error2.to_string().contains("test"));
    let error3: NewError = NewError::CloneFailed("network error".to_string());
    assert!(error3.to_string().contains("network error"));
    let error4: NewError = NewError::InvalidName("bad name".to_string());
    assert!(error4.to_string().contains("bad name"));
}
#[test]
fn test_new_error_from_io() {
    let io_error: std::io::Error = std::io::Error::new(std::io::ErrorKind::NotFound, "test");
    let new_error: NewError = NewError::from(io_error);
    assert!(new_error.to_string().contains("test"));
}
#[test]
fn test_new_error_debug() {
    let error: NewError = NewError::GitNotFound;
    let debug_str: String = format!("{error:?}");
    assert!(debug_str.contains("GitNotFound"));
}
#[test]
fn test_new_project_config_clone() {
    let config: NewProjectConfig = NewProjectConfig::new("test".to_string());
    let cloned: NewProjectConfig = config.clone();
    assert_eq!(cloned.project_name, config.project_name);
    assert_eq!(cloned.template_url, config.template_url);
}
#[test]
fn test_new_project_config_debug() {
    let config: NewProjectConfig = NewProjectConfig::new("test".to_string());
    let debug_str: String = format!("{config:?}");
    assert!(debug_str.contains("test"));
}
```
# Path: hyperlane-cli/src/new/enum.rs
```rust
#[derive(Debug, thiserror::Error)]
pub(crate) enum NewError {
    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),
    #[error("Git is not installed or not found in PATH")]
    GitNotFound,
    #[error("Project directory '{0}' already exists")]
    ProjectExists(String),
    #[error("Git clone failed: {0}")]
    CloneFailed(String),
    #[error("Invalid project name: {0}")]
    InvalidName(String),
}
```
# Path: hyperlane-cli/src/config/mod.rs
```rust
mod r#fn;
mod r#struct;
#[cfg(test)]
mod test;
pub(crate) use {r#fn::*, r#struct::*};
```
# Path: hyperlane-cli/src/config/fn.rs
```rust
use std::str::FromStr;
use crate::*;
pub(crate) fn parse_args() -> Args {
    let raw_args: Vec<String> = args().collect();
    let mut command: CommandType = CommandType::Help;
    let mut check: bool = false;
    let mut manifest_path: Option<String> = None;
    let mut bump_type: Option<BumpVersionType> = None;
    let mut max_retries: u32 = 3;
    let mut project_name: Option<String> = None;
    let mut template_type: Option<TemplateType> = None;
    let mut model_sub_type: Option<ModelSubType> = None;
    let mut component_name: Option<String> = None;
    let mut i: usize = 1;
    while i < raw_args.len() {
        let arg: &str = raw_args[i].as_str();
        match arg {
            "-h" | "--help" => {
                command = CommandType::Help;
            }
            "-v" | "--version" => {
                command = CommandType::Version;
            }
            "fmt" => {
                if command == CommandType::Help || command == CommandType::Version {
                    command = CommandType::Fmt;
                }
            }
            "watch" => {
                if command == CommandType::Help || command == CommandType::Version {
                    command = CommandType::Watch;
                }
            }
            "bump" => {
                if command == CommandType::Help || command == CommandType::Version {
                    command = CommandType::Bump;
                }
            }
            "publish" => {
                if command == CommandType::Help || command == CommandType::Version {
                    command = CommandType::Publish;
                }
            }
            "new" => {
                if command == CommandType::Help || command == CommandType::Version {
                    command = CommandType::New;
                    i += 1;
                    if i < raw_args.len()
                        && !raw_args[i].starts_with("--")
                        && !raw_args[i].starts_with("-")
                    {
                        project_name = Some(raw_args[i].clone());
                    } else {
                        i -= 1;
                    }
                }
            }
            "template" => {
                if command == CommandType::Help || command == CommandType::Version {
                    command = CommandType::Template;
                    i += 1;
                    if i < raw_args.len()
                        && !raw_args[i].starts_with("--")
                        && !raw_args[i].starts_with("-")
                    {
                        let type_str: &str = &raw_args[i];
                        template_type = TemplateType::from_str(type_str).ok();
                        i += 1;
                        if template_type == Some(TemplateType::Model)
                            && i < raw_args.len()
                            && !raw_args[i].starts_with("--")
                            && !raw_args[i].starts_with("-")
                        {
                            let sub_type_str: &str = &raw_args[i];
                            model_sub_type = ModelSubType::from_str(sub_type_str).ok();
                            i += 1;
                        }
                        if i < raw_args.len()
                            && !raw_args[i].starts_with("--")
                            && !raw_args[i].starts_with("-")
                        {
                            component_name = Some(raw_args[i].clone());
                            i += 1;
                        }
                        i -= 1;
                    }
                }
            }
            "--patch" => {
                bump_type = Some(BumpVersionType::Patch);
            }
            "--minor" => {
                bump_type = Some(BumpVersionType::Minor);
            }
            "--major" => {
                bump_type = Some(BumpVersionType::Major);
            }
            "--release" => {
                bump_type = Some(BumpVersionType::Release);
            }
            "--alpha" => {
                bump_type = Some(BumpVersionType::Alpha);
            }
            "--beta" => {
                bump_type = Some(BumpVersionType::Beta);
            }
            "--rc" => {
                bump_type = Some(BumpVersionType::Rc);
            }
            "--check" => {
                check = true;
            }
            "--manifest-path" => {
                i += 1;
                if i < raw_args.len() {
                    manifest_path = Some(raw_args[i].clone());
                }
            }
            "--max-retries" => {
                i += 1;
                if i < raw_args.len()
                    && let Ok(n) = raw_args[i].parse::<u32>() {
                        max_retries = n;
                    }
            }
            _ => {}
        }
        i += 1;
    }
    Args {
        command,
        check,
        manifest_path,
        bump_type,
        max_retries,
        project_name,
        template_type,
        model_sub_type,
        component_name,
    }
}
```
# Path: hyperlane-cli/src/config/struct.rs
```rust
use crate::*;
#[derive(Clone, Debug)]
pub struct Args {
    pub command: CommandType,
    pub check: bool,
    pub manifest_path: Option<String>,
    pub bump_type: Option<BumpVersionType>,
    pub max_retries: u32,
    pub project_name: Option<String>,
    pub template_type: Option<TemplateType>,
    pub model_sub_type: Option<ModelSubType>,
    pub component_name: Option<String>,
}
```
# Path: hyperlane-cli/src/config/test.rs
```rust
use crate::*;
#[test]
fn test_args_default_values() {
    let args: Args = Args {
        command: CommandType::Help,
        check: false,
        manifest_path: None,
        bump_type: None,
        max_retries: 3,
        project_name: None,
        template_type: None,
        model_sub_type: None,
        component_name: None,
    };
    assert!(!args.check);
    assert_eq!(args.max_retries, 3);
    assert!(args.manifest_path.is_none());
    assert!(args.bump_type.is_none());
    assert!(args.project_name.is_none());
    assert!(args.template_type.is_none());
    assert!(args.model_sub_type.is_none());
    assert!(args.component_name.is_none());
}
#[test]
fn test_args_with_values() {
    let args: Args = Args {
        command: CommandType::Bump,
        check: true,
        manifest_path: Some("./test/Cargo.toml".to_string()),
        bump_type: Some(BumpVersionType::Minor),
        max_retries: 5,
        project_name: Some("test-project".to_string()),
        template_type: Some(TemplateType::Controller),
        model_sub_type: None,
        component_name: Some("test".to_string()),
    };
    assert!(args.check);
    assert_eq!(args.max_retries, 5);
    assert_eq!(args.manifest_path, Some("./test/Cargo.toml".to_string()));
    assert_eq!(args.bump_type, Some(BumpVersionType::Minor));
    assert_eq!(args.project_name, Some("test-project".to_string()));
    assert_eq!(args.template_type, Some(TemplateType::Controller));
    assert_eq!(args.component_name, Some("test".to_string()));
}
#[test]
fn test_args_with_model_subtype() {
    let args: Args = Args {
        command: CommandType::Template,
        check: false,
        manifest_path: None,
        bump_type: None,
        max_retries: 3,
        project_name: None,
        template_type: Some(TemplateType::Model),
        model_sub_type: Some(ModelSubType::Request),
        component_name: Some("user".to_string()),
    };
    assert_eq!(args.template_type, Some(TemplateType::Model));
    assert_eq!(args.model_sub_type, Some(ModelSubType::Request));
    assert_eq!(args.component_name, Some("user".to_string()));
}
#[test]
fn test_command_type_enum_values() {
    let _: CommandType = CommandType::Fmt;
    let _: CommandType = CommandType::Watch;
    let _: CommandType = CommandType::Bump;
    let _: CommandType = CommandType::Publish;
    let _: CommandType = CommandType::New;
    let _: CommandType = CommandType::Template;
    let _: CommandType = CommandType::Help;
    let _: CommandType = CommandType::Version;
}
#[test]
fn test_args_clone() {
    let args: Args = Args {
        command: CommandType::Bump,
        check: true,
        manifest_path: Some("./test/Cargo.toml".to_string()),
        bump_type: Some(BumpVersionType::Minor),
        max_retries: 5,
        project_name: Some("test-project".to_string()),
        template_type: Some(TemplateType::Controller),
        model_sub_type: None,
        component_name: Some("test".to_string()),
    };
    let cloned: Args = args.clone();
    assert_eq!(cloned.check, args.check);
    assert_eq!(cloned.max_retries, args.max_retries);
    assert_eq!(cloned.manifest_path, args.manifest_path);
    assert_eq!(cloned.bump_type, args.bump_type);
    assert_eq!(cloned.project_name, args.project_name);
    assert_eq!(cloned.template_type, args.template_type);
    assert_eq!(cloned.component_name, args.component_name);
}
```
# Path: hyperlane-cli/src/bump/mod.rs
```rust
mod r#enum;
mod r#fn;
mod r#struct;
#[cfg(test)]
mod test;
pub(crate) use {r#enum::*, r#fn::*, r#struct::*};
```
# Path: hyperlane-cli/src/bump/fn.rs
```rust
use crate::*;
fn parse_version(version_str: &str) -> Option<Version> {
    let parts: Vec<&str> = version_str.split('-').collect();
    let version_part: &str = parts.first()?;
    let prerelease: Option<String> = parts.get(1).map(|s: &&str| s.to_string());
    let nums: Vec<&str> = version_part.split('.').collect();
    if nums.len() != 3 {
        return None;
    }
    let major: u64 = nums.first()?.parse().ok()?;
    let minor: u64 = nums.get(1)?.parse().ok()?;
    let patch: u64 = nums.get(2)?.parse().ok()?;
    Some(Version {
        major,
        minor,
        patch,
        prerelease,
    })
}
fn parse_prerelease(prerelease: &str) -> Option<(&str, u64)> {
    let parts: Vec<&str> = prerelease.split('.').collect();
    let pre_type: &str = parts.first()?;
    let number: u64 = parts
        .get(1)
        .and_then(|s: &&str| s.parse().ok())
        .unwrap_or(0);
    Some((pre_type, number))
}
fn get_next_prerelease(current: Option<&String>, target_type: &str) -> String {
    match current {
        Some(pre) => {
            if let Some((pre_type, number)) = parse_prerelease(pre)
                && pre_type == target_type && number > 0 {
                    return format!("{}.{}", target_type, number + 1);
                }
            format!("{target_type}.1")
        }
        None => target_type.to_string(),
    }
}
fn version_to_string(version: &Version) -> String {
    let base: String = format!("{}.{}.{}", version.major, version.minor, version.patch);
    match &version.prerelease {
        Some(pre) => format!("{base}-{pre}"),
        None => base,
    }
}
fn bump_version(version: &Version, bump_type: &BumpVersionType) -> Version {
    match bump_type {
        BumpVersionType::Patch => Version {
            major: version.major,
            minor: version.minor,
            patch: version.patch + 1,
            prerelease: None,
        },
        BumpVersionType::Minor => Version {
            major: version.major,
            minor: version.minor + 1,
            patch: 0,
            prerelease: None,
        },
        BumpVersionType::Major => Version {
            major: version.major + 1,
            minor: 0,
            patch: 0,
            prerelease: None,
        },
        BumpVersionType::Release => Version {
            major: version.major,
            minor: version.minor,
            patch: version.patch,
            prerelease: None,
        },
        BumpVersionType::Alpha => {
            let prerelease: String = get_next_prerelease(version.prerelease.as_ref(), "alpha");
            Version {
                major: version.major,
                minor: version.minor,
                patch: version.patch,
                prerelease: Some(prerelease),
            }
        }
        BumpVersionType::Beta => {
            let prerelease: String = get_next_prerelease(version.prerelease.as_ref(), "beta");
            Version {
                major: version.major,
                minor: version.minor,
                patch: version.patch,
                prerelease: Some(prerelease),
            }
        }
        BumpVersionType::Rc => {
            let prerelease: String = get_next_prerelease(version.prerelease.as_ref(), "rc");
            Version {
                major: version.major,
                minor: version.minor,
                patch: version.patch,
                prerelease: Some(prerelease),
            }
        }
    }
}
fn find_version_position(line: &str) -> Option<(usize, usize)> {
    let trimmed: &str = line.trim();
    if !trimmed.starts_with("version") || !trimmed.contains('=') {
        return None;
    }
    let eq_pos: usize = line.find('=')?;
    let after_eq: &str = &line[eq_pos + 1..];
    let quote_start: usize = after_eq.find('"')?;
    let after_first_quote: &str = &after_eq[quote_start + 1..];
    let quote_end: usize = after_first_quote.find('"')?;
    let version_start: usize = eq_pos + 1 + quote_start + 1;
    let version_end: usize = version_start + quote_end;
    Some((version_start, version_end))
}
pub(crate) fn execute_bump(
    manifest_path: &str,
    bump_type: &BumpVersionType,
) -> Result<String, Box<dyn std::error::Error>> {
    let path: &Path = Path::new(manifest_path);
    let content: String = read_to_string(path)?;
    let mut new_version: Option<String> = None;
    let mut found_version: bool = false;
    let mut updated_content: String = content.clone();
    for line in content.lines() {
        if found_version {
            break;
        }
        if let Some((version_start, version_end)) = find_version_position(line) {
            let version_str: &str = &line[version_start..version_end];
            if let Some(version) = parse_version(version_str) {
                let bumped: Version = bump_version(&version, bump_type);
                let version_string: String = version_to_string(&bumped);
                new_version = Some(version_string.clone());
                let new_line: String = format!(
                    "{}{}{}",
                    &line[..version_start],
                    version_string,
                    &line[version_end..]
                );
                updated_content = updated_content.replacen(line, &new_line, 1);
                found_version = true;
            }
        }
    }
    if !found_version {
        return Err("version field not found in Cargo.toml".into());
    }
    write(path, updated_content)?;
    match new_version {
        Some(v) => Ok(v),
        None => Err("failed to bump version".into()),
    }
}
```
# Path: hyperlane-cli/src/bump/struct.rs
```rust
#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct Version {
    pub major: u64,
    pub minor: u64,
    pub patch: u64,
    pub prerelease: Option<String>,
}
```
# Path: hyperlane-cli/src/bump/test.rs
```rust
use crate::*;
#[test]
fn test_bump_version_type_enum() {
    assert_eq!(BumpVersionType::Patch, BumpVersionType::Patch);
    assert_eq!(BumpVersionType::Minor, BumpVersionType::Minor);
    assert_eq!(BumpVersionType::Major, BumpVersionType::Major);
    assert_eq!(BumpVersionType::Release, BumpVersionType::Release);
    assert_eq!(BumpVersionType::Alpha, BumpVersionType::Alpha);
    assert_eq!(BumpVersionType::Beta, BumpVersionType::Beta);
    assert_eq!(BumpVersionType::Rc, BumpVersionType::Rc);
}
#[test]
fn test_version_struct_creation() {
    let version: Version = Version {
        major: 1,
        minor: 2,
        patch: 3,
        prerelease: Some("alpha.1".to_string()),
    };
    assert_eq!(version.major, 1);
    assert_eq!(version.minor, 2);
    assert_eq!(version.patch, 3);
    assert_eq!(version.prerelease, Some("alpha.1".to_string()));
}
#[test]
fn test_version_clone() {
    let version: Version = Version {
        major: 1,
        minor: 2,
        patch: 3,
        prerelease: Some("beta".to_string()),
    };
    let cloned: Version = version.clone();
    assert_eq!(cloned.major, version.major);
    assert_eq!(cloned.minor, version.minor);
    assert_eq!(cloned.patch, version.patch);
    assert_eq!(cloned.prerelease, version.prerelease);
}
#[test]
fn test_execute_bump_integration() {
    use std::fs::write;
    use std::path::PathBuf;
    let tmp_dir: PathBuf = PathBuf::from("./tmp/test_bump");
    let _ = std::fs::create_dir_all(&tmp_dir);
    let manifest_path: PathBuf = tmp_dir.join("Cargo.toml");
    let content: &str = r#"[package]
name = "test-package"
version = "0.1.0"
edition = "2024"
"#;
    write(&manifest_path, content).unwrap();
    let result: Result<String, Box<dyn std::error::Error>> =
        execute_bump(manifest_path.to_str().unwrap(), &BumpVersionType::Patch);
    assert!(result.is_ok());
    assert_eq!(result.unwrap(), "0.1.1");
    let updated_content: String = std::fs::read_to_string(&manifest_path).unwrap();
    assert!(updated_content.contains("version = \"0.1.1\""));
}
#[test]
fn test_execute_bump_minor() {
    use std::fs::write;
    use std::path::PathBuf;
    let tmp_dir: PathBuf = PathBuf::from("./tmp/test_bump_minor");
    let _ = std::fs::create_dir_all(&tmp_dir);
    let manifest_path: PathBuf = tmp_dir.join("Cargo.toml");
    let content: &str = r#"[package]
name = "test-package"
version = "0.1.0"
edition = "2024"
"#;
    write(&manifest_path, content).unwrap();
    let result: Result<String, Box<dyn std::error::Error>> =
        execute_bump(manifest_path.to_str().unwrap(), &BumpVersionType::Minor);
    assert!(result.is_ok());
    assert_eq!(result.unwrap(), "0.2.0");
}
#[test]
fn test_execute_bump_major() {
    use std::fs::write;
    use std::path::PathBuf;
    let tmp_dir: PathBuf = PathBuf::from("./tmp/test_bump_major");
    let _ = std::fs::create_dir_all(&tmp_dir);
    let manifest_path: PathBuf = tmp_dir.join("Cargo.toml");
    let content: &str = r#"[package]
name = "test-package"
version = "0.1.0"
edition = "2024"
"#;
    write(&manifest_path, content).unwrap();
    let result: Result<String, Box<dyn std::error::Error>> =
        execute_bump(manifest_path.to_str().unwrap(), &BumpVersionType::Major);
    assert!(result.is_ok());
    assert_eq!(result.unwrap(), "1.0.0");
}
#[test]
fn test_execute_bump_alpha() {
    use std::fs::write;
    use std::path::PathBuf;
    let tmp_dir: PathBuf = PathBuf::from("./tmp/test_bump_alpha");
    let _ = std::fs::create_dir_all(&tmp_dir);
    let manifest_path: PathBuf = tmp_dir.join("Cargo.toml");
    let content: &str = r#"[package]
name = "test-package"
version = "0.1.0"
edition = "2024"
"#;
    write(&manifest_path, content).unwrap();
    let result: Result<String, Box<dyn std::error::Error>> =
        execute_bump(manifest_path.to_str().unwrap(), &BumpVersionType::Alpha);
    assert!(result.is_ok());
    assert_eq!(result.unwrap(), "0.1.0-alpha");
}
#[test]
fn test_execute_bump_beta() {
    use std::fs::write;
    use std::path::PathBuf;
    let tmp_dir: PathBuf = PathBuf::from("./tmp/test_bump_beta");
    let _ = std::fs::create_dir_all(&tmp_dir);
    let manifest_path: PathBuf = tmp_dir.join("Cargo.toml");
    let content: &str = r#"[package]
name = "test-package"
version = "0.1.0-alpha.2"
edition = "2024"
"#;
    write(&manifest_path, content).unwrap();
    let result: Result<String, Box<dyn std::error::Error>> =
        execute_bump(manifest_path.to_str().unwrap(), &BumpVersionType::Beta);
    assert!(result.is_ok());
    assert_eq!(result.unwrap(), "0.1.0-beta.1");
}
#[test]
fn test_execute_bump_rc() {
    use std::fs::write;
    use std::path::PathBuf;
    let tmp_dir: PathBuf = PathBuf::from("./tmp/test_bump_rc");
    let _ = std::fs::create_dir_all(&tmp_dir);
    let manifest_path: PathBuf = tmp_dir.join("Cargo.toml");
    let content: &str = r#"[package]
name = "test-package"
version = "0.1.0-beta.1"
edition = "2024"
"#;
    write(&manifest_path, content).unwrap();
    let result: Result<String, Box<dyn std::error::Error>> =
        execute_bump(manifest_path.to_str().unwrap(), &BumpVersionType::Rc);
    assert!(result.is_ok());
    assert_eq!(result.unwrap(), "0.1.0-rc.1");
}
#[test]
fn test_execute_bump_release() {
    use std::fs::write;
    use std::path::PathBuf;
    let tmp_dir: PathBuf = PathBuf::from("./tmp/test_bump_release");
    let _ = std::fs::create_dir_all(&tmp_dir);
    let manifest_path: PathBuf = tmp_dir.join("Cargo.toml");
    let content: &str = r#"[package]
name = "test-package"
version = "0.1.0-alpha"
edition = "2024"
"#;
    write(&manifest_path, content).unwrap();
    let result: Result<String, Box<dyn std::error::Error>> =
        execute_bump(manifest_path.to_str().unwrap(), &BumpVersionType::Release);
    assert!(result.is_ok());
    assert_eq!(result.unwrap(), "0.1.0");
}
#[test]
fn test_execute_bump_no_version_field() {
    use std::fs::write;
    use std::path::PathBuf;
    let tmp_dir: PathBuf = PathBuf::from("./tmp/test_bump_no_version");
    let _ = std::fs::create_dir_all(&tmp_dir);
    let manifest_path: PathBuf = tmp_dir.join("Cargo.toml");
    let content: &str = r#"[package]
name = "test-package"
edition = "2024"
"#;
    write(&manifest_path, content).unwrap();
    let result: Result<String, Box<dyn std::error::Error>> =
        execute_bump(manifest_path.to_str().unwrap(), &BumpVersionType::Patch);
    assert!(result.is_err());
}
```
# Path: hyperlane-cli/src/bump/enum.rs
```rust
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) enum BumpVersionType {
    Patch,
    Minor,
    Major,
    Release,
    Alpha,
    Beta,
    Rc,
}
```
# Path: hyperlane-cli/src/publish/mod.rs
```rust
mod r#enum;
mod r#fn;
mod r#struct;
#[cfg(test)]
mod test;
pub(crate) use {r#enum::*, r#fn::*, r#struct::*};
```
# Path: hyperlane-cli/src/publish/fn.rs
```rust
use crate::*;
fn discover_packages(workspace_root: &Path) -> Result<Vec<Package>, PublishError> {
    let content: String = read_to_string(workspace_root)?;
    let doc: toml::Value =
        toml::from_str(&content).map_err(|_| PublishError::ManifestParseError)?;
    let mut packages: Vec<Package> = Vec::new();
    if let Some(workspace) = doc.get("workspace")
        && let Some(members) = workspace.get("members").and_then(|m| m.as_array()) {
            for member in members {
                if let Some(pattern) = member.as_str() {
                    let base_path: &Path = workspace_root.parent().unwrap_or(workspace_root);
                    expand_pattern(base_path, pattern, &mut packages)?;
                }
            }
        }
    if packages.is_empty() {
        let package: Package = read_single_package(workspace_root)?;
        packages.push(package);
    }
    Ok(packages)
}
fn expand_pattern(
    base_path: &Path,
    pattern: &str,
    packages: &mut Vec<Package>,
) -> Result<(), PublishError> {
    if pattern.contains('*') {
        let parent: &Path = Path::new(pattern).parent().unwrap_or(Path::new("."));
        let full_parent: PathBuf = base_path.join(parent);
        if full_parent.is_dir() {
            for entry in std::fs::read_dir(&full_parent)? {
                let entry: std::fs::DirEntry = entry?;
                let path: PathBuf = entry.path();
                if path.is_dir() {
                    let cargo_toml: PathBuf = path.join("Cargo.toml");
                    if cargo_toml.exists() {
                        let package: Package = read_package_manifest(&cargo_toml)?;
                        packages.push(package);
                    }
                }
            }
        }
    } else {
        let cargo_toml: PathBuf = base_path.join(pattern).join("Cargo.toml");
        if cargo_toml.exists() {
            let package: Package = read_package_manifest(&cargo_toml)?;
            packages.push(package);
        }
    }
    Ok(())
}
fn read_single_package(manifest_path: &Path) -> Result<Package, PublishError> {
    read_package_manifest(manifest_path)
}
fn read_package_manifest(manifest_path: &Path) -> Result<Package, PublishError> {
    let content: String = read_to_string(manifest_path)?;
    let doc: toml::Value =
        toml::from_str(&content).map_err(|_| PublishError::ManifestParseError)?;
    let package_table: &toml::Value = doc.get("package").ok_or(PublishError::ManifestParseError)?;
    let name: String = package_table
        .get("name")
        .and_then(|n: &toml::Value| n.as_str())
        .ok_or(PublishError::ManifestParseError)?
        .to_string();
    let version: String = package_table
        .get("version")
        .and_then(|v: &toml::Value| v.as_str())
        .ok_or(PublishError::ManifestParseError)?
        .to_string();
    let path: PathBuf = manifest_path
        .parent()
        .filter(|p: &&Path| !p.as_os_str().is_empty())
        .map_or_else(|| PathBuf::from("."), |p: &Path| p.to_path_buf());
    let local_dependencies: Vec<String> = extract_local_dependencies(&doc, manifest_path)?;
    Ok(Package {
        name,
        version,
        path,
        local_dependencies,
    })
}
fn extract_local_dependencies(
    doc: &toml::Value,
    _manifest_path: &Path,
) -> Result<Vec<String>, PublishError> {
    let mut deps: Vec<String> = Vec::new();
    let dep_sections: [&str; 3] = ["dependencies", "dev-dependencies", "build-dependencies"];
    for section in &dep_sections {
        if let Some(table) = doc.get(section).and_then(|s| s.as_table()) {
            for (dep_name, dep_value) in table {
                let is_local: bool = match dep_value {
                    toml::Value::Table(t) => {
                        t.get("path").is_some()
                            || t.get("workspace")
                                .and_then(|w| w.as_bool())
                                .unwrap_or(false)
                    }
                    _ => false,
                };
                if is_local {
                    deps.push(dep_name.clone());
                }
            }
        }
    }
    Ok(deps)
}
fn topological_sort(packages: &[Package]) -> Result<Vec<Package>, PublishError> {
    let mut in_degree: HashMap<String, usize> = HashMap::new();
    let mut graph: HashMap<String, Vec<String>> = HashMap::new();
    let package_map: HashMap<String, Package> = packages
        .iter()
        .map(|p| (p.name.clone(), p.clone()))
        .collect();
    for package in packages {
        in_degree.entry(package.name.clone()).or_insert(0);
        for dep in &package.local_dependencies {
            if package_map.contains_key(dep) {
                graph
                    .entry(dep.clone())
                    .or_default()
                    .push(package.name.clone());
                *in_degree.entry(package.name.clone()).or_insert(0) += 1;
            }
        }
    }
    let mut queue: VecDeque<String> = VecDeque::new();
    for (name, degree) in &in_degree {
        if *degree == 0 {
            queue.push_back(name.clone());
        }
    }
    let mut result: Vec<Package> = Vec::new();
    while let Some(name) = queue.pop_front() {
        if let Some(package) = package_map.get(&name) {
            result.push(package.clone());
        }
        if let Some(dependents) = graph.get(&name) {
            for dependent in dependents {
                if let Some(degree) = in_degree.get_mut(dependent) {
                    *degree -= 1;
                    if *degree == 0 {
                        queue.push_back(dependent.clone());
                    }
                }
            }
        }
    }
    if result.len() != packages.len() {
        return Err(PublishError::CircularDependency);
    }
    Ok(result)
}
async fn publish_package_with_retry(package: &Package, max_retries: u32) -> PublishResult {
    let mut attempt: u32 = 0;
    let mut last_error: Option<String> = None;
    while attempt <= max_retries {
        match publish_single_package(package).await {
            Ok(()) => {
                return PublishResult {
                    package_name: package.name.clone(),
                    success: true,
                    error: None,
                    retries: attempt,
                };
            }
            Err(error) => {
                last_error = Some(error.to_string());
                attempt += 1;
                if attempt <= max_retries {
                    tokio::time::sleep(tokio::time::Duration::from_secs(2_u64.pow(attempt))).await;
                }
            }
        }
    }
    PublishResult {
        package_name: package.name.clone(),
        success: false,
        error: last_error,
        retries: attempt - 1,
    }
}
async fn publish_single_package(package: &Package) -> Result<(), Box<dyn std::error::Error>> {
    let output: std::process::Output = Command::new("cargo")
        .arg("publish")
        .arg("--allow-dirty")
        .current_dir(&package.path)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .output()
        .await?;
    if output.status.success() {
        Ok(())
    } else {
        let stderr: String = String::from_utf8_lossy(&output.stderr).to_string();
        Err(stderr.into())
    }
}
pub(crate) async fn execute_publish(
    manifest_path: &str,
    max_retries: u32,
) -> Result<Vec<PublishResult>, PublishError> {
    let path: &Path = Path::new(manifest_path);
    let packages: Vec<Package> = discover_packages(path)?;
    if packages.is_empty() {
        return Ok(Vec::new());
    }
    let sorted_packages: Vec<Package> = topological_sort(&packages)?;
    let mut results: Vec<PublishResult> = Vec::new();
    for package in sorted_packages {
        println!("Publishing {} v{}...", package.name, package.version);
        let result: PublishResult = publish_package_with_retry(&package, max_retries).await;
        if result.success {
            if result.retries == 0 {
                println!("Successfully published {}", result.package_name,);
            } else {
                println!(
                    "Successfully published {} (retried {} times)",
                    result.package_name, result.retries
                );
            }
        } else if let Some(error) = &result.error {
            eprintln!("Failed to publish {}: {error}", result.package_name);
        } else {
            eprintln!("Failed to publish {}", result.package_name);
        }
        results.push(result);
    }
    Ok(results)
}
```
# Path: hyperlane-cli/src/publish/struct.rs
```rust
#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct Package {
    pub name: String,
    pub version: String,
    pub path: std::path::PathBuf,
    pub local_dependencies: Vec<String>,
}
#[derive(Clone, Debug)]
pub(crate) struct PublishResult {
    pub package_name: String,
    pub success: bool,
    pub error: Option<String>,
    pub retries: u32,
}
```
# Path: hyperlane-cli/src/publish/test.rs
```rust
use crate::*;
#[test]
fn test_package_creation() {
    let package: Package = Package {
        name: "test-package".to_string(),
        version: "0.1.0".to_string(),
        path: std::path::PathBuf::from("."),
        local_dependencies: vec![],
    };
    assert_eq!(package.name, "test-package");
    assert_eq!(package.version, "0.1.0");
    assert!(package.local_dependencies.is_empty());
}
#[test]
fn test_package_clone() {
    let package: Package = Package {
        name: "test-package".to_string(),
        version: "0.1.0".to_string(),
        path: std::path::PathBuf::from("."),
        local_dependencies: vec!["dep1".to_string()],
    };
    let cloned: Package = package.clone();
    assert_eq!(cloned.name, package.name);
    assert_eq!(cloned.version, package.version);
    assert_eq!(cloned.local_dependencies.len(), 1);
}
#[test]
fn test_package_equality() {
    let package1: Package = Package {
        name: "test".to_string(),
        version: "0.1.0".to_string(),
        path: std::path::PathBuf::from("."),
        local_dependencies: vec![],
    };
    let package2: Package = Package {
        name: "test".to_string(),
        version: "0.1.0".to_string(),
        path: std::path::PathBuf::from("."),
        local_dependencies: vec![],
    };
    assert_eq!(package1, package2);
}
#[test]
fn test_publish_result_success() {
    let result: PublishResult = PublishResult {
        package_name: "test".to_string(),
        success: true,
        error: None,
        retries: 0,
    };
    assert_eq!(result.package_name, "test");
    assert!(result.success);
    assert!(result.error.is_none());
    assert_eq!(result.retries, 0);
}
#[test]
fn test_publish_result_failure() {
    let result: PublishResult = PublishResult {
        package_name: "test".to_string(),
        success: false,
        error: Some("network error".to_string()),
        retries: 3,
    };
    assert!(!result.success);
    assert_eq!(result.error, Some("network error".to_string()));
    assert_eq!(result.retries, 3);
}
#[test]
fn test_publish_result_clone() {
    let result: PublishResult = PublishResult {
        package_name: "test".to_string(),
        success: true,
        error: None,
        retries: 0,
    };
    let cloned: PublishResult = result.clone();
    assert_eq!(cloned.package_name, result.package_name);
    assert_eq!(cloned.success, result.success);
    assert_eq!(cloned.error, result.error);
    assert_eq!(cloned.retries, result.retries);
}
#[test]
fn test_publish_error_display() {
    let error1: PublishError = PublishError::ManifestParseError;
    assert!(error1.to_string().contains("Failed to parse"));
    let error2: PublishError = PublishError::CircularDependency;
    assert!(error2.to_string().contains("Circular dependency"));
}
#[test]
fn test_publish_error_from_io() {
    let io_error: std::io::Error = std::io::Error::new(std::io::ErrorKind::NotFound, "test");
    let publish_error: PublishError = PublishError::from(io_error);
    assert!(publish_error.to_string().contains("IO error"));
}
```
# Path: hyperlane-cli/src/publish/enum.rs
```rust
#[derive(Debug, thiserror::Error)]
pub(crate) enum PublishError {
    #[error("Failed to parse Cargo.toml")]
    ManifestParseError,
    #[error("Circular dependency detected")]
    CircularDependency,
    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),
}
```
# Path: hyperlane-cli/src/help/mod.rs
```rust
mod r#fn;
pub(crate) use r#fn::*;
```
# Path: hyperlane-cli/src/help/fn.rs
```rust
pub(crate) fn print_help() {
    println!("hyperlane-cli [COMMAND] [OPTIONS]");
    println!();
    println!("Commands:");
    println!("  bump      Bump version in Cargo.toml");
    println!("  fmt       Format Rust code using cargo fmt");
    println!("  watch     Watch files and run cargo run using cargo-watch");
    println!("  publish   Publish packages in monorepo with topological ordering");
    println!("  new       Create a new project from template");
    println!(
        "  template  Generate template components (controller|domain|exception|mapper|model|repository|service|utils|view)"
    );
    println!("  -h, --help      Print this help message");
    println!("  -v, --version   Print version information");
    println!();
    println!("New Options:");
    println!("  <PROJECT_NAME>  Name of the project to create");
    println!();
    println!("Bump Options:");
    println!("  --patch         Bump patch version (0.1.0 -> 0.1.1) [default]");
    println!("  --minor         Bump minor version (0.1.0 -> 0.2.0)");
    println!("  --major         Bump major version (0.1.0 -> 1.0.0)");
    println!(
        "  --alpha         Add or bump alpha version (0.1.0 -> 0.1.0-alpha, 0.1.0-alpha -> 0.1.0-alpha.1)"
    );
    println!(
        "  --beta          Add or bump beta version (0.1.0 -> 0.1.0-beta, 0.1.0-alpha.2 -> 0.1.0-beta.1)"
    );
    println!(
        "  --rc            Add or bump rc version (0.1.0 -> 0.1.0-rc, 0.1.0-beta.1 -> 0.1.0-rc.1)"
    );
    println!("  --release       Remove pre-release identifier (0.1.0-alpha -> 0.1.0)");
    println!("  --manifest-path <PATH>  Path to Cargo.toml [default: Cargo.toml]");
    println!();
    println!("Fmt Options:");
    println!("  --check         Check formatting without making changes");
    println!("  --manifest-path <PATH>  Path to Cargo.toml");
    println!();
    println!("Publish Options:");
    println!("  --manifest-path <PATH>  Path to workspace Cargo.toml [default: Cargo.toml]");
    println!("  --max-retries <N>       Maximum retry attempts per package [default: 3]");
}
```
# Path: hyperlane-cli/src/watch/mod.rs
```rust
mod r#fn;
pub(crate) use r#fn::*;
```
# Path: hyperlane-cli/src/watch/fn.rs
```rust
use crate::*;
async fn is_cargo_watch_installed() -> bool {
    Command::new("cargo-watch")
        .arg("--version")
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status()
        .await
        .is_ok_and(|status: ExitStatus| status.success())
}
async fn install_cargo_watch() -> Result<(), std::io::Error> {
    println!("cargo-watch not found, installing...");
    let mut cmd: Command = Command::new("cargo");
    cmd.arg("install").arg("cargo-watch");
    cmd.stdout(Stdio::inherit()).stderr(Stdio::inherit());
    let status: ExitStatus = cmd.status().await?;
    if !status.success() {
        return Err(std::io::Error::other("failed to install cargo-watch"));
    }
    Ok(())
}
pub(crate) async fn execute_watch() -> Result<(), std::io::Error> {
    if !is_cargo_watch_installed().await {
        install_cargo_watch().await?;
    }
    let mut cmd: Command = Command::new("cargo-watch");
    cmd.arg("--clear")
        .arg("--skip-local-deps")
        .arg("-q")
        .arg("-x")
        .arg("run");
    cmd.stdout(Stdio::inherit()).stderr(Stdio::inherit());
    let status: ExitStatus = cmd.status().await?;
    if !status.success() {
        return Err(std::io::Error::other("cargo-watch failed"));
    }
    Ok(())
}
```
# Path: hyperlane-cli/src/command/mod.rs
```rust
mod r#enum;
pub(crate) use r#enum::*;
```
# Path: hyperlane-cli/src/command/enum.rs
```rust
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) enum CommandType {
    Fmt,
    Watch,
    Bump,
    Publish,
    New,
    Template,
    Help,
    Version,
}
```
# Path: hyperlane-cli/src/version/mod.rs
```rust
mod r#fn;
#[cfg(test)]
mod test;
pub(crate) use r#fn::*;
```
# Path: hyperlane-cli/src/version/fn.rs
```rust
pub(crate) fn print_version() {
    println!("hyperlane-cli {}", env!("CARGO_PKG_VERSION"));
}
```
# Path: hyperlane-cli/src/version/test.rs
```rust
use crate::*;
#[test]
fn test_print_version_runs() {
    print_version();
}
```
# Path: hyperlane-log/README.md
## hyperlane-log
[Official Documentation](https://docs.ltpp.vip/hyperlane-log/)
[Api Docs](https://docs.rs/hyperlane-log/latest/)
> A Rust logging library that supports both asynchronous and synchronous logging. It provides multiple log levels, such as error, info, and debug. Users can define custom log handling methods and configure log file paths. The library supports log rotation, automatically creating a new log file when the current file reaches the specified size limit. It allows flexible logging configurations, making it suitable for both high-performance asynchronous applications and traditional synchronous logging scenarios. The asynchronous mode utilizes Tokio's async channels for efficient log buffering, while the synchronous mode writes logs directly to the file system.
## Installation
To use this crate, you can run cmd:
```shell
cargo add hyperlane-log
```
## Log Storage Location Description
> Three directories will be created under the user-specified directory: one for error logs, one for info logs, and one for debug logs. Each of these directories will contain a subdirectory named by the date, and the log files within these subdirectories will be named in the format `timestamp.index.log`.
## Contact
# Path: hyperlane-log/src/const.rs
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
# Path: hyperlane-log/src/lib.rs
```rust
mod r#const;
mod r#fn;
mod r#impl;
mod r#struct;
#[cfg(test)]
mod test;
mod r#trait;
pub use {r#const::*, r#fn::*, r#struct::*, r#trait::*};
use std::fs::read_dir;
use {file_operation::*, hyperlane_time::*};
```
# Path: hyperlane-log/src/trait.rs
```rust
pub trait FileLoggerFuncTrait<T: AsRef<str>>: Fn(T) -> String + Send + Sync {}
```
# Path: hyperlane-log/src/fn.rs
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
# Path: hyperlane-log/src/impl.rs
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
            trace_dir: TRACE_DIR.to_owned(),
            debug_dir: DEBUG_DIR.to_owned(),
            info_dir: INFO_DIR.to_owned(),
            warn_dir: WARN_DIR.to_owned(),
            error_dir: ERROR_DIR.to_owned(),
        }
    }
}
impl FileLogger {
    #[inline(always)]
    pub fn new<P: AsRef<str>>(path: P, limit_file_size: usize) -> Self {
        Self {
            path: path.as_ref().to_owned(),
            limit_file_size,
            trace_dir: TRACE_DIR.to_owned(),
            debug_dir: DEBUG_DIR.to_owned(),
            info_dir: INFO_DIR.to_owned(),
            warn_dir: WARN_DIR.to_owned(),
            error_dir: ERROR_DIR.to_owned(),
        }
    }
    #[inline(always)]
    pub fn get_path(&self) -> &String {
        &self.path
    }
    #[inline(always)]
    pub fn get_limit_file_size(&self) -> &usize {
        &self.limit_file_size
    }
    #[inline(always)]
    pub fn get_trace_dir(&self) -> &String {
        &self.trace_dir
    }
    #[inline(always)]
    pub fn get_debug_dir(&self) -> &String {
        &self.debug_dir
    }
    #[inline(always)]
    pub fn get_info_dir(&self) -> &String {
        &self.info_dir
    }
    #[inline(always)]
    pub fn get_warn_dir(&self) -> &String {
        &self.warn_dir
    }
    #[inline(always)]
    pub fn get_error_dir(&self) -> &String {
        &self.error_dir
    }
    #[inline(always)]
    pub fn set_path<P: AsRef<str>>(&mut self, path: P) -> &mut Self {
        self.path = path.as_ref().to_owned();
        self
    }
    #[inline(always)]
    pub fn set_limit_file_size(&mut self, limit_file_size: usize) -> &mut Self {
        self.limit_file_size = limit_file_size;
        self
    }
    #[inline(always)]
    pub fn set_trace_dir<P: AsRef<str>>(&mut self, dir: P) -> &mut Self {
        self.trace_dir = dir.as_ref().to_owned();
        self
    }
    #[inline(always)]
    pub fn set_debug_dir<P: AsRef<str>>(&mut self, dir: P) -> &mut Self {
        self.debug_dir = dir.as_ref().to_owned();
        self
    }
    #[inline(always)]
    pub fn set_info_dir<P: AsRef<str>>(&mut self, dir: P) -> &mut Self {
        self.info_dir = dir.as_ref().to_owned();
        self
    }
    #[inline(always)]
    pub fn set_warn_dir<P: AsRef<str>>(&mut self, dir: P) -> &mut Self {
        self.warn_dir = dir.as_ref().to_owned();
        self
    }
    #[inline(always)]
    pub fn set_error_dir<P: AsRef<str>>(&mut self, dir: P) -> &mut Self {
        self.error_dir = dir.as_ref().to_owned();
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
        self.write_sync(data, func, &self.trace_dir)
    }
    pub async fn async_trace<T, L>(&self, data: T, func: L) -> &Self
    where
        T: AsRef<str>,
        L: FileLoggerFuncTrait<T>,
    {
        self.write_async(data, func, &self.trace_dir).await
    }
    pub fn debug<T, L>(&self, data: T, func: L) -> &Self
    where
        T: AsRef<str>,
        L: FileLoggerFuncTrait<T>,
    {
        self.write_sync(data, func, &self.debug_dir)
    }
    pub async fn async_debug<T, L>(&self, data: T, func: L) -> &Self
    where
        T: AsRef<str>,
        L: FileLoggerFuncTrait<T>,
    {
        self.write_async(data, func, &self.debug_dir).await
    }
    pub fn info<T, L>(&self, data: T, func: L) -> &Self
    where
        T: AsRef<str>,
        L: FileLoggerFuncTrait<T>,
    {
        self.write_sync(data, func, &self.info_dir)
    }
    pub async fn async_info<T, L>(&self, data: T, func: L) -> &Self
    where
        T: AsRef<str>,
        L: FileLoggerFuncTrait<T>,
    {
        self.write_async(data, func, &self.info_dir).await
    }
    pub fn warn<T, L>(&self, data: T, func: L) -> &Self
    where
        T: AsRef<str>,
        L: FileLoggerFuncTrait<T>,
    {
        self.write_sync(data, func, &self.warn_dir)
    }
    pub async fn async_warn<T, L>(&self, data: T, func: L) -> &Self
    where
        T: AsRef<str>,
        L: FileLoggerFuncTrait<T>,
    {
        self.write_async(data, func, &self.warn_dir).await
    }
    pub fn error<T, L>(&self, data: T, func: L) -> &Self
    where
        T: AsRef<str>,
        L: FileLoggerFuncTrait<T>,
    {
        self.write_sync(data, func, &self.error_dir)
    }
    pub async fn async_error<T, L>(&self, data: T, func: L) -> &Self
    where
        T: AsRef<str>,
        L: FileLoggerFuncTrait<T>,
    {
        self.write_async(data, func, &self.error_dir).await
    }
}
```
# Path: hyperlane-log/src/struct.rs
```rust
#[derive(Clone)]
pub struct FileLogger {
    pub(super) path: String,
    pub(super) limit_file_size: usize,
    pub(super) trace_dir: String,
    pub(super) debug_dir: String,
    pub(super) info_dir: String,
    pub(super) warn_dir: String,
    pub(super) error_dir: String,
}
```
# Path: hyperlane-log/src/test.rs
```rust
use crate::*;
#[tokio::test]
async fn test() {
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
#[tokio::test]
async fn test_more_log_first() {
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
#[tokio::test]
async fn test_more_log_second() {
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
#[tokio::test]
async fn test_set_log_level_dirs() {
    let mut log: FileLogger = FileLogger::new("./test_logs", 1_024_000);
    log.set_trace_dir("custom_trace")
        .set_debug_dir("custom_debug")
        .set_info_dir("custom_info")
        .set_warn_dir("custom_warn")
        .set_error_dir("custom_error");
    assert_eq!(log.get_trace_dir(), "custom_trace");
    assert_eq!(log.get_debug_dir(), "custom_debug");
    assert_eq!(log.get_info_dir(), "custom_info");
    assert_eq!(log.get_warn_dir(), "custom_warn");
    assert_eq!(log.get_error_dir(), "custom_error");
    log.trace("test trace message", common_log);
    log.debug("test debug message", common_log);
    log.info("test info message", common_log);
    log.warn("test warn message", common_log);
    log.error("test error message", common_log);
    log.async_trace("async test trace message", common_log)
        .await;
    log.async_debug("async test debug message", common_log)
        .await;
    log.async_info("async test info message", common_log).await;
    log.async_warn("async test warn message", common_log).await;
    log.async_error("async test error message", common_log)
        .await;
}
#[tokio::test]
async fn test_log_level_dir_constants() {
    let log: FileLogger = FileLogger::default();
    assert_eq!(log.get_trace_dir(), TRACE_DIR);
    assert_eq!(log.get_debug_dir(), DEBUG_DIR);
    assert_eq!(log.get_info_dir(), INFO_DIR);
    assert_eq!(log.get_warn_dir(), WARN_DIR);
    assert_eq!(log.get_error_dir(), ERROR_DIR);
}
#[tokio::test]
async fn test_log_level_dir_method_chaining() {
    let mut log: FileLogger = FileLogger::new("./logs", 512_000);
    let log_ref: &mut FileLogger = log
        .set_trace_dir("chain_trace")
        .set_debug_dir("chain_debug")
        .set_info_dir("chain_info")
        .set_warn_dir("chain_warn")
        .set_error_dir("chain_error");
    assert_eq!(log_ref.get_trace_dir(), "chain_trace");
    assert_eq!(log_ref.get_debug_dir(), "chain_debug");
    assert_eq!(log_ref.get_info_dir(), "chain_info");
    assert_eq!(log_ref.get_warn_dir(), "chain_warn");
    assert_eq!(log_ref.get_error_dir(), "chain_error");
}
#[tokio::test]
async fn test_log_level_dirs_with_special_characters() {
    let mut log: FileLogger = FileLogger::new("./logs/special", 1_024_000);
    log.set_trace_dir("trace-2024")
        .set_debug_dir("debug_test")
        .set_info_dir("info.logs")
        .set_warn_dir("warn/logs")
        .set_error_dir("error_logs");
    log.trace("special trace message", common_log);
    log.async_trace("async special trace message", common_log)
        .await;
    log.debug("special debug message", common_log);
    log.async_debug("async special debug message", common_log)
        .await;
    log.info("special info message", common_log);
    log.async_info("async special info message", common_log)
        .await;
    log.warn("special warn message", common_log);
    log.async_warn("async special warn message", common_log)
        .await;
    log.error("special error message", common_log);
    log.async_error("async special error message", common_log)
        .await;
}
#[tokio::test]
async fn test_log_level_dirs_edge_cases() {
    let mut log: FileLogger = FileLogger::new("./logs", 512_000);
    log.set_trace_dir("")
        .set_debug_dir("")
        .set_info_dir("")
        .set_warn_dir("")
        .set_error_dir("");
    assert_eq!(log.get_trace_dir(), "");
    assert_eq!(log.get_debug_dir(), "");
    assert_eq!(log.get_info_dir(), "");
    assert_eq!(log.get_warn_dir(), "");
    assert_eq!(log.get_error_dir(), "");
    log.trace("empty dir trace", common_log);
    log.debug("empty dir debug", common_log);
    log.info("empty dir info", common_log);
    log.warn("empty dir warn", common_log);
    log.error("empty dir error", common_log);
    log.set_trace_dir("valid_trace")
        .set_debug_dir("valid_debug")
        .set_info_dir("valid_info")
        .set_warn_dir("valid_warn")
        .set_error_dir("valid_error");
    let long_dir_name: String = "a".repeat(200);
    log.set_trace_dir(&long_dir_name);
    assert_eq!(log.get_trace_dir().as_str(), long_dir_name.as_str());
}
```
