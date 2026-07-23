<!--2026-07-23 19:24:43-->
# Path: hyperlane-time/README.md
## hyperlane-time
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
pub use r#fn::*;
use r#enum::*;
use std::{
    env, fmt,
    fmt::Write,
    str::FromStr,
    time::{Duration, SystemTime, UNIX_EPOCH},
};
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
# Path: hyperlane-time/src/impl.rs
```rust
use super::*;
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
# Path: hyperlane-time/src/mod.rs
```rust
use super::*;
```
# Path: hyperlane-time/src/fn.rs
```rust
use super::*;
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
        days_since_epoch -= days_in_year;
        year += 1;
    }
    let mut month: u64 = 0;
    for (i, &days) in COMMON_YEAR.iter().enumerate() {
        let days_in_month = if i == 1 && is_leap_year(year) {
            days + 1
        } else {
            days
        };
        if days_since_epoch < days_in_month {
            month = i as u64 + 1;
            return (year, month, days_since_epoch + 1);
        }
        days_since_epoch -= days_in_month;
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
# Path: hyperlane-time/tests/mod.rs
```rust
mod time;
use hyperlane_time::*;
```
# Path: hyperlane-time/tests/time/mod.rs
```rust
mod r#fn;
use super::*;
```
# Path: hyperlane-time/tests/time/fn.rs
```rust
use super::*;
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
# Path: hyperlane-plugin-websocket/README.md
## hyperlane-plugin-websocket
[Api Docs](https://docs.rs/hyperlane-plugin-websocket/latest/)
> A WebSocket plugin for the Hyperlane framework, providing robust WebSocket communication capabilities and integrating with hyperlane-broadcast for efficient message dissemination.
## Installation
To use this crate, you can run cmd:
```shell
cargo add hyperlane-plugin-websocket
```
## Contact
# Path: hyperlane-plugin-websocket/src/trait.rs
```rust
pub trait BroadcastTypeTrait: ToString + PartialOrd + Clone {}
```
# Path: hyperlane-plugin-websocket/src/lib.rs
```rust
mod r#const;
mod r#enum;
mod r#impl;
mod r#struct;
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
use {
    hyperlane::{
        tokio::sync::broadcast::{Receiver, error::SendError},
        *,
    },
    hyperlane_broadcast::*,
};
```
# Path: hyperlane-plugin-websocket/src/enum.rs
```rust
use super::*;
#[derive(Clone, Copy, Debug, Eq, Hash, PartialEq)]
pub enum BroadcastType<T: BroadcastTypeTrait> {
    PointToPoint(T, T),
    PointToGroup(T),
    Unknown,
}
```
# Path: hyperlane-plugin-websocket/src/struct.rs
```rust
use super::*;
#[derive(Clone, Debug, Default)]
pub struct WebSocket {
    pub(super) broadcast_map: BroadcastMap<Vec<u8>>,
}
pub struct WebSocketConfig<'a, B: BroadcastTypeTrait> {
    pub(super) stream: &'a mut Stream,
    pub(super) context: &'a mut Context,
    pub(super) capacity: Capacity,
    pub(super) broadcast_type: BroadcastType<B>,
    pub(super) connected_hook: ServerHookHandler,
    pub(super) request_hook: ServerHookHandler,
    pub(super) sended_hook: ServerHookHandler,
    pub(super) closed_hook: ServerHookHandler,
}
```
# Path: hyperlane-plugin-websocket/src/const.rs
```rust
pub(crate) const POINT_TO_POINT_KEY: &str = "ptp-";
pub(crate) const POINT_TO_GROUP_KEY: &str = "ptg-";
```
# Path: hyperlane-plugin-websocket/src/impl.rs
```rust
use super::*;
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
    pub fn new(stream: &'a mut Stream, context: &'a mut Context) -> Self {
        Self {
            stream,
            context,
            capacity: DEFAULT_BROADCAST_SENDER_CAPACITY,
            broadcast_type: BroadcastType::default(),
            connected_hook: Hook::default_handler(),
            request_hook: Hook::default_handler(),
            sended_hook: Hook::default_handler(),
            closed_hook: Hook::default_handler(),
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
    pub fn get_stream(&mut self) -> &mut Stream {
        self.stream
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
        self.connected_hook = Hook::factory::<S>();
        self
    }
    #[inline(always)]
    pub fn set_request_hook<S>(mut self) -> Self
    where
        S: ServerHook,
    {
        self.request_hook = Hook::factory::<S>();
        self
    }
    #[inline(always)]
    pub fn set_sended_hook<S>(mut self) -> Self
    where
        S: ServerHook,
    {
        self.sended_hook = Hook::factory::<S>();
        self
    }
    #[inline(always)]
    pub fn set_closed_hook<S>(mut self) -> Self
    where
        S: ServerHook,
    {
        self.closed_hook = Hook::factory::<S>();
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
    pub async fn run<B>(&self, websocket_config: WebSocketConfig<'_, B>)
    where
        B: BroadcastTypeTrait,
    {
        let capacity: Capacity = websocket_config.get_capacity();
        let broadcast_type: BroadcastType<B> = websocket_config.get_broadcast_type().clone();
        let connected_hook: ServerHookHandler = websocket_config.get_connected_hook().clone();
        let sended_hook: ServerHookHandler = websocket_config.get_sended_hook().clone();
        let request_hook: ServerHookHandler = websocket_config.get_request_hook().clone();
        let closed_hook: ServerHookHandler = websocket_config.get_closed_hook().clone();
        let WebSocketConfig {
            stream,
            context: ctx,
            ..
        } = websocket_config;
        let mut receiver: Receiver<Vec<u8>> = match &broadcast_type {
            BroadcastType::PointToPoint(key1, key2) => self.point_to_point(key1, key2, capacity),
            BroadcastType::PointToGroup(key) => self.point_to_group(key, capacity),
            BroadcastType::Unknown => panic!("BroadcastType must be PointToPoint or PointToGroup"),
        };
        let key: String = BroadcastType::get_key(broadcast_type);
        if connected_hook(stream, ctx).await.is_reject() {
            return;
        }
        let mut is_reject: bool;
        loop {
            tokio::select! {
                request_res = stream.try_get_websocket_request() => {
                    if let Ok(body) = request_res {
                        ctx.get_mut_request().set_body(body);
                        is_reject = request_hook(stream, ctx).await.is_reject();
                    } else {
                        is_reject = true;
                        closed_hook(stream, ctx).await;
                    }
                    let body: ResponseBody = ctx.get_response().get_body().clone();
                    let is_err: bool = self.broadcast_map.try_send(&key, body).is_err();
                    if is_err || sended_hook(stream, ctx).await.is_reject() || is_reject {
                        break;
                    }
                },
                msg_res = receiver.recv() => {
                    if let Ok(msg) = &msg_res {
                        if stream.try_send_list(&WebSocketFrame::create_frame_list(msg)).await.is_ok() {
                            continue;
                        } else {
                            break;
                        }
                    }
                    break;
                }
            }
        }
        stream.set_closed(true);
    }
}
```
# Path: hyperlane-plugin-websocket/tests/mod.rs
```rust
mod websocket;
use hyperlane_plugin_websocket::*;
use std::sync::OnceLock;
use {
    hyperlane::*,
    hyperlane_broadcast::*,
    tokio::{spawn, time::sleep},
};
```
# Path: hyperlane-plugin-websocket/tests/websocket/struct.rs
```rust
use super::*;
pub(crate) struct TaskPanicHook {
    pub(crate) response_body: String,
    pub(crate) content_type: String,
}
pub(crate) struct RequestErrorHook {
    pub(crate) response_status_code: ResponseStatusCode,
    pub(crate) response_body: String,
}
pub(crate) struct RequestMiddleware {
    pub(crate) socket_addr: String,
}
pub(crate) struct UpgradeHook;
pub(crate) struct ConnectedHook {
    pub(crate) receiver_count: ReceiverCount,
    pub(crate) data: String,
    pub(crate) group_broadcast_type: BroadcastType<String>,
    pub(crate) private_broadcast_type: BroadcastType<String>,
}
pub(crate) struct SendedHook {
    pub(crate) msg: String,
}
pub(crate) struct GroupChatRequestHook {
    pub(crate) body: RequestBody,
    pub(crate) receiver_count: ReceiverCount,
}
pub(crate) struct GroupClosedHook {
    pub(crate) body: String,
    pub(crate) receiver_count: ReceiverCount,
}
pub(crate) struct GroupChat;
pub(crate) struct PrivateChatRequestHook {
    pub(crate) body: RequestBody,
    pub(crate) receiver_count: ReceiverCount,
}
pub(crate) struct PrivateClosedHook {
    pub(crate) body: String,
    pub(crate) receiver_count: ReceiverCount,
}
pub(crate) struct PrivateChat;
```
# Path: hyperlane-plugin-websocket/tests/websocket/static.rs
```rust
use super::*;
pub(crate) static BROADCAST_MAP: OnceLock<WebSocket> = OnceLock::new();
```
# Path: hyperlane-plugin-websocket/tests/websocket/impl.rs
```rust
use super::*;
impl ServerHook for TaskPanicHook {
    async fn new(_: &mut Stream, ctx: &mut Context) -> Self {
        let error: PanicData = ctx.try_get_task_panic_data().unwrap_or_default();
        let response_body: String = error.to_string();
        let content_type: String = ContentType::format_content_type_with_charset(TEXT_PLAIN, UTF8);
        Self {
            response_body,
            content_type,
        }
    }
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        let data: Vec<u8> = ctx
            .get_mut_response()
            .set_version(HttpVersion::Http1_1)
            .set_status_code(500)
            .clear_headers()
            .set_header(SERVER, HYPERLANE)
            .set_header(CONTENT_TYPE, &self.content_type)
            .set_body(&self.response_body)
            .build();
        if stream.try_send(data).await.is_err() {
            stream.set_closed(true);
            return Status::Reject;
        }
        Status::Continue
    }
}
impl ServerHook for RequestErrorHook {
    async fn new(_: &mut Stream, ctx: &mut Context) -> Self {
        let request_error: RequestError = ctx.try_get_request_error_data().unwrap_or_default();
        Self {
            response_status_code: request_error.get_http_status_code(),
            response_body: request_error.to_string(),
        }
    }
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        let data: Vec<u8> = ctx
            .get_mut_response()
            .set_version(HttpVersion::Http1_1)
            .set_status_code(self.response_status_code)
            .set_body(self.response_body)
            .build();
        if stream.try_send(data).await.is_err() {
            stream.set_closed(true);
            return Status::Reject;
        }
        Status::Continue
    }
}
impl ServerHook for RequestMiddleware {
    async fn new(stream: &mut Stream, _: &mut Context) -> Self {
        let socket_addr: String = stream
            .get_stream()
            .peer_addr()
            .map(|data| data.to_string())
            .unwrap_or_default();
        Self { socket_addr }
    }
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        ctx.get_mut_response()
            .set_version(HttpVersion::Http1_1)
            .set_status_code(200)
            .set_header(SERVER, HYPERLANE)
            .set_header(CONNECTION, KEEP_ALIVE)
            .set_header(CONTENT_TYPE, TEXT_PLAIN)
            .set_header(ACCESS_CONTROL_ALLOW_ORIGIN, WILDCARD_ANY)
            .set_header("SocketAddr", &self.socket_addr);
        Status::Continue
    }
}
impl ServerHook for UpgradeHook {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        if !ctx.get_request().is_ws_upgrade_type() {
            return Status::Continue;
        }
        if let Some(key) = &ctx.get_request().try_get_header_back(SEC_WEBSOCKET_KEY) {
            let accept_key: String = WebSocketFrame::generate_accept_key(key);
            let data: Vec<u8> = ctx
                .get_mut_response()
                .set_version(HttpVersion::Http1_1)
                .set_status_code(101)
                .set_header(UPGRADE, WEBSOCKET)
                .set_header(CONNECTION, UPGRADE)
                .set_header(SEC_WEBSOCKET_ACCEPT, &accept_key)
                .set_body(Vec::new())
                .build();
            if stream.try_send(data).await.is_err() {
                stream.set_closed(true);
                return Status::Reject;
            }
        }
        Status::Continue
    }
}
impl ServerHook for ConnectedHook {
    async fn new(_: &mut Stream, ctx: &mut Context) -> Self {
        let group_name: String = ctx.try_get_route_param("group_name").unwrap_or_default();
        let group_broadcast_type: BroadcastType<String> = BroadcastType::PointToGroup(group_name);
        let group_receiver_count: ReceiverCount = BROADCAST_MAP
            .get_or_init(WebSocket::new)
            .receiver_count(group_broadcast_type.clone());
        let my_name: String = ctx.try_get_route_param("my_name").unwrap_or_default();
        let your_name: String = ctx.try_get_route_param("your_name").unwrap_or_default();
        let private_broadcast_type: BroadcastType<String> =
            BroadcastType::PointToPoint(my_name, your_name);
        let private_receiver_count: ReceiverCount = BROADCAST_MAP
            .get_or_init(WebSocket::new)
            .receiver_count(private_broadcast_type.clone());
        let receiver_count: usize = if group_receiver_count > 0 {
            group_receiver_count
        } else {
            private_receiver_count
        };
        let data: String = format!("receiver_count => {receiver_count:?}");
        Self {
            receiver_count,
            data,
            group_broadcast_type,
            private_broadcast_type,
        }
    }
    async fn handle(self, _: &mut Stream, _: &mut Context) -> Status {
        BROADCAST_MAP
            .get_or_init(WebSocket::new)
            .try_send(self.group_broadcast_type, self.data.clone())
            .unwrap_or_else(|err| {
                println!("[connected_hook] send group error => {:?}", err.to_string());
                None
            });
        BROADCAST_MAP
            .get_or_init(WebSocket::new)
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
        Status::Continue
    }
}
impl ServerHook for SendedHook {
    async fn new(_: &mut Stream, ctx: &mut Context) -> Self {
        let msg: String = ctx.get_response().get_body_string();
        Self { msg }
    }
    async fn handle(self, _: &mut Stream, _: &mut Context) -> Status {
        println!("[sended_hook] msg => {}", self.msg);
        Server::flush_stdout();
        Status::Continue
    }
}
impl ServerHook for GroupChatRequestHook {
    async fn new(_: &mut Stream, ctx: &mut Context) -> Self {
        let group_name: String = ctx.try_get_route_param("group_name").unwrap();
        let key: BroadcastType<String> = BroadcastType::PointToGroup(group_name);
        let mut receiver_count: ReceiverCount = BROADCAST_MAP
            .get_or_init(WebSocket::new)
            .receiver_count(key.clone());
        let mut body: RequestBody = ctx.get_request().get_body().clone();
        if body.is_empty() {
            receiver_count = BROADCAST_MAP
                .get_or_init(WebSocket::new)
                .receiver_count_after_closed(key);
            body = format!("receiver_count => {receiver_count:?}").into();
        }
        Self {
            body,
            receiver_count,
        }
    }
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        ctx.get_mut_response().set_body(&self.body);
        println!("[group_chat] receiver_count => {:?}", self.receiver_count);
        Server::flush_stdout();
        Status::Continue
    }
}
impl ServerHook for GroupClosedHook {
    async fn new(_: &mut Stream, ctx: &mut Context) -> Self {
        let group_name: String = ctx.try_get_route_param("group_name").unwrap();
        let key: BroadcastType<String> = BroadcastType::PointToGroup(group_name);
        let receiver_count: ReceiverCount = BROADCAST_MAP
            .get_or_init(WebSocket::new)
            .receiver_count_after_closed(key.clone());
        let body: String = format!("receiver_count => {receiver_count:?}");
        Self {
            body,
            receiver_count,
        }
    }
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        ctx.get_mut_response().set_body(&self.body);
        println!("[group_closed] receiver_count => {:?}", self.receiver_count);
        Server::flush_stdout();
        Status::Continue
    }
}
impl ServerHook for GroupChat {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        let group_name: String = ctx.try_get_route_param("group_name").unwrap();
        let key: BroadcastType<String> = BroadcastType::PointToGroup(group_name);
        let config: WebSocketConfig<String> = WebSocketConfig::new(stream, ctx)
            .set_capacity(1024)
            .set_broadcast_type(key)
            .set_connected_hook::<ConnectedHook>()
            .set_request_hook::<GroupChatRequestHook>()
            .set_sended_hook::<SendedHook>()
            .set_closed_hook::<GroupClosedHook>();
        BROADCAST_MAP.get_or_init(WebSocket::new).run(config).await;
        Status::Continue
    }
}
impl ServerHook for PrivateChatRequestHook {
    async fn new(_: &mut Stream, ctx: &mut Context) -> Self {
        let my_name: String = ctx.try_get_route_param("my_name").unwrap();
        let your_name: String = ctx.try_get_route_param("your_name").unwrap();
        let key: BroadcastType<String> = BroadcastType::PointToPoint(my_name, your_name);
        let mut receiver_count: ReceiverCount = BROADCAST_MAP
            .get_or_init(WebSocket::new)
            .receiver_count(key.clone());
        let mut body: RequestBody = ctx.get_request().get_body().clone();
        if body.is_empty() {
            receiver_count = BROADCAST_MAP
                .get_or_init(WebSocket::new)
                .receiver_count_after_closed(key);
            body = format!("receiver_count => {receiver_count:?}").into();
        }
        Self {
            body,
            receiver_count,
        }
    }
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        ctx.get_mut_response().set_body(&self.body);
        println!("[private_chat] receiver_count => {:?}", self.receiver_count);
        Server::flush_stdout();
        Status::Continue
    }
}
impl ServerHook for PrivateClosedHook {
    async fn new(_: &mut Stream, ctx: &mut Context) -> Self {
        let my_name: String = ctx.try_get_route_param("my_name").unwrap();
        let your_name: String = ctx.try_get_route_param("your_name").unwrap();
        let key: BroadcastType<String> = BroadcastType::PointToPoint(my_name, your_name);
        let receiver_count: ReceiverCount = BROADCAST_MAP
            .get_or_init(WebSocket::new)
            .receiver_count_after_closed(key);
        let body: String = format!("receiver_count => {receiver_count:?}");
        Self {
            body,
            receiver_count,
        }
    }
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        ctx.get_mut_response().set_body(&self.body);
        println!(
            "[private_closed] receiver_count => {:?}",
            self.receiver_count
        );
        Server::flush_stdout();
        Status::Continue
    }
}
impl ServerHook for PrivateChat {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        let my_name: String = ctx.try_get_route_param("my_name").unwrap();
        let your_name: String = ctx.try_get_route_param("your_name").unwrap();
        let key: BroadcastType<String> = BroadcastType::PointToPoint(my_name, your_name);
        let config: WebSocketConfig<String> = WebSocketConfig::new(stream, ctx)
            .set_capacity(1024)
            .set_broadcast_type(key)
            .set_connected_hook::<ConnectedHook>()
            .set_request_hook::<PrivateChatRequestHook>()
            .set_sended_hook::<SendedHook>()
            .set_closed_hook::<PrivateClosedHook>();
        BROADCAST_MAP.get_or_init(WebSocket::new).run(config).await;
        Status::Continue
    }
}
```
# Path: hyperlane-plugin-websocket/tests/websocket/mod.rs
```rust
mod r#fn;
mod r#impl;
mod r#static;
mod r#struct;
pub(crate) use {r#static::*, r#struct::*};
use super::*;
```
# Path: hyperlane-plugin-websocket/tests/websocket/fn.rs
```rust
use super::*;
#[tokio::test]
async fn main() {
    let mut server: Server = Server::default();
    let request_config: RequestConfig = RequestConfig::low_security();
    server.request_config(request_config);
    server.task_panic::<TaskPanicHook>();
    server.request_error::<RequestErrorHook>();
    server.request_middleware::<RequestMiddleware>();
    server.request_middleware::<UpgradeHook>();
    server.route::<GroupChat>("/{group_name}");
    server.route::<PrivateChat>("/{my_name}/{your_name}");
    let server_control_hook_1: ServerControlHook = server.run().await.unwrap_or_default();
    let server_control_hook_2: ServerControlHook = server_control_hook_1.clone();
    spawn(async move {
        sleep(std::time::Duration::from_secs(60)).await;
        server_control_hook_2.shutdown().await;
    });
    server_control_hook_1.wait().await;
}
```
# Path: hyperlane-utils/README.md
## hyperlane-utils
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
    aes, ahash, base64, bin_encode_decode::*, bytemuck_derive, chrono, chunkify::*, cipher,
    clonelicious::*, color_output::*, compare_version::*, dotenvy, ed25519_dalek,
    file_operation::*, future_fn::*, futures, getrandom, hex, hot_restart::*,
    hyperlane_broadcast::*, hyperlane_log::*, hyperlane_macros::*, hyperlane_plugin_websocket::*,
    instrument_level::*, jsonwebtoken, jwt_service::*, log, lombok_macros::*, md5, num_cpus,
    once_cell, rand, recoverable_spawn::*, recoverable_thread_pool::*, redis, regex, reqwest, rsa,
    rust_decimal, rustls_pki_types, scraper, sea_orm, serde_urlencoded, serde_with, serde_xml_rs,
    serde_yaml, server_manager::*, sha2, simd_json, snafu, sqlx, std_macro_extensions::*, sysinfo,
    tracing_log, tracing_subscriber, twox_hash, url, urlencoding, utoipa, utoipa_rapidoc,
    utoipa_swagger_ui, uuid,
};
```
# Path: hyperlane-broadcast/README.md
## hyperlane-broadcast
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
use std::{fmt::Debug, hash::BuildHasherDefault};
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
use super::*;
pub trait BroadcastMapTrait: Clone + Debug {}
```
# Path: hyperlane-broadcast/src/broadcast_map/struct.rs
```rust
use super::*;
#[derive(Clone, Debug)]
pub struct BroadcastMap<T: BroadcastTrait>(pub(super) DashMapStringBroadcast<T>);
```
# Path: hyperlane-broadcast/src/broadcast_map/type.rs
```rust
use super::*;
pub type BroadcastMapSendError<T> = SendError<T>;
pub type BroadcastMapReceiver<T> = Receiver<T>;
pub type BroadcastMapSender<T> = Sender<T>;
pub type DashMapStringBroadcast<T> = DashMap<String, Broadcast<T>, BuildHasherDefault<XxHash3_64>>;
```
# Path: hyperlane-broadcast/src/broadcast_map/impl.rs
```rust
use super::*;
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
# Path: hyperlane-broadcast/src/broadcast_map/mod.rs
```rust
mod r#impl;
mod r#struct;
mod r#trait;
mod r#type;
pub use {r#struct::*, r#trait::*, r#type::*};
use super::*;
```
# Path: hyperlane-broadcast/src/broadcast/trait.rs
```rust
use super::*;
pub trait BroadcastTrait: Clone + Debug {}
```
# Path: hyperlane-broadcast/src/broadcast/struct.rs
```rust
use super::*;
#[derive(Clone, Debug)]
pub struct Broadcast<T: BroadcastTrait>(pub(super) BroadcastSender<T>);
```
# Path: hyperlane-broadcast/src/broadcast/type.rs
```rust
use super::*;
pub type ReceiverCount = usize;
pub type BroadcastSendError<T> = SendError<T>;
pub type BroadcastSendResult<T> = Result<ReceiverCount, BroadcastSendError<T>>;
pub type BroadcastReceiver<T> = Receiver<T>;
pub type BroadcastSender<T> = Sender<T>;
pub type Capacity = usize;
```
# Path: hyperlane-broadcast/src/broadcast/const.rs
```rust
pub const DEFAULT_BROADCAST_SENDER_CAPACITY: usize = 1024;
```
# Path: hyperlane-broadcast/src/broadcast/impl.rs
```rust
use super::*;
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
# Path: hyperlane-broadcast/src/broadcast/mod.rs
```rust
mod r#const;
mod r#impl;
mod r#struct;
mod r#trait;
mod r#type;
pub use {r#const::*, r#struct::*, r#trait::*, r#type::*};
use super::*;
```
# Path: hyperlane-broadcast/tests/mod.rs
```rust
mod broadcast;
mod broadcast_map;
use hyperlane_broadcast::*;
use std::time::Duration;
use tokio::{
    sync::broadcast::error::{RecvError, SendError},
    time::{error::Elapsed, timeout},
};
```
# Path: hyperlane-broadcast/tests/broadcast_map/mod.rs
```rust
mod r#fn;
use super::*;
```
# Path: hyperlane-broadcast/tests/broadcast_map/fn.rs
```rust
use super::*;
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
# Path: hyperlane-broadcast/tests/broadcast/mod.rs
```rust
mod r#fn;
use super::*;
```
# Path: hyperlane-broadcast/tests/broadcast/fn.rs
```rust
use super::*;
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
# Path: hyperlane/README.md
## hyperlane
[Api Docs](https://docs.rs/hyperlane/latest/)
> A lightweight, high-performance, and cross-platform Rust HTTP server library built on Tokio. It simplifies modern web service development by providing built-in support for middleware, WebSocket, Server-Sent Events (SSE), and raw TCP communication. With a unified and ergonomic API across Windows, Linux, and MacOS, it enables developers to build robust, scalable, and event-driven network applications with minimal overhead and maximum flexibility.
## Installation
To use this crate, you can run cmd:
```shell
cargo add hyperlane
```
## Quick start
- [hyperlane-quick-start git](https://github.com/hyperlane-dev/hyperlane-quick-start)
```sh
git clone https://github.com/hyperlane-dev/hyperlane-quick-start.git
```
## Contact
# Path: hyperlane/src/lib.rs
```rust
mod config;
mod context;
mod error;
mod hook;
mod route;
mod server;
pub use {config::*, context::*, error::*, hook::*, route::*, server::*};
pub use {http_type::*, inventory};
use std::{
    cmp::Ordering,
    collections::HashSet,
    future::Future,
    hash::{Hash, Hasher},
    io::{self, Write, stderr, stdout},
    pin::Pin,
    sync::Arc,
};
use {
    inventory::collect,
    lombok_macros::*,
    regex::Regex,
    serde::{Deserialize, Serialize},
    tokio::{
        net::{TcpListener, TcpStream},
        spawn,
        sync::watch::{Receiver, Sender, channel},
        task::JoinHandle,
    },
};
```
# Path: hyperlane/src/hook/trait.rs
```rust
use super::*;
pub trait FnContext<R>: Fn(&mut Context) -> R + Send + Sync {}
pub trait FnContextPinBox<T>: FnContext<FutureBox<T>> {}
pub trait FnContextStatic<Fut, T>: FnContext<Fut> + 'static
where
    Fut: Future<Output = T> + Send,
{
}
```
# Path: hyperlane/src/hook/enum.rs
```rust
use super::*;
#[derive(Clone, Copy, Debug, DisplayDebug)]
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
use super::*;
#[derive(
    Clone,
    Copy,
    Debug,
    Deserialize,
    DisplayDebug,
    Eq,
    Hash,
    Ord,
    PartialEq,
    PartialOrd,
    Serialize,
    Default,
)]
pub struct DefaultServerHook;
#[derive(
    Clone,
    Copy,
    Debug,
    Deserialize,
    DisplayDebug,
    Eq,
    Hash,
    Ord,
    PartialEq,
    PartialOrd,
    Serialize,
    Default,
)]
pub struct Hook;
#[derive(Clone, CustomDebug, DisplayDebug, Getter, Setter)]
pub struct ServerControlHook {
    #[debug(skip)]
    #[set(pub(crate))]
    pub(super) wait_hook: ServerControlHookHandler<()>,
    #[debug(skip)]
    #[set(pub(crate))]
    pub(super) shutdown_hook: ServerControlHookHandler<()>,
}
```
# Path: hyperlane/src/hook/type.rs
```rust
use super::*;
pub type HookHandler<T> = Arc<dyn FnContextPinBox<T>>;
pub type HookHandlerChain<T> = Vec<HookHandler<T>>;
pub type FutureBox<T> = Pin<Box<dyn Future<Output = T> + Send>>;
pub type ServerControlHookHandler<T> = Arc<dyn FutureFn<T>>;
pub type ServerHookHandlerFactory = fn() -> ServerHookHandler;
pub type ServerHookHandler =
    Arc<dyn Fn(&mut Stream, &mut Context) -> FutureBox<Status> + Send + Sync>;
pub type ServerHookList = Vec<ServerHookHandler>;
pub type ServerHookMap = HashMapXxHash3_64<String, ServerHookHandler>;
pub type ServerHookPatternRoute = HashMapXxHash3_64<usize, Vec<(RoutePattern, ServerHookHandler)>>;
```
# Path: hyperlane/src/hook/impl.rs
```rust
use super::*;
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
            wait_hook: Hook::default_control_handler(),
            shutdown_hook: Hook::default_control_handler(),
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
impl Hook {
    #[inline(always)]
    pub fn default_control_handler() -> ServerControlHookHandler<()> {
        Arc::new(|| Box::pin(async {}))
    }
    #[inline(always)]
    pub fn default_handler() -> ServerHookHandler {
        Arc::new(|_: &mut Stream, _: &mut Context| -> FutureBox<Status> {
            Box::pin(async move { Status::default() })
        })
    }
    #[inline(always)]
    pub fn factory<R>() -> ServerHookHandler
    where
        R: ServerHook,
    {
        Arc::new(
            move |stream: &mut Stream, ctx: &mut Context| -> FutureBox<Status> {
                let ctx_address: usize = ctx.into();
                let stream_address: usize = stream.into();
                Box::pin(async move {
                    let ctx: &mut Context = ctx_address.into();
                    let stream: &mut Stream = stream_address.into();
                    R::new(stream, ctx).await.handle(stream, ctx).await
                })
            },
        )
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
    #[inline(always)]
    pub fn assert_unique_order(list: Vec<HookType>) {
        let mut seen: HashSet<(HookType, isize)> = HashSet::new();
        list.iter().for_each(|hook: &HookType| {
            if let Some(order) = hook.try_get_order()
                && !seen.insert((*hook, order))
            {
                panic!("Duplicate hook detected: {} with order {}", hook, order);
            }
        });
    }
}
impl ServerHook for DefaultServerHook {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    async fn handle(self, _: &mut Stream, _: &mut Context) -> Status {
        Status::default()
    }
}
```
# Path: hyperlane/src/hook/mod.rs
```rust
mod r#enum;
mod r#impl;
mod r#struct;
mod r#trait;
mod r#type;
pub use {r#enum::*, r#struct::*, r#trait::*, r#type::*};
use super::*;
```
# Path: hyperlane/src/config/struct.rs
```rust
use super::*;
#[derive(Clone, CustomDebug, Data, Deserialize, DisplayDebug, Eq, New, PartialEq, Serialize)]
pub struct ServerConfig {
    #[set(type(AsRef<str>))]
    pub(super) address: String,
    pub(super) nodelay: Option<bool>,
    pub(super) ttl: Option<u32>,
}
```
# Path: hyperlane/src/config/impl.rs
```rust
use super::*;
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
# Path: hyperlane/src/config/mod.rs
```rust
mod r#impl;
mod r#struct;
pub use r#struct::*;
use super::*;
```
# Path: hyperlane/src/context/struct.rs
```rust
use super::*;
#[derive(Clone, CustomDebug, Data, DisplayDebug)]
pub struct Context {
    pub(super) request: Request,
    pub(super) response: Response,
    #[get_mut(skip)]
    pub(super) route_params: RouteParams,
    pub(super) attributes: ThreadSafeAttributeStore,
}
```
# Path: hyperlane/src/context/impl.rs
```rust
use super::*;
impl Default for Context {
    #[inline(always)]
    fn default() -> Self {
        Self {
            request: Request::default(),
            response: Response::default(),
            route_params: RouteParams::default(),
            attributes: ThreadSafeAttributeStore::default(),
        }
    }
}
impl PartialEq for Context {
    #[inline(always)]
    fn eq(&self, other: &Self) -> bool {
        self.get_request() == other.get_request()
            && self.get_response() == other.get_response()
            && self.get_route_params() == other.get_route_params()
            && self.get_attributes().len() == other.get_attributes().len()
    }
}
impl Eq for Context {}
impl From<usize> for &'static Context {
    #[inline(always)]
    fn from(address: usize) -> &'static Context {
        unsafe { &*(address as *const Context) }
    }
}
impl<'a> From<usize> for &'a mut Context {
    #[inline(always)]
    fn from(address: usize) -> &'a mut Context {
        unsafe { &mut *(address as *mut Context) }
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
    fn as_ref(&self) -> &Self {
        let address: usize = self.into();
        address.into()
    }
}
impl AsMut<Context> for Context {
    #[inline(always)]
    fn as_mut(&mut self) -> &mut Self {
        let address: usize = self.into();
        address.into()
    }
}
impl Lifetime for Context {
    #[inline(always)]
    unsafe fn leak(&self) -> &'static Self {
        let address: usize = self.into();
        address.into()
    }
    #[inline(always)]
    unsafe fn leak_mut(&self) -> &'static mut Self {
        let address: usize = self.into();
        address.into()
    }
}
impl Context {
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
            .and_then(|arc: &ArcAnySendSync| arc.downcast_ref::<V>())
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
            .and_then(|arc: &ArcAnySendSync| arc.downcast_ref::<V>())
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
    pub fn set_task_panic(&mut self, panic_data: PanicData) -> &mut Self {
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
}
```
# Path: hyperlane/src/context/mod.rs
```rust
mod r#impl;
mod r#struct;
pub use r#struct::*;
use super::*;
```
# Path: hyperlane/src/server/struct.rs
```rust
use super::*;
#[derive(Clone, CustomDebug, Data, DisplayDebug)]
pub struct Server {
    pub(super) server_config: ServerConfig,
    pub(super) request_config: RequestConfig,
    #[set(skip)]
    pub(super) route_matcher: RouteMatcher,
    #[debug(skip)]
    #[set(skip)]
    pub(super) request_error: ServerHookList,
    #[debug(skip)]
    #[set(skip)]
    pub(super) task_panic: ServerHookList,
    #[debug(skip)]
    #[set(skip)]
    pub(super) request_middleware: ServerHookList,
    #[debug(skip)]
    #[set(skip)]
    pub(super) response_middleware: ServerHookList,
}
```
# Path: hyperlane/src/server/impl.rs
```rust
use super::*;
impl Default for Server {
    #[inline(always)]
    fn default() -> Self {
        Self {
            server_config: ServerConfig::default(),
            request_config: RequestConfig::default(),
            task_panic: Vec::new(),
            request_error: Vec::new(),
            route_matcher: RouteMatcher::new(),
            request_middleware: Vec::new(),
            response_middleware: Vec::new(),
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
                .all(|pair: (&ServerHookHandler, &ServerHookHandler)| Arc::ptr_eq(pair.0, pair.1))
            && self
                .get_request_error()
                .iter()
                .zip(other.get_request_error().iter())
                .all(|pair: (&ServerHookHandler, &ServerHookHandler)| Arc::ptr_eq(pair.0, pair.1))
            && self
                .get_request_middleware()
                .iter()
                .zip(other.get_request_middleware().iter())
                .all(|pair: (&ServerHookHandler, &ServerHookHandler)| Arc::ptr_eq(pair.0, pair.1))
            && self
                .get_response_middleware()
                .iter()
                .zip(other.get_response_middleware().iter())
                .all(|pair: (&ServerHookHandler, &ServerHookHandler)| Arc::ptr_eq(pair.0, pair.1))
    }
}
impl Eq for Server {}
impl From<usize> for Server {
    #[inline(always)]
    fn from(address: usize) -> Self {
        let server: &Server = address.into();
        server.clone()
    }
}
impl From<usize> for &'static Server {
    #[inline(always)]
    fn from(address: usize) -> &'static Server {
        unsafe { &*(address as *const Server) }
    }
}
impl From<usize> for &'static mut Server {
    #[inline(always)]
    fn from(address: usize) -> &'static mut Server {
        unsafe { &mut *(address as *mut Server) }
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
    fn as_ref(&self) -> &Self {
        let address: usize = self.into();
        address.into()
    }
}
impl AsMut<Server> for Server {
    #[inline(always)]
    fn as_mut(&mut self) -> &mut Self {
        let address: usize = self.into();
        address.into()
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
impl Lifetime for Server {
    #[inline(always)]
    unsafe fn leak(&self) -> &'static Self {
        let address: usize = self.into();
        address.into()
    }
    #[inline(always)]
    unsafe fn leak_mut(&self) -> &'static mut Self {
        let address: usize = self.into();
        address.into()
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
        self.get_mut_task_panic().push(Hook::factory::<S>());
        self
    }
    #[inline(always)]
    pub fn request_error<S>(&mut self) -> &mut Self
    where
        S: ServerHook,
    {
        self.get_mut_request_error().push(Hook::factory::<S>());
        self
    }
    #[inline(always)]
    pub fn route<S>(&mut self, path: impl AsRef<str>) -> &mut Self
    where
        S: ServerHook,
    {
        self.get_mut_route_matcher()
            .add(path.as_ref(), Hook::factory::<S>())
            .unwrap();
        self
    }
    #[inline(always)]
    pub fn request_middleware<S>(&mut self) -> &mut Self
    where
        S: ServerHook,
    {
        self.get_mut_request_middleware().push(Hook::factory::<S>());
        self
    }
    #[inline(always)]
    pub fn response_middleware<S>(&mut self) -> &mut Self
    where
        S: ServerHook,
    {
        self.get_mut_response_middleware()
            .push(Hook::factory::<S>());
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
    async fn task_handler<F>(&'static self, stream_address: usize, ctx_address: usize, hook: F)
    where
        F: Future<Output = ()> + Send + 'static,
    {
        if let Err(error) = spawn(hook).await
            && error.is_panic()
        {
            let ctx: &mut Context = ctx_address.into();
            let stream: &mut Stream = stream_address.into();
            let panic: PanicData = PanicData::from_join_error(error);
            ctx.set_task_panic(panic)
                .get_mut_response()
                .set_status_code(HttpStatus::InternalServerError.code());
            stream.set_closed(false);
            for hook in self.get_task_panic().iter() {
                if hook(stream, ctx).await.is_reject() {
                    break;
                }
            }
            unsafe {
                let _: Box<Context> = Box::from_raw(ctx);
                let _: Box<Stream> = Box::from_raw(stream);
            }
        };
    }
    fn configure_stream(&self, stream: &TcpStream) {
        let config: &ServerConfig = self.get_server_config();
        if let Some(nodelay) = config.try_get_nodelay() {
            let _: Result<(), std::io::Error> = stream.set_nodelay(*nodelay);
        }
        if let Some(ttl) = config.try_get_ttl() {
            let _: Result<(), std::io::Error> = stream.set_ttl(*ttl);
        }
    }
    pub(super) async fn handle_request_middleware(
        &self,
        stream: &mut Stream,
        ctx: &mut Context,
    ) -> bool {
        for hook in self.get_request_middleware().iter() {
            if hook(stream, ctx).await.is_reject() {
                return true;
            }
        }
        false
    }
    pub(super) async fn handle_route_matcher(
        &self,
        stream: &mut Stream,
        ctx: &mut Context,
        path: &str,
    ) -> bool {
        if let Some(hook) = self.get_route_matcher().try_resolve_route(ctx, path)
            && hook(stream, ctx).await.is_reject()
        {
            return true;
        }
        false
    }
    pub(super) async fn handle_response_middleware(
        &self,
        stream: &mut Stream,
        ctx: &mut Context,
    ) -> bool {
        for hook in self.get_response_middleware().iter() {
            if hook(stream, ctx).await.is_reject() {
                return true;
            }
        }
        false
    }
    pub async fn handle_request_error(
        &self,
        stream: &mut Stream,
        ctx: &mut Context,
        error: &RequestError,
    ) {
        ctx.set_request_error_data(error.clone());
        stream.set_closed(false);
        for hook in self.get_request_error().iter() {
            if hook(stream, ctx).await.is_reject() {
                return;
            }
        }
    }
    async fn request_hook(
        &self,
        stream: &mut Stream,
        ctx: &mut Context,
        request: &Request,
    ) -> bool {
        let mut response: Response = Response::default();
        response.set_version(request.get_version().clone());
        ctx.set_request(request.clone());
        ctx.set_response(response);
        ctx.set_route_params(RouteParams::default());
        ctx.clear_attribute();
        stream.set_closed(false);
        let keep_alive: bool = request.is_enable_keep_alive();
        if self.handle_request_middleware(stream, ctx).await {
            return stream.is_keep_alive(keep_alive);
        }
        let route: &str = request.get_path();
        if self.handle_route_matcher(stream, ctx, route).await {
            return stream.is_keep_alive(keep_alive);
        }
        if self.handle_response_middleware(stream, ctx).await {
            return stream.is_keep_alive(keep_alive);
        }
        stream.is_keep_alive(keep_alive)
    }
    async fn handle_http_requests(
        &self,
        stream: &mut Stream,
        ctx: &mut Context,
        request: &Request,
    ) {
        if !self.request_hook(stream, ctx, request).await {
            return;
        }
        loop {
            match stream.try_get_http_request().await {
                Ok(new_request) => {
                    if !self.request_hook(stream, ctx, &new_request).await {
                        return;
                    }
                }
                Err(error) => {
                    self.handle_request_error(stream, ctx, &error).await;
                    return;
                }
            }
        }
    }
    async fn handle_connection(&self, stream: &mut Stream, ctx: &mut Context) {
        match stream.try_get_http_request().await {
            Ok(request) => {
                self.handle_http_requests(stream, ctx, &request).await;
            }
            Err(error) => {
                self.handle_request_error(stream, ctx, &error).await;
            }
        }
        unsafe {
            let _: Box<Context> = Box::from_raw(ctx);
            let _: Box<Stream> = Box::from_raw(stream);
        }
    }
    async fn tcp_accept(&'static self, tcp_listener: &TcpListener) {
        loop {
            if let Ok((stream, _)) = tcp_listener.accept().await {
                self.configure_stream(&stream);
                let request_config: RequestConfig = *self.get_request_config();
                let stream: &'static mut Stream =
                    Box::leak(Box::new(Stream::new(stream, request_config, false)));
                let ctx: &'static mut Context = Box::leak(Box::new(Context::default()));
                spawn(self.task_handler(
                    stream.into(),
                    ctx.into(),
                    self.handle_connection(stream, ctx),
                ));
            }
        }
    }
    pub async fn run(&self) -> Result<ServerControlHook, ServerError> {
        let bind_address: &String = self.get_server_config().get_address();
        let tcp_listener: TcpListener = TcpListener::bind(&bind_address).await?;
        let server: &'static Self = unsafe { self.leak() };
        let (wait_sender, wait_receiver) = channel(());
        let (shutdown_sender, mut shutdown_receiver) = channel(());
        let accept_connections: JoinHandle<()> = spawn(async move {
            server.tcp_accept(&tcp_listener).await;
            let _: Result<(), tokio::sync::watch::error::SendError<()>> = wait_sender.send(());
        });
        let wait_hook: ServerControlHookHandler<()> = Arc::new(move || {
            let mut wait_receiver_clone: Receiver<()> = wait_receiver.clone();
            Box::pin(async move {
                let _: Result<(), tokio::sync::watch::error::RecvError> =
                    wait_receiver_clone.changed().await;
            })
        });
        let shutdown_hook: ServerControlHookHandler<()> = Arc::new(move || {
            let shutdown_sender_clone: Sender<()> = shutdown_sender.clone();
            Box::pin(async move {
                let _: Result<(), tokio::sync::watch::error::SendError<()>> =
                    shutdown_sender_clone.send(());
            })
        });
        spawn(async move {
            let _: Result<(), tokio::sync::watch::error::RecvError> =
                shutdown_receiver.changed().await;
            accept_connections.abort();
        });
        let mut server_control_hook: ServerControlHook = ServerControlHook::default();
        server_control_hook.set_shutdown_hook(shutdown_hook);
        server_control_hook.set_wait_hook(wait_hook);
        Ok(server_control_hook)
    }
}
```
# Path: hyperlane/src/server/mod.rs
```rust
mod r#impl;
mod r#struct;
pub use r#struct::*;
use super::*;
```
# Path: hyperlane/src/route/enum.rs
```rust
use super::*;
#[derive(Clone, CustomDebug, DisplayDebug)]
pub enum RouteSegment {
    Static(String),
    Dynamic(String),
    Regex(String, Regex),
}
```
# Path: hyperlane/src/route/struct.rs
```rust
use super::*;
#[derive(Clone, Debug, DisplayDebug, Getter)]
pub struct RoutePattern(
    #[get]
    pub(super) RouteSegmentList,
);
#[derive(Clone, CustomDebug, DisplayDebug, Getter, GetterMut, Setter)]
pub struct RouteMatcher {
    #[get]
    #[set(skip)]
    #[debug(skip)]
    pub(super) static_route: ServerHookMap,
    #[get]
    #[set(skip)]
    #[debug(skip)]
    pub(super) dynamic_route: ServerHookPatternRoute,
    #[get]
    #[set(skip)]
    #[debug(skip)]
    pub(super) regex_route: ServerHookPatternRoute,
}
```
# Path: hyperlane/src/route/type.rs
```rust
use super::*;
pub type RouteParams = HashMapXxHash3_64<String, String>;
pub type RouteSegmentList = Vec<RouteSegment>;
pub(crate) type PathComponentList<'a> = Vec<&'a str>;
```
# Path: hyperlane/src/route/impl.rs
```rust
use super::*;
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
                        if !other_routes
                            .iter()
                            .any(|entry: &(RoutePattern, ServerHookHandler)| &entry.0 == pattern)
                        {
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
                        if !other_routes
                            .iter()
                            .any(|entry: &(RoutePattern, ServerHookHandler)| &entry.0 == pattern)
                        {
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
            (Self::Static(left_static), Self::Static(right_static)) => {
                left_static.cmp(right_static)
            }
            (Self::Dynamic(left_dynamic), Self::Dynamic(right_dynamic)) => {
                left_dynamic.cmp(right_dynamic)
            }
            (Self::Regex(left_name, left_regex), Self::Regex(right_name, right_regex)) => left_name
                .cmp(right_name)
                .then_with(|| left_regex.as_str().cmp(right_regex.as_str())),
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
            (Self::Static(left_value), Self::Static(right_value)) => left_value == right_value,
            (Self::Dynamic(left_value), Self::Dynamic(right_value)) => left_value == right_value,
            (Self::Regex(left_name, left_regex), Self::Regex(right_name, right_regex)) => {
                left_name == right_name && left_regex.as_str() == right_regex.as_str()
            }
            _ => false,
        }
    }
}
impl Hash for RouteSegment {
    #[inline(always)]
    fn hash<H: Hasher>(&self, state: &mut H) {
        match self {
            Self::Static(static_value) => {
                0u8.hash(state);
                static_value.hash(state);
            }
            Self::Dynamic(dynamic_value) => {
                1u8.hash(state);
                dynamic_value.hash(state);
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
    fn try_match_static_path(&self, path: &str) -> Option<RouteParams> {
        let route_segments_len: usize = self.get_0().len();
        let path_bytes: &[u8] = path.as_bytes();
        let path_separator_byte: u8 = DEFAULT_HTTP_PATH_BYTES[0];
        let mut segment_start: usize = 0;
        let mut matched_segments: usize = 0;
        let mut saw_content: bool = false;
        for (byte_index, &current_byte) in path_bytes.iter().enumerate() {
            if current_byte == path_separator_byte {
                saw_content = true;
                let expected: &str = match self.get_0().get(matched_segments) {
                    Some(RouteSegment::Static(s)) => s.as_str(),
                    Some(_) => return None,
                    None => return None,
                };
                if &path[segment_start..byte_index] != expected {
                    return None;
                }
                matched_segments += 1;
                segment_start = byte_index + 1;
            }
        }
        if segment_start < path.len() {
            saw_content = true;
            let expected: &str = match self.get_0().get(matched_segments) {
                Some(RouteSegment::Static(s)) => s.as_str(),
                Some(_) => return None,
                None => return None,
            };
            if &path[segment_start..] != expected {
                return None;
            }
            matched_segments += 1;
        }
        let all_matched: bool = matched_segments == route_segments_len;
        let empty_single_match: bool = !saw_content && route_segments_len == 1 && path.is_empty();
        if all_matched || empty_single_match {
            Some(hash_map_xx_hash3_64())
        } else {
            None
        }
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
        if self.is_static() {
            return self.try_match_static_path(path);
        }
        let mut path_segments: PathComponentList = Vec::with_capacity(route_segments_len);
        let path_bytes: &[u8] = path.as_bytes();
        let path_separator_byte: u8 = DEFAULT_HTTP_PATH_BYTES[0];
        let mut segment_start: usize = 0;
        for (byte_index, &current_byte) in path_bytes.iter().enumerate() {
            if current_byte == path_separator_byte {
                if segment_start < byte_index {
                    path_segments.push(&path[segment_start..byte_index]);
                }
                segment_start = byte_index + 1;
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
            .all(|segment: &RouteSegment| matches!(segment, RouteSegment::Static(_)))
    }
    #[inline(always)]
    pub(crate) fn is_dynamic(&self) -> bool {
        self.get_0()
            .iter()
            .any(|segment: &RouteSegment| matches!(segment, RouteSegment::Dynamic(_)))
            && self
                .get_0()
                .iter()
                .all(|segment: &RouteSegment| !matches!(segment, RouteSegment::Regex(_, _)))
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
        match routes_for_count.binary_search_by(|entry: &(RoutePattern, ServerHookHandler)| {
            entry.0.cmp(&route_pattern)
        }) {
            Ok(_) => return Err(RouteError::DuplicatePattern(pattern.to_owned())),
            Err(pos) => routes_for_count.insert(pos, (route_pattern, hook)),
        }
        Ok(())
    }
    pub fn try_resolve_route<'a>(
        &'a self,
        ctx: &mut Context,
        path: &str,
    ) -> Option<&'a ServerHookHandler> {
        if let Some(hook) = self.get_static_route().get(path) {
            return Some(hook);
        }
        let path_segment_count: usize = Self::count_path_segments(path);
        if let Some(routes) = self.get_dynamic_route().get(&path_segment_count) {
            for (pattern, hook) in routes {
                if let Some(params) = pattern.try_match_path(path) {
                    ctx.set_route_params(params);
                    return Some(hook);
                }
            }
        }
        if let Some(routes) = self.get_regex_route().get(&path_segment_count) {
            for (pattern, hook) in routes {
                if let Some(params) = pattern.try_match_path(path) {
                    ctx.set_route_params(params);
                    return Some(hook);
                }
            }
        }
        for (&segment_count, routes) in self.get_regex_route() {
            if segment_count >= path_segment_count {
                continue;
            }
            for (pattern, hook) in routes {
                if pattern.has_tail_regex()
                    && let Some(params) = pattern.try_match_path(path)
                {
                    ctx.set_route_params(params);
                    return Some(hook);
                }
            }
        }
        None
    }
}
```
# Path: hyperlane/src/route/mod.rs
```rust
mod r#enum;
mod r#impl;
mod r#struct;
mod r#type;
pub use {r#enum::*, r#struct::*, r#type::*};
use super::*;
```
# Path: hyperlane/src/error/enum.rs
```rust
use super::*;
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
# Path: hyperlane/src/error/impl.rs
```rust
use super::*;
impl From<std::io::Error> for ServerError {
    #[inline(always)]
    fn from(error: std::io::Error) -> Self {
        ServerError::TcpBind(error.to_string())
    }
}
```
# Path: hyperlane/src/error/mod.rs
```rust
mod r#enum;
mod r#impl;
pub use r#enum::*;
use super::*;
```
# Path: hyperlane/tests/mod.rs
```rust
mod config;
mod context;
mod error;
mod route;
mod server;
use hyperlane::*;
use std::{
    sync::{Arc, OnceLock},
    time::{Duration, Instant},
};
use tokio::{spawn, task::JoinHandle, time::sleep};
```
# Path: hyperlane/tests/config/mod.rs
```rust
mod r#fn;
use super::*;
```
# Path: hyperlane/tests/config/fn.rs
```rust
use super::*;
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
# Path: hyperlane/tests/context/mod.rs
```rust
mod r#fn;
use super::*;
```
# Path: hyperlane/tests/context/fn.rs
```rust
use super::*;
#[test]
fn context_ref_from_address() {
    let ctx: Context = Context::default();
    let ctx_address: usize = (&ctx).into();
    let ctx_ref: &Context = ctx_address.into();
    assert_eq!(&ctx, ctx_ref);
}
#[test]
fn context_mut_from_address() {
    let mut ctx: Context = Context::default();
    let ctx_address: usize = (&mut ctx).into();
    let ctx_mut: &mut Context = ctx_address.into();
    assert_eq!(&mut ctx, ctx_mut);
}
#[test]
fn context_ref_into_address() {
    let ctx: Context = Context::default();
    let ctx_address: usize = (&ctx).into();
    assert!(ctx_address > 0);
}
#[test]
fn context_mut_into_address() {
    let mut ctx: Context = Context::default();
    let ctx_address: usize = (&mut ctx).into();
    assert!(ctx_address > 0);
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
    assert_eq!(ctx.get_request(), ctx_ref.get_request());
    assert_eq!(ctx.get_response(), ctx_ref.get_response());
}
#[test]
fn context_as_mut() {
    let mut ctx: Context = Context::default();
    let new_ctx: Context = ctx.as_mut().clone();
    assert_eq!(ctx, new_ctx);
}
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
# Path: hyperlane/tests/server/struct.rs
```rust
use super::*;
pub(crate) struct TestSendRoute;
pub(crate) struct TaskPanicHook {
    pub(crate) response_body: String,
    pub(crate) content_type: String,
}
pub(crate) struct RequestErrorHook {
    pub(crate) response_status_code: ResponseStatusCode,
    pub(crate) response_body: String,
}
pub(crate) struct RequestMiddleware {
    pub(crate) socket_addr: String,
}
pub(crate) struct UpgradeMiddleware;
pub(crate) struct ResponseMiddleware;
pub(crate) struct RootRoute {
    pub(crate) response_body: String,
    pub(crate) cookie1: String,
    pub(crate) cookie2: String,
}
pub(crate) struct SseRoute;
pub(crate) struct WebsocketRoute;
pub(crate) struct DynamicRoute {
    pub(crate) params: RouteParams,
}
pub(crate) struct GetAllRoutes;
```
# Path: hyperlane/tests/server/static.rs
```rust
use super::*;
pub(crate) static SERVER_REF: OnceLock<Server> = OnceLock::new();
```
# Path: hyperlane/tests/server/impl.rs
```rust
use super::*;
impl ServerHook for TestSendRoute {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    async fn handle(self, _: &mut Stream, _: &mut Context) -> Status {
        Status::Continue
    }
}
impl ServerHook for TaskPanicHook {
    async fn new(_: &mut Stream, ctx: &mut Context) -> Self {
        let error: PanicData = ctx.try_get_task_panic_data().unwrap_or_default();
        let response_body: String = error.to_string();
        let content_type: String = ContentType::format_content_type_with_charset(TEXT_PLAIN, UTF8);
        Self {
            response_body,
            content_type,
        }
    }
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        let data: Vec<u8> = ctx
            .get_mut_response()
            .set_version(HttpVersion::Http1_1)
            .set_status_code(500)
            .clear_headers()
            .set_header(SERVER, HYPERLANE)
            .set_header(CONTENT_TYPE, &self.content_type)
            .set_body(&self.response_body)
            .build();
        if stream.try_send(data).await.is_err() {
            stream.set_closed(true);
            return Status::Reject;
        }
        Status::Continue
    }
}
impl ServerHook for RequestErrorHook {
    async fn new(_: &mut Stream, ctx: &mut Context) -> Self {
        let request_error: RequestError = ctx.try_get_request_error_data().unwrap_or_default();
        Self {
            response_status_code: request_error.get_http_status_code(),
            response_body: request_error.to_string(),
        }
    }
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        let data: Vec<u8> = ctx
            .get_mut_response()
            .set_version(HttpVersion::Http1_1)
            .set_status_code(self.response_status_code)
            .set_body(self.response_body)
            .build();
        if stream.try_send(data).await.is_err() {
            stream.set_closed(true);
            return Status::Reject;
        }
        Status::Continue
    }
}
impl ServerHook for RequestMiddleware {
    async fn new(stream: &mut Stream, _: &mut Context) -> Self {
        let mut socket_addr: String = String::new();
        socket_addr = stream
            .get_stream()
            .peer_addr()
            .map(|data| data.to_string())
            .unwrap_or_default();
        Self { socket_addr }
    }
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        ctx.get_mut_response()
            .set_version(HttpVersion::Http1_1)
            .set_status_code(200)
            .set_header(SERVER, HYPERLANE)
            .set_header(CONNECTION, KEEP_ALIVE)
            .set_header(CONTENT_TYPE, TEXT_PLAIN)
            .set_header(ACCESS_CONTROL_ALLOW_ORIGIN, WILDCARD_ANY)
            .set_header("SocketAddr", &self.socket_addr);
        Status::Continue
    }
}
impl ServerHook for UpgradeMiddleware {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        if !ctx.get_request().is_ws_upgrade_type() {
            return Status::Continue;
        }
        if let Some(key) = &ctx.get_request().try_get_header_back(SEC_WEBSOCKET_KEY) {
            let accept_key: String = WebSocketFrame::generate_accept_key(key);
            let data: Vec<u8> = ctx
                .get_mut_response()
                .set_version(HttpVersion::Http1_1)
                .set_status_code(101)
                .set_header(UPGRADE, WEBSOCKET)
                .set_header(CONNECTION, UPGRADE)
                .set_header(SEC_WEBSOCKET_ACCEPT, &accept_key)
                .set_body(Vec::new())
                .build();
            if stream.try_send(data).await.is_err() {
                stream.set_closed(true);
                return Status::Reject;
            }
        }
        Status::Continue
    }
}
impl ServerHook for ResponseMiddleware {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        if ctx.get_request().is_ws_upgrade_type() {
            return Status::Continue;
        }
        let data: Vec<u8> = ctx.get_mut_response().build();
        if stream.try_send(data).await.is_err() {
            stream.set_closed(true);
            return Status::Reject;
        }
        Status::Continue
    }
}
impl ServerHook for RootRoute {
    async fn new(_: &mut Stream, ctx: &mut Context) -> Self {
        let response_body: String = format!("Hello hyperlane => {}", ctx.get_request().get_path());
        let cookie1: String = CookieBuilder::new("key1", "value1").http_only().build();
        let cookie2: String = CookieBuilder::new("key2", "value2").http_only().build();
        Self {
            response_body,
            cookie1,
            cookie2,
        }
    }
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        ctx.get_mut_response()
            .add_header(SET_COOKIE, &self.cookie1)
            .add_header(SET_COOKIE, &self.cookie2)
            .set_body(&self.response_body);
        Status::Continue
    }
}
impl ServerHook for SseRoute {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        let data: Vec<u8> = ctx
            .get_mut_response()
            .set_header(CONTENT_TYPE, TEXT_EVENT_STREAM)
            .set_body(Vec::new())
            .build();
        if stream.try_send(data).await.is_err() {
            stream.set_closed(true);
            return Status::Reject;
        }
        for i in 0..10 {
            let body: String = format!("data:{i}{HTTP_DOUBLE_BR}");
            if stream.try_send(&body).await.is_err() {
                break;
            }
        }
        stream.set_closed(true);
        Status::Reject
    }
}
impl WebsocketRoute {
    pub async fn try_send_body_hook(
        &self,
        stream: &mut Stream,
        ctx: &mut Context,
    ) -> Result<(), ResponseError> {
        let send_result: Result<(), ResponseError> = if ctx.get_request().is_ws_upgrade_type() {
            let body: &ResponseBody = ctx.get_response().get_body();
            let frame_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(body);
            stream.try_send_list(&frame_list).await
        } else {
            let body: &Vec<u8> = ctx.get_response().get_body();
            stream.try_send(body).await
        };
        if send_result.is_err() {
            stream.set_closed(true);
        }
        send_result
    }
}
impl ServerHook for WebsocketRoute {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        while let Ok(body) = stream.try_get_websocket_request().await {
            ctx.get_mut_response().set_body(body);
            if self.try_send_body_hook(stream, ctx).await.is_err() {
                return Status::Reject;
            }
        }
        Status::Continue
    }
}
impl ServerHook for DynamicRoute {
    async fn new(_: &mut Stream, ctx: &mut Context) -> Self {
        Self {
            params: ctx.get_route_params().clone(),
        }
    }
    async fn handle(mut self, _: &mut Stream, _: &mut Context) -> Status {
        self.params.insert("key".to_owned(), "value".to_owned());
        panic!("Test panic {:?}", self.params);
    }
}
impl ServerHook for GetAllRoutes {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        if let Some(server) = SERVER_REF.get() {
            let route_matcher: &RouteMatcher = server.get_route_matcher();
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
        Status::Continue
    }
}
```
# Path: hyperlane/tests/server/mod.rs
```rust
mod r#fn;
mod r#impl;
mod r#static;
mod r#struct;
pub(crate) use {r#static::*, r#struct::*};
use super::*;
```
# Path: hyperlane/tests/server/fn.rs
```rust
use super::*;
#[test]
fn server_partial_eq() {
    let server1: Server = Server::default();
    let server2: Server = Server::default();
    assert_eq!(server1, server2);
    let server1_clone: Server = server1.clone();
    assert_eq!(server1, server1_clone);
}
#[test]
fn server_from_address() {
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
fn server_ref_from_address() {
    let mut server: Server = Server::default();
    server.set_server_config(ServerConfig::default());
    let server_address: usize = (&server).into();
    let server_ref: &Server = server_address.into();
    assert_eq!(server.get_server_config(), server_ref.get_server_config());
}
#[test]
fn server_mut_from_address() {
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
fn server_ref_into_address() {
    let server: Server = Server::default();
    let server_address: usize = (&server).into();
    assert!(server_address > 0);
}
#[test]
fn server_mut_into_address() {
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
    let _: Result<(), Server> = SERVER_REF.set(server.clone());
    let server_control_hook_1: ServerControlHook = server.run().await.unwrap_or_default();
    let server_control_hook_2: ServerControlHook = server_control_hook_1.clone();
    spawn(async move {
        sleep(Duration::from_secs(60)).await;
        server_control_hook_2.shutdown().await;
    });
    server_control_hook_1.wait().await;
}
```
# Path: hyperlane/tests/route/struct.rs
```rust
pub(crate) struct TestRoute {
    pub data: String,
}
```
# Path: hyperlane/tests/route/impl.rs
```rust
use super::*;
impl ServerHook for TestRoute {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self {
            data: String::new(),
        }
    }
    async fn handle(mut self, _: &mut Stream, _: &mut Context) -> Status {
        self.data = String::from("test");
        Status::Continue
    }
}
```
# Path: hyperlane/tests/route/mod.rs
```rust
mod r#fn;
mod r#impl;
mod r#struct;
pub(crate) use r#struct::*;
use super::*;
```
# Path: hyperlane/tests/route/fn.rs
```rust
use super::*;
#[tokio::test]
#[should_panic(expected = "EmptyPattern")]
async fn empty_route() {
    let _server: &Server = Server::default().route::<TestRoute>(EMPTY_STR);
}
#[tokio::test]
#[should_panic(expected = "DuplicatePattern")]
async fn duplicate_route() {
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
        let _: Option<&ServerHookHandler> = route_matcher.try_resolve_route(&mut ctx, &path);
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
        let _: Option<&ServerHookHandler> = route_matcher.try_resolve_route(&mut ctx, &path);
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
        let _: Option<&ServerHookHandler> = route_matcher.try_resolve_route(&mut ctx, &path);
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
# Path: hyperlane/tests/error/mod.rs
```rust
mod r#fn;
use super::*;
```
# Path: hyperlane/tests/error/fn.rs
```rust
use super::*;
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
# Path: hyperlane-macros/README.md
## hyperlane-macros
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
- `#[is_get_method]` - GET method handler
- `#[is_post_method]` - POST method handler
- `#[is_put_method]` - PUT method handler
- `#[is_delete_method]` - DELETE method handler
- `#[is_patch_method]` - PATCH method handler
- `#[is_head_method]` - HEAD method handler
- `#[is_options_method]` - OPTIONS method handler
- `#[is_connect_method]` - CONNECT method handler
- `#[is_trace_method]` - TRACE method handler
- `#[is_unknown_method]` - Unknown method handler
### HTTP Version Macros
- `#[is_http0_9_version]` - HTTP/0.9 check, ensures function only executes for HTTP/0.9 protocol requests
- `#[is_http1_0_version]` - HTTP/1.0 check, ensures function only executes for HTTP/1.0 protocol requests
- `#[is_http1_1_version]` - HTTP/1.1 check, ensures function only executes for HTTP/1.1 protocol requests
- `#[is_http2_version]` - HTTP/2 check, ensures function only executes for HTTP/2 protocol requests
- `#[is_http3_version]` - HTTP/3 check, ensures function only executes for HTTP/3 protocol requests
- `#[is_http1_1_or_higher_version]` - HTTP/1.1 or higher version check, ensures function only executes for HTTP/1.1 or newer protocol versions
- `#[is_http_version]` - HTTP check, ensures function only executes for standard HTTP requests
- `#[is_unknown_version]` - Unknown version check, ensures function only executes for requests with unknown HTTP versions
### Upgrade type Macros
- `#[is_ws_upgrade_type]` - WebSocket check, ensures function only executes for WebSocket upgrade requests
- `#[is_h2c_upgrade_type]` - HTTP/2 Cleartext check, ensures function only executes for HTTP/2 cleartext requests
- `#[is_tls_upgrade_type]` - TLS check, ensures function only executes for TLS-secured connections
- `#[is_unknown_upgrade_type]` - Unknown upgrade type check, ensures function only executes for requests with unknown upgrade types
### Response Setting Macros
- `#[response_status_code(code)]` - Set response status code (supports literals and global constants)
- `#[response_reason_phrase("phrase")]` - Set response reason phrase (supports literals and global constants)
- `#[response_header("key", "value")]` - Add response header (supports literals and global constants)
- `#[response_header("key" => "value")]` - Set response header (supports literals and global constants)
- `#[response_body("data")]` - Set response body (supports literals and global constants)
- `#[response_version(version)]` - Set response HTTP version (supports literals and global constants)
- `#[clear_response_headers]` - Clear all response headers
### Send Operation Macros
- `#[try_send]` - Try to send data via stream after function execution (returns Result). Defaults to sending the response built from context.
- `#[try_send(data_expr)]` - Try to send the specified data expression via stream after function execution (returns Result)
- `#[send]` - Send data via stream after function execution (**panics on failure**). Defaults to sending the response built from context.
- `#[send(data_expr)]` - Send the specified data expression via stream after function execution (**panics on failure**)
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
- `#[try_get_attribute(key => variable_name: type)]` - Extract a specific attribute by key into a typed variable
- `#[try_get_attribute("key1" => var1: Type1, "key2" => var2: Type2, ...)]` - Supports multiple attribute extraction
- `#[attribute(key => variable_name: type)]` - Extract a specific attribute by key into a typed variable
- `#[attribute("key1" => var1: Type1, "key2" => var2: Type2, ...)]` - Supports multiple attribute extraction
### Attributes Macros
- `#[attributes(variable_name)]` - Get all attributes as a HashMap for comprehensive attribute access
- `#[attributes(var1, var2, ...)]` - Supports multiple attribute collections
### Panic Data Macros
- `#[try_get_task_panic_data(variable_name)]` - Extract panic data into a variable wrapped in Option type
- `#[try_get_task_panic_data(var1, var2, ...)]` - Supports multiple panic data variables
- `#[task_panic_data(variable_name)]` - Extract panic data into a variable with panic on missing value
- `#[task_panic_data(var1, var2, ...)]` - Supports multiple panic data variables
### Request Error Data Macros
- `#[try_get_request_error_data(variable_name)]` - Extract request error data into a variable wrapped in Option type
- `#[try_get_request_error_data(var1, var2, ...)]` - Supports multiple request error data variables
- `#[request_error_data(variable_name)]` - Extract request error data into a variable with panic on missing value
- `#[request_error_data(var1, var2, ...)]` - Supports multiple request error data variables
### Route Param Macros
- `#[try_get_route_param(key => variable_name)]` - Extract a specific route parameter by key into a variable
- `#[try_get_route_param("key1" => var1, "key2" => var2, ...)]` - Supports multiple route parameter extraction
- `#[route_param(key => variable_name)]` - Extract a specific route parameter by key into a variable
- `#[route_param("key1" => var1, "key2" => var2, ...)]` - Supports multiple route parameter extraction
### Route Params Macros
- `#[route_params(variable_name)]` - Get all route parameters as a collection
- `#[route_params(var1, var2, ...)]` - Supports multiple route parameter collections
### Request Query Macros
- `#[try_get_request_query(key => variable_name)]` - Extract a specific query parameter by key from the URL query string
- `#[try_get_request_query("key1" => var1, "key2" => var2, ...)]` - Supports multiple query parameter extraction
- `#[request_query(key => variable_name)]` - Extract a specific query parameter by key from the URL query string
- `#[request_query("key1" => var1, "key2" => var2, ...)]` - Supports multiple query parameter extraction
### Request Querys Macros
- `#[request_querys(variable_name)]` - Get all query parameters as a collection
- `#[request_querys(var1, var2, ...)]` - Supports multiple query parameter collections
### Request Header Macros
- `#[try_get_request_header(key => variable_name)]` - Extract a specific HTTP header by name from the request
- `#[try_get_request_header(KEY1 => var1, KEY2 => var2, ...)]` - Supports multiple header extraction
- `#[request_header(key => variable_name)]` - Extract a specific HTTP header by name from the request
- `#[request_header(KEY1 => var1, KEY2 => var2, ...)]` - Supports multiple header extraction
### Request Headers Macros
- `#[request_headers(variable_name)]` - Get all HTTP headers as a collection
- `#[request_headers(var1, var2, ...)]` - Supports multiple header collections
### Request Cookie Macros
- `#[try_get_request_cookie(key => variable_name)]` - Extract a specific cookie value by key from the request cookie header
- `#[try_get_request_cookie("key1" => var1, "key2" => var2, ...)]` - Supports multiple cookie extraction
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
- `#[try_get_http_request]` - Wraps function body with HTTP stream processing. The function body only executes if data is successfully read from the HTTP stream.
- `#[try_get_http_request(variable_name)]` - Wraps function body with HTTP stream processing, storing data in specified variable name.
- `#[try_get_websocket_request]` - Wraps function body with WebSocket stream processing. The function body only executes if data is successfully read from the WebSocket stream.
- `#[try_get_websocket_request(variable_name)]` - Wraps function body with WebSocket stream processing, storing data in specified variable name.
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
# Path: hyperlane-macros/src/lib.rs
```rust
﻿
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
    closed::*, common::*, context::*, filter::*, flush::*, from_stream::*, hook::*, host::*,
    hyperlane::*, inject::*, method::*, referer::*, reject::*, request::*, request_middleware::*,
    response::*, response_middleware::*, route::*, send::*, stream::*, upgrade::*, version::*,
};
use {
    proc_macro::TokenStream,
    proc_macro2::Span,
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
pub fn try_get_websocket_request(attr: TokenStream, item: TokenStream) -> TokenStream {
    try_get_websocket_request_macro(attr, item)
}
#[proc_macro_attribute]
pub fn try_get_http_request(attr: TokenStream, item: TokenStream) -> TokenStream {
    try_get_http_request_macro(attr, item)
}
#[proc_macro_attribute]
pub fn is_get_method(_attr: TokenStream, item: TokenStream) -> TokenStream {
    is_get_method_handler(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn is_post_method(_attr: TokenStream, item: TokenStream) -> TokenStream {
    is_post_method_handler(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn is_put_method(_attr: TokenStream, item: TokenStream) -> TokenStream {
    is_put_method_handler(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn is_delete_method(_attr: TokenStream, item: TokenStream) -> TokenStream {
    is_delete_method_handler(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn is_patch_method(_attr: TokenStream, item: TokenStream) -> TokenStream {
    is_patch_method_handler(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn is_head_method(_attr: TokenStream, item: TokenStream) -> TokenStream {
    is_head_method_handler(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn is_options_method(_attr: TokenStream, item: TokenStream) -> TokenStream {
    is_options_method_handler(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn is_connect_method(_attr: TokenStream, item: TokenStream) -> TokenStream {
    is_connect_method_handler(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn is_trace_method(_attr: TokenStream, item: TokenStream) -> TokenStream {
    is_trace_method_handler(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn is_unknown_method(_attr: TokenStream, item: TokenStream) -> TokenStream {
    is_unknown_method_handler(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn methods(attr: TokenStream, item: TokenStream) -> TokenStream {
    methods_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn is_http0_9_version(_attr: TokenStream, item: TokenStream) -> TokenStream {
    is_http0_9_version_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn is_http1_0_version(_attr: TokenStream, item: TokenStream) -> TokenStream {
    is_http1_0_version_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn is_http1_1_version(_attr: TokenStream, item: TokenStream) -> TokenStream {
    is_http1_1_version_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn is_http2_version(_attr: TokenStream, item: TokenStream) -> TokenStream {
    is_http2_version_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn is_http3_version(_attr: TokenStream, item: TokenStream) -> TokenStream {
    is_http3_version_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn is_http1_1_or_higher_version(_attr: TokenStream, item: TokenStream) -> TokenStream {
    is_http1_1_or_higher_version_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn is_http_version(_attr: TokenStream, item: TokenStream) -> TokenStream {
    is_http_version_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn is_unknown_version(_attr: TokenStream, item: TokenStream) -> TokenStream {
    is_unknown_version_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn is_ws_upgrade_type(_attr: TokenStream, item: TokenStream) -> TokenStream {
    is_ws_upgrade_type_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn is_h2c_upgrade_type(_attr: TokenStream, item: TokenStream) -> TokenStream {
    is_h2c_upgrade_type_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn is_tls_upgrade_type(_attr: TokenStream, item: TokenStream) -> TokenStream {
    is_tls_upgrade_type_macro(item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn is_unknown_upgrade_type(_attr: TokenStream, item: TokenStream) -> TokenStream {
    is_unknown_upgrade_type_macro(item, Position::Prologue)
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
pub fn try_get_attribute(attr: TokenStream, item: TokenStream) -> TokenStream {
    try_get_attribute_macro(attr, item, Position::Prologue)
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
pub fn try_get_task_panic_data(attr: TokenStream, item: TokenStream) -> TokenStream {
    try_get_task_panic_data_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn task_panic_data(attr: TokenStream, item: TokenStream) -> TokenStream {
    task_panic_data_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn try_get_request_error_data(attr: TokenStream, item: TokenStream) -> TokenStream {
    try_get_request_error_data_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn request_error_data(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_error_data_macro(attr, item, Position::Prologue)
}
#[proc_macro_attribute]
pub fn try_get_route_param(attr: TokenStream, item: TokenStream) -> TokenStream {
    try_get_route_param_macro(attr, item, Position::Prologue)
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
pub fn try_get_request_query(attr: TokenStream, item: TokenStream) -> TokenStream {
    try_get_request_query_macro(attr, item, Position::Prologue)
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
pub fn try_get_request_header(attr: TokenStream, item: TokenStream) -> TokenStream {
    try_get_request_header_macro(attr, item, Position::Prologue)
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
pub fn try_get_request_cookie(attr: TokenStream, item: TokenStream) -> TokenStream {
    try_get_request_cookie_macro(attr, item, Position::Prologue)
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
pub fn try_send(attr: TokenStream, item: TokenStream) -> TokenStream {
    try_send_macro(attr, item, Position::Epilogue)
}
#[proc_macro_attribute]
pub fn send(attr: TokenStream, item: TokenStream) -> TokenStream {
    send_macro(attr, item, Position::Epilogue)
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
# Path: hyperlane-macros/src/hook/mod.rs
```rust
mod r#fn;
pub(crate) use r#fn::*;
use super::*;
```
# Path: hyperlane-macros/src/hook/fn.rs
```rust
use super::*;
pub(crate) fn task_panic_macro(attr: TokenStream, item: TokenStream) -> TokenStream {
    let attr_args: OrderAttr = parse_macro_input!(attr as OrderAttr);
    let order: proc_macro2::TokenStream = expr_to_isize(&attr_args.order);
    let input_struct: ItemStruct = parse_macro_input!(item as ItemStruct);
    let struct_name: &Ident = &input_struct.ident;
    let gen_code: proc_macro2::TokenStream = quote! {
        #input_struct
        ::hyperlane::inventory::submit! {
            ::hyperlane::HookType::TaskPanic(#order, || ::hyperlane::Hook::factory::<#struct_name>())
        }
    };
    gen_code.into()
}
pub(crate) fn request_error_macro(attr: TokenStream, item: TokenStream) -> TokenStream {
    let attr_args: OrderAttr = parse_macro_input!(attr as OrderAttr);
    let order: proc_macro2::TokenStream = expr_to_isize(&attr_args.order);
    let input_struct: ItemStruct = parse_macro_input!(item as ItemStruct);
    let struct_name: &Ident = &input_struct.ident;
    let gen_code: proc_macro2::TokenStream = quote! {
        #input_struct
        ::hyperlane::inventory::submit! {
            ::hyperlane::HookType::RequestError(#order, || ::hyperlane::Hook::factory::<#struct_name>())
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
    inject(position, item, |context, stream| {
        let hook_calls = functions.iter().map(|function_expr| {
            quote! {
                let _ = #function_expr(#stream, #context).await;
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
    inject(position, item, |context, stream| {
        let hook_calls = functions.iter().map(|function_expr| {
            quote! {
                let _ = #function_expr(#stream, #context).await;
            }
        });
        quote! {
            #(#hook_calls)*
        }
    })
}
```
# Path: hyperlane-macros/src/from_stream/struct.rs
```rust
use super::*;
pub(crate) struct FromStreamData {
    pub(crate) variable_name: Option<Expr>,
}
```
# Path: hyperlane-macros/src/from_stream/impl.rs
```rust
use super::*;
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
# Path: hyperlane-macros/src/from_stream/mod.rs
```rust
mod r#impl;
mod r#struct;
pub(crate) use r#struct::*;
use super::*;
```
# Path: hyperlane-macros/src/stream/mod.rs
```rust
mod r#fn;
pub(crate) use r#fn::*;
use super::*;
```
# Path: hyperlane-macros/src/stream/fn.rs
```rust
use super::*;
pub(crate) fn generate_http_stream(
    stream: &Ident,
    context: &Ident,
    data: &FromStreamData,
    stmts: &[Stmt],
) -> proc_macro2::TokenStream {
    let method_ident: Ident = Ident::new("try_get_http_request", Span::call_site());
    match data.variable_name.clone() {
        Some(variable_name) => {
            quote! {
                while let Ok(#variable_name) = #stream.#method_ident().await {
                    #context.set_request(#variable_name.clone());
                    #(#stmts)*
                }
                ::hyperlane::Status::Continue
            }
        }
        None => {
            quote! {
                while let Ok(_request) = #stream.#method_ident().await {
                    #context.set_request(_request);
                    #(#stmts)*
                }
                ::hyperlane::Status::Continue
            }
        }
    }
}
pub(crate) fn generate_websocket_stream(
    stream: &Ident,
    context: &Ident,
    data: &FromStreamData,
    stmts: &[Stmt],
) -> proc_macro2::TokenStream {
    let method_ident: Ident = Ident::new("try_get_websocket_request", Span::call_site());
    match data.variable_name.clone() {
        Some(variable_name) => {
            quote! {
                while let Ok(#variable_name) = #stream.#method_ident().await {
                    #context.get_mut_request().set_body(#variable_name.clone());
                    #(#stmts)*
                }
                ::hyperlane::Status::Continue
            }
        }
        None => {
            quote! {
                while let Ok(_body) = #stream.#method_ident().await {
                    #context.get_mut_request().set_body(_body);
                    #(#stmts)*
                }
                ::hyperlane::Status::Continue
            }
        }
    }
}
pub(crate) fn try_get_http_request_macro(attr: TokenStream, item: TokenStream) -> TokenStream {
    let data: FromStreamData = parse_macro_input!(attr as FromStreamData);
    let input_fn: ItemFn = parse_macro_input!(item as ItemFn);
    let vis: &Visibility = &input_fn.vis;
    let sig: &Signature = &input_fn.sig;
    let block: &Block = &input_fn.block;
    let attrs: &Vec<Attribute> = &input_fn.attrs;
    match parse_stream_from_signature(sig) {
        Ok(stream) => match parse_context_from_signature(sig) {
            Ok(context) => {
                let stmts: &Vec<Stmt> = &block.stmts;
                let loop_stream: proc_macro2::TokenStream =
                    generate_http_stream(&stream, &context, &data, stmts);
                quote! {
                    #(#attrs)*
                    #vis #sig {
                        #loop_stream
                    }
                }
                .into()
            }
            Err(err) => err.to_compile_error().into(),
        },
        Err(err) => err.to_compile_error().into(),
    }
}
pub(crate) fn try_get_websocket_request_macro(attr: TokenStream, item: TokenStream) -> TokenStream {
    let data: FromStreamData = parse_macro_input!(attr as FromStreamData);
    let input_fn: ItemFn = parse_macro_input!(item as ItemFn);
    let vis: &Visibility = &input_fn.vis;
    let sig: &Signature = &input_fn.sig;
    let block: &Block = &input_fn.block;
    let attrs: &Vec<Attribute> = &input_fn.attrs;
    match parse_stream_from_signature(sig) {
        Ok(stream) => match parse_context_from_signature(sig) {
            Ok(context) => {
                let stmts: &Vec<Stmt> = &block.stmts;
                let loop_stream: proc_macro2::TokenStream =
                    generate_websocket_stream(&stream, &context, &data, stmts);
                quote! {
                    #(#attrs)*
                    #vis #sig {
                        #loop_stream
                    }
                }
                .into()
            }
            Err(err) => err.to_compile_error().into(),
        },
        Err(err) => err.to_compile_error().into(),
    }
}
```
# Path: hyperlane-macros/src/version/mod.rs
```rust
mod r#fn;
pub(crate) use r#fn::*;
use super::*;
```
# Path: hyperlane-macros/src/version/fn.rs
```rust
use super::*;
pub(crate) fn create_version_check(
    version: &proc_macro2::Ident,
) -> impl FnOnce(&Ident, &Ident) -> proc_macro2::TokenStream {
    let version_str: String = version.to_string();
    move |context: &Ident, _: &Ident| {
        let check_fn: proc_macro2::Ident = Ident::new(&format!("is_{version_str}"), context.span());
        quote! {
            if !#context.get_request().get_version().#check_fn() {
                return ::hyperlane::Status::Continue;
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
                    Span::call_site(),
                )),
            )
        }
    };
}
impl_version_check_macro!(is_http0_9_version_macro, is_http0_9_version, http0_9);
impl_version_check_macro!(is_http1_0_version_macro, is_http1_0_version, http1_0);
impl_version_check_macro!(is_http1_1_version_macro, is_http1_1_version, http1_1);
impl_version_check_macro!(is_http2_version_macro, is_http2_version, http2);
impl_version_check_macro!(is_http3_version_macro, is_http3_version, http3);
impl_version_check_macro!(
    is_http1_1_or_higher_version_macro,
    is_http1_1_or_higher_version,
    http1_1_or_higher
);
impl_version_check_macro!(is_http_version_macro, is_http_version, http);
impl_version_check_macro!(is_unknown_version_macro, is_unknown_version, unknown);
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
use super::*;
pub(crate) struct SendData {
    pub(crate) data: Expr,
}
```
# Path: hyperlane-macros/src/response/impl.rs
```rust
use super::*;
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
# Path: hyperlane-macros/src/response/mod.rs
```rust
mod r#enum;
mod r#fn;
mod r#impl;
mod r#struct;
pub(crate) use {r#enum::*, r#fn::*, r#struct::*};
use super::*;
```
# Path: hyperlane-macros/src/response/fn.rs
```rust
use super::*;
pub(crate) fn response_status_code_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let value: Expr = match parse(attr) {
        Ok(v) => v,
        Err(err) => return err.to_compile_error().into(),
    };
    inject(position, item, |context: &Ident, _: &Ident| {
        let new_context: proc_macro2::TokenStream = leak_mut_context(false, context);
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
    inject(position, item, |context: &Ident, _: &Ident| {
        let new_context: proc_macro2::TokenStream = leak_mut_context(false, context);
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
    inject(position, item, |context: &Ident, _: &Ident| {
        let new_context: proc_macro2::TokenStream = leak_mut_context(false, context);
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
    inject(position, item, |context: &Ident, _: &Ident| {
        let new_context: proc_macro2::TokenStream = leak_mut_context(false, context);
        quote! {
            #new_context.get_mut_response().set_body(&#body);
        }
    })
}
pub(crate) fn clear_response_headers_macro(item: TokenStream, position: Position) -> TokenStream {
    inject(position, item, |context: &Ident, _: &Ident| {
        let new_context: proc_macro2::TokenStream = leak_mut_context(false, context);
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
    inject(position, item, |context: &Ident, _: &Ident| {
        let new_context: proc_macro2::TokenStream = leak_mut_context(false, context);
        quote! {
            #new_context.get_mut_response().set_version(#value);
        }
    })
}
```
# Path: hyperlane-macros/src/referer/struct.rs
```rust
use super::*;
pub(crate) struct MultiRefererData {
    pub(crate) referer_values: Vec<Expr>,
}
```
# Path: hyperlane-macros/src/referer/impl.rs
```rust
use super::*;
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
# Path: hyperlane-macros/src/referer/mod.rs
```rust
mod r#fn;
mod r#impl;
mod r#struct;
pub(crate) use {r#fn::*, r#struct::*};
use super::*;
```
# Path: hyperlane-macros/src/referer/fn.rs
```rust
use super::*;
pub(crate) fn referer_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_referer: MultiRefererData = parse_macro_input!(attr as MultiRefererData);
    inject(position, item, |context: &Ident, _: &Ident| {
        let statements = multi_referer.referer_values.iter().map(|referer_value| {
            quote! {
                if #context.get_request().try_get_header_back(::hyperlane::REFERER).map_or(true, |referer_header| referer_header != #referer_value) {
                    return ::hyperlane::Status::Continue;
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
    inject(position, item, |context: &Ident, _: &Ident| {
        let statements = multi_referer.referer_values.iter().map(|referer_value| {
            quote! {
                if #context.get_request().try_get_header_back(::hyperlane::REFERER).map_or(false, |referer_header| referer_header == #referer_value) {
                    return ::hyperlane::Status::Continue;
                }
            }
        });
        quote! {
            #(#statements)*
        }
    })
}
```
# Path: hyperlane-macros/src/method/mod.rs
```rust
mod r#fn;
pub(crate) use r#fn::*;
use super::*;
```
# Path: hyperlane-macros/src/method/fn.rs
```rust
use super::*;
pub(crate) fn create_method_check(
    method: &proc_macro2::Ident,
) -> impl FnOnce(&Ident, &Ident) -> proc_macro2::TokenStream {
    let method_str: String = method.to_string();
    move |context: &Ident, _: &Ident| {
        let check_fn: proc_macro2::Ident = Ident::new(&format!("is_{method_str}"), context.span());
        quote! {
            if !#context.get_request().get_method().#check_fn() {
                return ::hyperlane::Status::Continue;
            }
        }
    }
}
pub(crate) fn methods_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
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
            inject(
                position,
                TokenStream::from(quote! { #input_fn }),
                |_: &Ident, _: &Ident| {
                    quote! {
                        if !(#(#method_checks)||*) {
                            return ::hyperlane::Status::Continue;
                        }
                    }
                },
            )
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
                    Span::call_site(),
                )),
            )
        }
    };
}
impl_http_method_macro!(is_get_method_handler, is_get_method, get);
impl_http_method_macro!(is_post_method_handler, is_post_method, post);
impl_http_method_macro!(is_put_method_handler, is_put_method, put);
impl_http_method_macro!(is_delete_method_handler, is_delete_method, delete);
impl_http_method_macro!(is_patch_method_handler, is_patch_method, patch);
impl_http_method_macro!(is_head_method_handler, is_head_method, head);
impl_http_method_macro!(is_options_method_handler, is_options_method, options);
impl_http_method_macro!(is_connect_method_handler, is_connect_method, connect);
impl_http_method_macro!(is_trace_method_handler, is_trace_method, trace);
impl_http_method_macro!(is_unknown_method_handler, is_unknown_method, unknown);
```
# Path: hyperlane-macros/src/host/struct.rs
```rust
use super::*;
pub(crate) struct MultiHostData {
    pub(crate) host_values: Vec<Expr>,
}
```
# Path: hyperlane-macros/src/host/impl.rs
```rust
use super::*;
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
# Path: hyperlane-macros/src/host/mod.rs
```rust
mod r#fn;
mod r#impl;
mod r#struct;
pub(crate) use {r#fn::*, r#struct::*};
use super::*;
```
# Path: hyperlane-macros/src/host/fn.rs
```rust
use super::*;
pub(crate) fn host_macro(attr: TokenStream, item: TokenStream, position: Position) -> TokenStream {
    let multi_host: MultiHostData = parse_macro_input!(attr as MultiHostData);
    inject(position, item, |context: &Ident, _: &Ident| {
        let statements = multi_host.host_values.iter().map(|host_value| {
            quote! {
                if #context.get_request().get_host() != #host_value {
                    return ::hyperlane::Status::Continue;
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
    inject(position, item, |context: &Ident, _: &Ident| {
        let statements = multi_host.host_values.iter().map(|host_value| {
            quote! {
                if #context.get_request().get_host() == #host_value {
                    return ::hyperlane::Status::Continue;
                }
            }
        });
        quote! {
            #(#statements)*
        }
    })
}
```
# Path: hyperlane-macros/src/request/struct.rs
```rust
use super::*;
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
# Path: hyperlane-macros/src/request/impl.rs
```rust
use super::*;
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
# Path: hyperlane-macros/src/request/mod.rs
```rust
mod r#fn;
mod r#impl;
mod r#struct;
pub(crate) use {r#fn::*, r#struct::*};
use super::*;
```
# Path: hyperlane-macros/src/request/fn.rs
```rust
use super::*;
pub(crate) fn request_body_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_body: MultiRequestBodyData = parse_macro_input!(attr as MultiRequestBodyData);
    inject(position, item, |context: &Ident, _: &Ident| {
        let new_context: proc_macro2::TokenStream = leak_context(false, context);
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
    inject(position, item, |context: &Ident, _: &Ident| {
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
    inject(position, item, |context: &Ident, _: &Ident| {
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
pub(crate) fn try_get_attribute_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_attr: MultiAttributeData = parse_macro_input!(attr as MultiAttributeData);
    inject(position, item, |context: &Ident, _: &Ident| {
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
    inject(position, item, |context: &Ident, _: &Ident| {
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
    inject(position, item, |context: &Ident, _: &Ident| {
        let new_context: proc_macro2::TokenStream = leak_context(false, context);
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
pub(crate) fn try_get_task_panic_data_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_task_panic_data: MultiPanicData = parse_macro_input!(attr as MultiPanicData);
    inject(position, item, |context: &Ident, _: &Ident| {
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
    inject(position, item, |context: &Ident, _: &Ident| {
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
pub(crate) fn try_get_request_error_data_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_error_data: MultiRequestErrorData = parse_macro_input!(attr as MultiRequestErrorData);
    inject(position, item, |context: &Ident, _: &Ident| {
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
    inject(position, item, |context: &Ident, _: &Ident| {
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
pub(crate) fn try_get_route_param_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_param: MultiRouteParamData = parse_macro_input!(attr as MultiRouteParamData);
    inject(position, item, |context: &Ident, _: &Ident| {
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
    inject(position, item, |context: &Ident, _: &Ident| {
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
    inject(position, item, |context: &Ident, _: &Ident| {
        let new_context: proc_macro2::TokenStream = leak_context(false, context);
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
pub(crate) fn try_get_request_query_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_query: MultiQueryData = parse_macro_input!(attr as MultiQueryData);
    inject(position, item, |context: &Ident, _: &Ident| {
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
    inject(position, item, |context: &Ident, _: &Ident| {
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
    inject(position, item, |context: &Ident, _: &Ident| {
        let new_context: proc_macro2::TokenStream = leak_context(false, context);
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
pub(crate) fn try_get_request_header_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_header: MultiHeaderData = parse_macro_input!(attr as MultiHeaderData);
    inject(position, item, |context: &Ident, _: &Ident| {
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
    inject(position, item, |context: &Ident, _: &Ident| {
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
    inject(position, item, |context: &Ident, _: &Ident| {
        let new_context: proc_macro2::TokenStream = leak_context(false, context);
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
pub(crate) fn try_get_request_cookie_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let multi_cookie: MultiCookieData = parse_macro_input!(attr as MultiCookieData);
    inject(position, item, |context: &Ident, _: &Ident| {
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
    inject(position, item, |context: &Ident, _: &Ident| {
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
    inject(position, item, |context: &Ident, _: &Ident| {
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
    inject(position, item, |context: &Ident, _: &Ident| {
        let new_context: proc_macro2::TokenStream = leak_context(false, context);
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
    inject(position, item, |context: &Ident, _: &Ident| {
        let new_context: proc_macro2::TokenStream = leak_context(false, context);
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
# Path: hyperlane-macros/src/send/struct.rs
```rust
use super::*;
pub(crate) struct ResponseHeaderData {
    pub(crate) key: Expr,
    pub(crate) value: Expr,
    pub(crate) operation: HeaderOperation,
}
pub(crate) struct ResponseBodyData {
    pub(crate) body: Expr,
}
```
# Path: hyperlane-macros/src/send/impl.rs
```rust
use super::*;
impl Parse for SendData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let data: Expr = input.parse()?;
        Ok(SendData { data })
    }
}
```
# Path: hyperlane-macros/src/send/mod.rs
```rust
mod r#fn;
mod r#impl;
mod r#struct;
pub(crate) use {r#fn::*, r#struct::*};
use super::*;
```
# Path: hyperlane-macros/src/send/fn.rs
```rust
use super::*;
pub(crate) fn try_send_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let data_expr: Option<Expr> = if attr.is_empty() {
        None
    } else {
        let data: SendData = parse_macro_input!(attr as SendData);
        Some(data.data)
    };
    inject(position, item, |context, stream| match data_expr {
        Some(expr) => {
            quote! {
                let _: ::std::result::Result<(), ::hyperlane::ResponseError> = #stream.try_send(#expr).await;
            }
        }
        None => {
            quote! {
                let _: ::std::result::Result<(), ::hyperlane::ResponseError> = #stream.try_send(#context.get_mut_response().build()).await;
            }
        }
    })
}
pub(crate) fn send_macro(attr: TokenStream, item: TokenStream, position: Position) -> TokenStream {
    let data_expr: Option<Expr> = if attr.is_empty() {
        None
    } else {
        let data: SendData = parse_macro_input!(attr as SendData);
        Some(data.data)
    };
    inject(position, item, |context, stream| match data_expr {
        Some(expr) => {
            quote! {
                #stream.send(#expr).await;
            }
        }
        None => {
            quote! {
                #stream.send(#context.get_mut_response().build()).await;
            }
        }
    })
}
```
# Path: hyperlane-macros/src/flush/mod.rs
```rust
mod r#fn;
pub(crate) use r#fn::*;
use super::*;
```
# Path: hyperlane-macros/src/flush/fn.rs
```rust
use super::*;
pub(crate) fn try_flush_macro(item: TokenStream, position: Position) -> TokenStream {
    inject(position, item, |_: &Ident, stream: &Ident| {
        quote! {
            let _: ::std::result::Result<(), ::hyperlane::ResponseError> = #stream.try_flush().await;
        }
    })
}
pub(crate) fn flush_macro(item: TokenStream, position: Position) -> TokenStream {
    inject(position, item, |_: &Ident, stream: &Ident| {
        quote! {
            #stream.flush().await;
        }
    })
}
```
# Path: hyperlane-macros/src/upgrade/mod.rs
```rust
mod r#fn;
pub(crate) use r#fn::*;
use super::*;
```
# Path: hyperlane-macros/src/upgrade/fn.rs
```rust
use super::*;
pub(crate) fn create_protocol_check(
    upgrade_type: &proc_macro2::Ident,
) -> impl FnOnce(&Ident, &Ident) -> proc_macro2::TokenStream {
    let upgrade_type_str: String = upgrade_type.to_string();
    move |context: &Ident, _: &Ident| {
        let check_fn: proc_macro2::Ident =
            Ident::new(&format!("is_{upgrade_type_str}"), context.span());
        quote! {
            if !#context.get_request().get_upgrade_type().#check_fn() {
                return ::hyperlane::Status::Continue;
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
                    Span::call_site(),
                )),
            )
        }
    };
}
impl_protocol_check_macro!(is_ws_upgrade_type_macro, is_ws_upgrade_type, ws);
impl_protocol_check_macro!(is_h2c_upgrade_type_macro, is_h2c_upgrade_type, h2c);
impl_protocol_check_macro!(is_tls_upgrade_type_macro, is_tls_upgrade_type, tls);
impl_protocol_check_macro!(
    is_unknown_upgrade_type_macro,
    is_unknown_upgrade_type,
    unknown
);
```
# Path: hyperlane-macros/src/context/struct.rs
```rust
use super::*;
pub(crate) struct ContextInput {
    pub(crate) source_ctx: Ident,
    pub(crate) ty: Option<Type>,
}
```
# Path: hyperlane-macros/src/context/impl.rs
```rust
use super::*;
impl Parse for ContextInput {
    fn parse(input: ParseStream) -> Result<Self> {
        let source_ctx: Ident = input.parse()?;
        let ty: Option<Type> = if input.peek(Token![:]) {
            input.parse::<Token![:]>()?;
            Some(input.parse()?)
        } else {
            None
        };
        Ok(ContextInput { source_ctx, ty })
    }
}
```
# Path: hyperlane-macros/src/context/mod.rs
```rust
mod r#fn;
mod r#impl;
mod r#struct;
pub(crate) use {r#fn::*, r#struct::*};
use super::*;
```
# Path: hyperlane-macros/src/context/fn.rs
```rust
use super::*;
pub(crate) fn is_mutable_reference_type(ty: &Type) -> bool {
    if let Type::Reference(type_ref) = ty {
        type_ref.mutability.is_some()
    } else {
        false
    }
}
pub(crate) fn context_macro(input: TokenStream) -> TokenStream {
    let context_input: ContextInput = match parse(input) {
        Ok(input) => input,
        Err(err) => return err.to_compile_error().into(),
    };
    let source_ctx: Ident = context_input.source_ctx;
    let is_mut: bool = context_input
        .ty
        .as_ref()
        .is_some_and(is_mutable_reference_type);
    if is_mut {
        leak_mut_context(true, &source_ctx).into()
    } else {
        leak_context(true, &source_ctx).into()
    }
}
```
# Path: hyperlane-macros/src/filter/mod.rs
```rust
mod r#fn;
pub(crate) use r#fn::*;
use super::*;
```
# Path: hyperlane-macros/src/filter/fn.rs
```rust
use super::*;
pub(crate) fn filter_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let condition: Expr = parse_macro_input!(attr as Expr);
    inject(position, item, |_: &Ident, _: &Ident| {
        quote! {
            if !(#condition) {
                return ::hyperlane::Status::Continue;
            }
        }
    })
}
```
# Path: hyperlane-macros/src/hyperlane/struct.rs
```rust
use super::*;
pub(crate) struct MultiHyperlaneAttr {
    pub(crate) params: Vec<(Ident, Ident)>,
}
```
# Path: hyperlane-macros/src/hyperlane/impl.rs
```rust
use super::*;
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
# Path: hyperlane-macros/src/hyperlane/mod.rs
```rust
mod r#fn;
mod r#impl;
mod r#struct;
pub(crate) use {r#fn::*, r#struct::*};
use super::*;
```
# Path: hyperlane-macros/src/hyperlane/fn.rs
```rust
use super::*;
pub(crate) fn hyperlane_macro(attr: TokenStream, item: TokenStream) -> TokenStream {
    let multi_hyperlane: MultiHyperlaneAttr = parse_macro_input!(attr as MultiHyperlaneAttr);
    let input_fn: ItemFn = parse_macro_input!(item as ItemFn);
    let vis: &Visibility = &input_fn.vis;
    let sig: &Signature = &input_fn.sig;
    let block: &Block = &input_fn.block;
    let attrs: &Vec<Attribute> = &input_fn.attrs;
    let stmts: &Vec<Stmt> = &block.stmts;
    let mut init_statements: Vec<proc_macro2::TokenStream> = Vec::new();
    for (var_name, type_name) in &multi_hyperlane.params {
        init_statements.push(quote! {
            let mut #var_name: #type_name = #type_name::default();
        });
        if type_name == SERVER_TYPE_KEY {
            init_statements.push(quote! {
                let mut hooks: Vec<::hyperlane::HookType> = ::hyperlane::inventory::iter().cloned().collect();
                ::hyperlane::HookType::assert_unique_order(hooks.clone());
                hooks.sort_by_key(|hook| hook.try_get_order());
                for hook in hooks {
                    #var_name.handle_hook(hook.clone());
                }
            });
        }
    }
    let gen_code: proc_macro2::TokenStream = quote! {
        #(#attrs)*
        #vis #sig {
            #(#init_statements)*
            #(#stmts)*
        }
    };
    gen_code.into()
}
```
# Path: hyperlane-macros/src/inject/mod.rs
```rust
mod r#fn;
pub(crate) use r#fn::*;
use super::*;
```
# Path: hyperlane-macros/src/inject/fn.rs
```rust
use super::*;
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
# Path: hyperlane-macros/src/response_middleware/mod.rs
```rust
mod r#fn;
pub(crate) use r#fn::*;
use super::*;
```
# Path: hyperlane-macros/src/response_middleware/fn.rs
```rust
use super::*;
pub(crate) fn response_middleware_macro(attr: TokenStream, item: TokenStream) -> TokenStream {
    let attr_args: OrderAttr = parse_macro_input!(attr as OrderAttr);
    let order: proc_macro2::TokenStream = expr_to_isize(&attr_args.order);
    let input_struct: ItemStruct = parse_macro_input!(item as ItemStruct);
    let struct_name: &Ident = &input_struct.ident;
    let gen_code: proc_macro2::TokenStream = quote! {
        #input_struct
        ::hyperlane::inventory::submit! {
            ::hyperlane::HookType::ResponseMiddleware(#order, || ::hyperlane::Hook::factory::<#struct_name>())
        }
    };
    gen_code.into()
}
```
# Path: hyperlane-macros/src/request_middleware/mod.rs
```rust
mod r#fn;
pub(crate) use r#fn::*;
use super::*;
```
# Path: hyperlane-macros/src/request_middleware/fn.rs
```rust
use super::*;
pub(crate) fn request_middleware_macro(attr: TokenStream, item: TokenStream) -> TokenStream {
    let attr_args: OrderAttr = parse_macro_input!(attr as OrderAttr);
    let order: proc_macro2::TokenStream = expr_to_isize(&attr_args.order);
    let input_struct: ItemStruct = parse_macro_input!(item as ItemStruct);
    let struct_name: &Ident = &input_struct.ident;
    let gen_code: proc_macro2::TokenStream = quote! {
        #input_struct
        ::hyperlane::inventory::submit! {
            ::hyperlane::HookType::RequestMiddleware(#order, || ::hyperlane::Hook::factory::<#struct_name>())
        }
    };
    gen_code.into()
}
```
# Path: hyperlane-macros/src/common/enum.rs
```rust
use super::*;
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
use super::*;
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
use super::*;
pub(crate) type MacroHandlerPosition = fn(TokenStream, Position) -> TokenStream;
pub(crate) type MacroHandlerWithAttr = fn(TokenStream, TokenStream) -> TokenStream;
pub(crate) type MacroHandlerWithAttrPosition =
    fn(TokenStream, TokenStream, Position) -> TokenStream;
```
# Path: hyperlane-macros/src/common/const.rs
```rust
pub(crate) const SERVER_TYPE_KEY: &str = "Server";
```
# Path: hyperlane-macros/src/common/static.rs
```rust
use super::*;
pub(crate) static INJECTABLE_MACROS: &[InjectableMacro] = &[
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
        name: "is_get_method",
        handler: Handler::NoAttrPosition(is_get_method_handler),
    },
    InjectableMacro {
        name: "is_post_method",
        handler: Handler::NoAttrPosition(is_post_method_handler),
    },
    InjectableMacro {
        name: "is_put_method",
        handler: Handler::NoAttrPosition(is_put_method_handler),
    },
    InjectableMacro {
        name: "is_delete_method",
        handler: Handler::NoAttrPosition(is_delete_method_handler),
    },
    InjectableMacro {
        name: "is_patch_method",
        handler: Handler::NoAttrPosition(is_patch_method_handler),
    },
    InjectableMacro {
        name: "is_head_method",
        handler: Handler::NoAttrPosition(is_head_method_handler),
    },
    InjectableMacro {
        name: "is_options_method",
        handler: Handler::NoAttrPosition(is_options_method_handler),
    },
    InjectableMacro {
        name: "is_connect_method",
        handler: Handler::NoAttrPosition(is_connect_method_handler),
    },
    InjectableMacro {
        name: "is_trace_method",
        handler: Handler::NoAttrPosition(is_trace_method_handler),
    },
    InjectableMacro {
        name: "is_unknown_method",
        handler: Handler::NoAttrPosition(is_unknown_method_handler),
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
        name: "try_get_attribute",
        handler: Handler::WithAttrPosition(try_get_attribute_macro),
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
        name: "try_get_task_panic_data",
        handler: Handler::WithAttrPosition(try_get_task_panic_data_macro),
    },
    InjectableMacro {
        name: "task_panic_data",
        handler: Handler::WithAttrPosition(task_panic_data_macro),
    },
    InjectableMacro {
        name: "try_get_request_error_data",
        handler: Handler::WithAttrPosition(try_get_request_error_data_macro),
    },
    InjectableMacro {
        name: "request_error_data",
        handler: Handler::WithAttrPosition(request_error_data_macro),
    },
    InjectableMacro {
        name: "try_get_route_param",
        handler: Handler::WithAttrPosition(try_get_route_param_macro),
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
        name: "try_get_request_query",
        handler: Handler::WithAttrPosition(try_get_request_query_macro),
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
        name: "try_get_request_header",
        handler: Handler::WithAttrPosition(try_get_request_header_macro),
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
        name: "try_get_request_cookie",
        handler: Handler::WithAttrPosition(try_get_request_cookie_macro),
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
        handler: Handler::WithAttrPosition(try_send_macro),
    },
    InjectableMacro {
        name: "send",
        handler: Handler::WithAttrPosition(send_macro),
    },
    InjectableMacro {
        name: "try_get_http_request",
        handler: Handler::WithAttr(try_get_http_request_macro),
    },
    InjectableMacro {
        name: "try_get_websocket_request",
        handler: Handler::WithAttr(try_get_websocket_request_macro),
    },
    InjectableMacro {
        name: "is_ws_upgrade_type",
        handler: Handler::NoAttrPosition(is_ws_upgrade_type_macro),
    },
    InjectableMacro {
        name: "is_h2c_upgrade_type",
        handler: Handler::NoAttrPosition(is_h2c_upgrade_type_macro),
    },
    InjectableMacro {
        name: "is_tls_upgrade_type",
        handler: Handler::NoAttrPosition(is_tls_upgrade_type_macro),
    },
    InjectableMacro {
        name: "is_unknown_upgrade_type",
        handler: Handler::NoAttrPosition(is_unknown_upgrade_type_macro),
    },
    InjectableMacro {
        name: "is_http0_9_version",
        handler: Handler::NoAttrPosition(is_http0_9_version_macro),
    },
    InjectableMacro {
        name: "is_http1_0_version",
        handler: Handler::NoAttrPosition(is_http1_0_version_macro),
    },
    InjectableMacro {
        name: "is_http1_1_version",
        handler: Handler::NoAttrPosition(is_http1_1_version_macro),
    },
    InjectableMacro {
        name: "is_http2_version",
        handler: Handler::NoAttrPosition(is_http2_version_macro),
    },
    InjectableMacro {
        name: "is_http3_version",
        handler: Handler::NoAttrPosition(is_http3_version_macro),
    },
    InjectableMacro {
        name: "is_http1_1_or_higher_version",
        handler: Handler::NoAttrPosition(is_http1_1_or_higher_version_macro),
    },
    InjectableMacro {
        name: "is_http_version",
        handler: Handler::NoAttrPosition(is_http_version_macro),
    },
    InjectableMacro {
        name: "is_unknown_version",
        handler: Handler::NoAttrPosition(is_unknown_version_macro),
    },
];
```
# Path: hyperlane-macros/src/common/impl.rs
```rust
use super::*;
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
use super::*;
```
# Path: hyperlane-macros/src/common/fn.rs
```rust
use super::*;
fn inject_at_start(
    input: TokenStream,
    before_fn: impl FnOnce(&Ident, &Ident) -> proc_macro2::TokenStream,
) -> TokenStream {
    let input_fn: ItemFn = parse_macro_input!(input as ItemFn);
    let vis: &Visibility = &input_fn.vis;
    let sig: &Signature = &input_fn.sig;
    let block: &Block = &input_fn.block;
    let attrs: &Vec<Attribute> = &input_fn.attrs;
    match parse_context_from_signature(sig) {
        Ok(context) => match parse_stream_from_signature(sig) {
            Ok(stream) => {
                let before_code: proc_macro2::TokenStream = before_fn(&context, &stream);
                let stmts: &Vec<Stmt> = &block.stmts;
                let gen_code: proc_macro2::TokenStream = quote! {
                    #(#attrs)*
                    #vis #sig {
                        #before_code
                        #(#stmts)*
                    }
                };
                gen_code.into()
            }
            Err(err) => err.to_compile_error().into(),
        },
        Err(err) => err.to_compile_error().into(),
    }
}
fn inject_at_end(
    input: TokenStream,
    after_fn: impl FnOnce(&Ident, &Ident) -> proc_macro2::TokenStream,
) -> TokenStream {
    let input_fn: ItemFn = parse_macro_input!(input as ItemFn);
    let vis: &Visibility = &input_fn.vis;
    let sig: &Signature = &input_fn.sig;
    let block: &Block = &input_fn.block;
    let attrs: &Vec<Attribute> = &input_fn.attrs;
    match parse_context_from_signature(sig) {
        Ok(context) => match parse_stream_from_signature(sig) {
            Ok(stream) => {
                let after_code: proc_macro2::TokenStream = after_fn(&context, &stream);
                let stmts: &Vec<Stmt> = &block.stmts;
                let (leading_stmts, tail_expr) = if let Some((last, leading)) = stmts.split_last() {
                    match last {
                        Stmt::Expr(expr, None) => (leading, Some(quote! { #expr })),
                        _ => (stmts.as_slice(), None),
                    }
                } else {
                    (stmts.as_slice(), None)
                };
                let normalized_leading: Vec<proc_macro2::TokenStream> = leading_stmts
                    .iter()
                    .map(|stmt| match stmt {
                        Stmt::Expr(expr, None) => quote! { #expr; },
                        _ => quote! { #stmt },
                    })
                    .collect();
                let gen_code: proc_macro2::TokenStream = match tail_expr {
                    Some(expr) => quote! {
                        #(#attrs)*
                        #vis #sig {
                            #(#normalized_leading)*
                            #after_code
                            #expr
                        }
                    },
                    None => quote! {
                        #(#attrs)*
                        #vis #sig {
                            #(#normalized_leading)*
                            #after_code
                        }
                    },
                };
                gen_code.into()
            }
            Err(err) => err.to_compile_error().into(),
        },
        Err(err) => err.to_compile_error().into(),
    }
}
pub(crate) fn inject(
    position: Position,
    input: TokenStream,
    hook: impl FnOnce(&Ident, &Ident) -> proc_macro2::TokenStream,
) -> TokenStream {
    match position {
        Position::Prologue => inject_at_start(input, hook),
        Position::Epilogue => inject_at_end(input, hook),
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
fn is_stream_type(ty: &Type) -> bool {
    if let Type::Reference(type_ref) = ty
        && let Type::Path(type_path) = &*type_ref.elem
    {
        let path: &Path = &type_path.path;
        if path.segments.len() >= 2 {
            let segments: Vec<_> = path.segments.iter().collect();
            if segments.len() >= 2 {
                let last_two: &[&PathSegment] = &segments[segments.len() - 2..];
                if last_two[0].ident == "hyperlane" && last_two[1].ident == "Stream" {
                    return true;
                }
            }
        }
        if path.segments.len() == 1 && path.segments[0].ident == "Stream" {
            return true;
        }
    }
    false
}
pub(crate) fn parse_context_from_signature(sig: &Signature) -> syn::Result<Ident> {
    for arg in sig.inputs.iter() {
        if let FnArg::Typed(pat_type) = arg
            && is_context_type(&pat_type.ty)
        {
            let ident: Ident = match &*pat_type.pat {
                Pat::Ident(pat_ident) => pat_ident.ident.clone(),
                Pat::Wild(_) => Ident::new("_", Span::call_site()),
                _ => {
                    return Err(syn::Error::new_spanned(
                        &pat_type.pat,
                        "expected identifier for context parameter",
                    ));
                }
            };
            return Ok(ident);
        }
    }
    Err(syn::Error::new_spanned(
        &sig.inputs,
        "expected at least one parameter of type &::hyperlane::Context",
    ))
}
pub(crate) fn parse_stream_from_signature(sig: &Signature) -> syn::Result<Ident> {
    for arg in sig.inputs.iter() {
        if let FnArg::Typed(pat_type) = arg
            && is_stream_type(&pat_type.ty)
        {
            let ident: Ident = match &*pat_type.pat {
                Pat::Ident(pat_ident) => pat_ident.ident.clone(),
                Pat::Wild(_) => Ident::new("_", Span::call_site()),
                _ => {
                    return Err(syn::Error::new_spanned(
                        &pat_type.pat,
                        "expected identifier for stream parameter",
                    ));
                }
            };
            return Ok(ident);
        }
    }
    Err(syn::Error::new_spanned(
        &sig.inputs,
        "expected at least one parameter of type &::hyperlane::Stream",
    ))
}
pub(crate) fn expr_to_isize(opt_expr: &Option<Expr>) -> proc_macro2::TokenStream {
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
pub(crate) fn leak_mut_context(is_unsafe_error: bool, context: &Ident) -> proc_macro2::TokenStream {
    if is_unsafe_error {
        quote! {
          #context.leak_mut()
        }
    } else {
        quote! {
            unsafe { #context.leak_mut() }
        }
    }
}
pub(crate) fn leak_context(is_unsafe_error: bool, context: &Ident) -> proc_macro2::TokenStream {
    if is_unsafe_error {
        quote! {
          #context.leak()
        }
    } else {
        quote! {
            unsafe { #context.leak() }
        }
    }
}
```
# Path: hyperlane-macros/src/closed/mod.rs
```rust
mod r#fn;
pub(crate) use r#fn::*;
use super::*;
```
# Path: hyperlane-macros/src/closed/fn.rs
```rust
use super::*;
pub(crate) fn closed_macro(item: TokenStream, position: Position) -> TokenStream {
    inject(position, item, |_: &Ident, stream: &Ident| {
        quote! {
            #stream.set_closed(true);
        }
    })
}
```
# Path: hyperlane-macros/src/route/struct.rs
```rust
use super::*;
pub(crate) struct RouteAttr {
    pub(crate) path: Expr,
}
```
# Path: hyperlane-macros/src/route/impl.rs
```rust
use super::*;
impl Parse for RouteAttr {
    fn parse(input: ParseStream) -> Result<Self> {
        let first_expr: Expr = input.parse()?;
        Ok(RouteAttr { path: first_expr })
    }
}
```
# Path: hyperlane-macros/src/route/mod.rs
```rust
mod r#fn;
mod r#impl;
mod r#struct;
pub(crate) use {r#fn::*, r#struct::*};
use super::*;
```
# Path: hyperlane-macros/src/route/fn.rs
```rust
use super::*;
pub(crate) fn route_macro(attr: TokenStream, item: TokenStream) -> TokenStream {
    let route_attr: RouteAttr = parse_macro_input!(attr as RouteAttr);
    let path: &Expr = &route_attr.path;
    let input_struct: ItemStruct = parse_macro_input!(item as ItemStruct);
    let struct_name: &Ident = &input_struct.ident;
    let gen_code: proc_macro2::TokenStream = quote! {
        #input_struct
        ::hyperlane::inventory::submit! {
            ::hyperlane::HookType::Route(#path, || ::hyperlane::Hook::factory::<#struct_name>())
        }
    };
    gen_code.into()
}
```
# Path: hyperlane-macros/src/reject/mod.rs
```rust
mod r#fn;
pub(crate) use r#fn::*;
use super::*;
```
# Path: hyperlane-macros/src/reject/fn.rs
```rust
use super::*;
pub(crate) fn reject_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let condition: Expr = parse_macro_input!(attr as Expr);
    inject(position, item, |_: &Ident, _: &Ident| {
        quote! {
            if #condition {
                return ::hyperlane::Status::Continue;
            }
        }
    })
}
```
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
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        try_get_task_panic_data(try_get_task_panic_data),
        task_panic_data(task_panic_data)
    )]
    #[epilogue_macros(
        response_version(HttpVersion::Http1_1),
        response_status_code(500),
        response_body(format!("{task_panic_data} {try_get_task_panic_data:?}")),
        send
    )]
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[request_error]
#[request_error(1)]
#[request_error("2")]
struct RequestErrorHook;
impl ServerHook for RequestErrorHook {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        try_get_request_error_data(try_get_request_error_data),
        request_error_data(request_error_data)
    )]
    #[epilogue_macros(
        response_version(HttpVersion::Http1_1),
        response_status_code(500),
        response_body(format!("{request_error_data} {try_get_request_error_data:?}")),
        send
    )]
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[request_middleware]
struct RequestMiddleware;
impl ServerHook for RequestMiddleware {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[epilogue_macros(
        response_version(HttpVersion::Http1_1),
        response_status_code(200),
        response_header(SERVER => HYPERLANE),
        response_header(CONNECTION => KEEP_ALIVE),
        response_header(CONTENT_TYPE => TEXT_PLAIN),
        response_header(ACCESS_CONTROL_ALLOW_ORIGIN => WILDCARD_ANY),
        response_header(STEP => "request_middleware")
    )]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[request_middleware(1)]
struct UpgradeHook;
impl ServerHook for UpgradeHook {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[epilogue_macros(
        is_ws_upgrade_type,
        response_body(Vec::new()),
        response_status_code(101),
        response_header(UPGRADE => WEBSOCKET),
        response_header(CONNECTION => UPGRADE),
        response_header(SEC_WEBSOCKET_ACCEPT => &WebSocketFrame::generate_accept_key(ctx.get_request().get_header_back(SEC_WEBSOCKET_KEY))),
        response_header(STEP => "upgrade_hook"),
        send
    )]
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[request_middleware(2)]
struct ConnectedHook;
impl ServerHook for ConnectedHook {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[response_status_code(200)]
    #[response_header(SERVER => HYPERLANE)]
    #[response_version(HttpVersion::Http1_1)]
    #[response_header(ACCESS_CONTROL_ALLOW_ORIGIN => WILDCARD_ANY)]
    #[response_header(STEP => "connected_hook")]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[response_middleware]
struct ResponseMiddleware1;
impl ServerHook for ResponseMiddleware1 {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[response_header(STEP => "response_middleware_1")]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[response_middleware(2)]
struct ResponseMiddleware2;
impl ServerHook for ResponseMiddleware2 {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        reject(ctx.get_request().get_upgrade_type().is_ws()),
        response_header(STEP => "response_middleware_2")
    )]
    #[epilogue_macros(try_send, flush)]
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[response_middleware("3")]
struct ResponseMiddleware3;
impl ServerHook for ResponseMiddleware3 {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        is_ws_upgrade_type,
        response_header(STEP => "response_middleware_3")
    )]
    #[epilogue_macros(try_send, flush)]
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
struct PrologueHooks;
impl ServerHook for PrologueHooks {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[is_get_method]
    #[is_http_version]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
struct EpilogueHooks;
impl ServerHook for EpilogueHooks {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[response_status_code(200)]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
async fn prologue_hooks_fn(stream: &mut Stream, ctx: &mut Context) -> Status {
    let hook: PrologueHooks = PrologueHooks::new(stream, ctx).await;
    hook.handle(stream, ctx).await
}
async fn epilogue_hooks_fn(stream: &mut Stream, ctx: &mut Context) -> Status {
    let hook: EpilogueHooks = EpilogueHooks::new(stream, ctx).await;
    hook.handle(stream, ctx).await
}
#[route("/response")]
struct Response;
impl ServerHook for Response {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[response_body(&RESPONSE_DATA)]
    #[response_reason_phrase(CUSTOM_REASON)]
    #[response_status_code(CUSTOM_STATUS_CODE)]
    #[response_header(CUSTOM_HEADER_NAME => CUSTOM_HEADER_VALUE)]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/connect")]
struct ConnectMethod;
impl ServerHook for ConnectMethod {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(is_connect_method, response_body("connect"))]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/delete")]
struct DeleteMethod;
impl ServerHook for DeleteMethod {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(is_delete_method, response_body("delete"))]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/head")]
struct HeadMethod;
impl ServerHook for HeadMethod {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(is_head_method, response_body("head"))]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/options")]
struct OptionsMethod;
impl ServerHook for OptionsMethod {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(is_options_method, response_body("options"))]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/patch")]
struct PatchMethod;
impl ServerHook for PatchMethod {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(is_patch_method, response_body("patch"))]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/put")]
struct PutMethod;
impl ServerHook for PutMethod {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(is_put_method, response_body("put"))]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/trace")]
struct TraceMethod;
impl ServerHook for TraceMethod {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(is_trace_method, response_body("trace"))]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/get_post_method")]
struct GetPostMethod;
impl ServerHook for GetPostMethod {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[closed]
    #[prologue_macros(
        is_http_version,
        methods(get, post),
        response_body("get_post_method"),
        response_status_code(200),
        response_reason_phrase("OK")
    )]
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/is_get_method")]
struct GetMethod;
impl ServerHook for GetMethod {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(is_ws_upgrade_type, is_get_method, response_body("is_get_method"))]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/is_post_method")]
struct PostMethod;
impl ServerHook for PostMethod {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(is_post_method, response_body("is_post_method"))]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/is_unknown_method")]
struct UnknownMethod;
impl ServerHook for UnknownMethod {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(is_unknown_method, response_body("is_unknown_method"))]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/is_http0_9_version")]
struct Http09Version;
impl ServerHook for Http09Version {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(is_http0_9_version, response_body("is_http0_9_version"))]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/is_http1_0_version")]
struct Http10Version;
impl ServerHook for Http10Version {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(is_http1_0_version, response_body("is_http1_0_version"))]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/is_http1_1_version")]
struct Http11Version;
impl ServerHook for Http11Version {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(is_http1_1_version, response_body("is_http1_1_version"))]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/is_http2_version")]
struct Http2Version;
impl ServerHook for Http2Version {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(is_http2_version, response_body("is_http2_version"))]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/is_http3_version")]
struct Http3Version;
impl ServerHook for Http3Version {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(is_http3_version, response_body("is_http3_version"))]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/is_http1_1_or_higher_version")]
struct Http11OrHigher;
impl ServerHook for Http11OrHigher {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        is_http1_1_or_higher_version,
        response_body("is_http1_1_or_higher_version")
    )]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/is_http_version")]
struct HttpAllVersion;
impl ServerHook for HttpAllVersion {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(is_http_version, response_body("is_http_version"))]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/is_unknown_version")]
struct UnknownVersion;
impl ServerHook for UnknownVersion {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(is_unknown_version, response_body("is_unknown_version"))]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/is_ws_upgrade_type")]
struct WsUpgradeType;
impl ServerHook for WsUpgradeType {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[is_ws_upgrade_type]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/is_h2c_upgrade_type")]
struct H2cUpgradeType;
impl ServerHook for H2cUpgradeType {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(is_h2c_upgrade_type, response_body("is_h2c_upgrade_type"))]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/is_tls_upgrade_type")]
struct Tls;
impl ServerHook for Tls {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(is_tls_upgrade_type, response_body("is_tls_upgrade_type"))]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/is_unknown_upgrade_type")]
struct UnknownUpgradeType;
impl ServerHook for UnknownUpgradeType {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(is_unknown_upgrade_type, response_body("is_unknown_upgrade_type"))]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/ws1")]
struct Websocket1;
impl ServerHook for Websocket1 {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[is_ws_upgrade_type]
    #[try_get_websocket_request(body)]
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        let body_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(&body);
        stream.send_list(body_list).await;
    }
}
#[route("/ws2")]
struct Websocket2;
impl ServerHook for Websocket2 {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[is_ws_upgrade_type]
    #[try_get_websocket_request(request)]
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        let body_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(&request);
        stream.send_list(body_list).await;
    }
}
#[route("/ws3")]
struct Websocket3;
impl ServerHook for Websocket3 {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[is_ws_upgrade_type]
    #[try_get_websocket_request(request)]
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        let body_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(&request);
        stream.send_list(body_list).await;
    }
}
#[route("/ws4")]
struct Websocket4;
impl ServerHook for Websocket4 {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[is_ws_upgrade_type]
    #[try_get_websocket_request(request)]
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        let body_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(&request);
        stream.send_list(body_list).await;
    }
}
#[route("/ws5")]
struct Websocket5;
impl ServerHook for Websocket5 {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[is_ws_upgrade_type]
    #[try_get_websocket_request(body)]
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        let body_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(&body);
        stream.send_list(body_list).await;
    }
}
#[route("/hook")]
struct Hook;
impl ServerHook for Hook {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_hooks(prologue_hooks_fn)]
    #[epilogue_hooks(epilogue_hooks_fn)]
    #[response_body("Testing hook macro")]
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/attributes")]
struct Attributes;
impl ServerHook for Attributes {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[response_body(&format!("request attributes: {request_attributes:?}"))]
    #[attributes(request_attributes)]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/route_params/:test")]
struct RouteParams;
impl ServerHook for RouteParams {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[response_body(&format!("request route params: {request_route_params:?}"))]
    #[route_params(request_route_params)]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/try_get_route_param/:test")]
struct RouteParamOption;
impl ServerHook for RouteParamOption {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[response_body(&format!("route param: {request_try_get_route_param1:?} {request_try_get_route_param2:?} {request_try_get_route_param3:?}"))]
    #[try_get_route_param("test1" => request_try_get_route_param1)]
    #[try_get_route_param("test2" => request_try_get_route_param2, "test3" => request_try_get_route_param3)]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/route_param/:test")]
struct RouteParam;
impl ServerHook for RouteParam {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[response_body(&format!("route param: {request_route_param1} {request_route_param2} {request_route_param3}"))]
    #[route_param("test1" => request_route_param1)]
    #[route_param("test2" => request_route_param2, "test3" => request_route_param3)]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/host")]
struct Host;
impl ServerHook for Host {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[host("localhost")]
    #[epilogue_macros(response_body("host string literal: localhost"))]
    #[prologue_macros(response_body("host string literal: localhost"))]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/try_get_request_query")]
struct RequestQueryOption;
impl ServerHook for RequestQueryOption {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[epilogue_macros(
        try_get_request_query("test" => try_get_request_query),
        response_body(&format!("request query: {try_get_request_query:?}"))
    )]
    #[prologue_macros(
        try_get_request_query("test" => try_get_request_query),
        response_body(&format!("request query: {try_get_request_query:?}"))
    )]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/request_query")]
struct RequestQuery;
impl ServerHook for RequestQuery {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[epilogue_macros(
        request_query("test" => request_query),
        response_body(&format!("request query: {request_query}"))
    )]
    #[prologue_macros(
        request_query("test" => request_query),
        response_body(&format!("request query: {request_query}"))
    )]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/try_get_request_header")]
struct RequestHeaderOption;
impl ServerHook for RequestHeaderOption {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[epilogue_macros(
        try_get_request_header(HOST => try_get_request_header),
        response_body(&format!("request header: {try_get_request_header:?}"))
    )]
    #[prologue_macros(
        try_get_request_header(HOST => try_get_request_header),
        response_body(&format!("request header: {try_get_request_header:?}"))
    )]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/request_header")]
struct RequestHeader;
impl ServerHook for RequestHeader {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[epilogue_macros(
        request_header(HOST => request_header),
        response_body(&format!("request header: {request_header}"))
    )]
    #[prologue_macros(
        request_header(HOST => request_header),
        response_body(&format!("request header: {request_header}"))
    )]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/request_querys")]
struct RequestQuerys;
impl ServerHook for RequestQuerys {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[epilogue_macros(
        request_querys(request_querys),
        response_body(&format!("request querys: {request_querys:?}"))
    )]
    #[prologue_macros(
        request_querys(request_querys),
        response_body(&format!("request querys: {request_querys:?}"))
    )]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/request_headers")]
struct RequestHeaders;
impl ServerHook for RequestHeaders {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[epilogue_macros(
        request_headers(request_headers),
        response_body(&format!("request headers: {request_headers:?}"))
    )]
    #[prologue_macros(
        request_headers(request_headers),
        response_body(&format!("request headers: {request_headers:?}"))
    )]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/request_body")]
struct RequestBodyRoute;
impl ServerHook for RequestBodyRoute {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[response_body(&format!("raw body: {raw_body:?}"))]
    #[request_body(raw_body)]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/reject_host")]
struct RejectHost;
impl ServerHook for RejectHost {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        reject_host("filter.localhost"),
        response_body("host filter string literal")
    )]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/try_get_attribute")]
struct AttributeOption;
impl ServerHook for AttributeOption {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[response_body(&format!("request attribute: {request_try_get_attribute:?}"))]
    #[try_get_attribute(TEST_ATTRIBUTE_KEY => request_try_get_attribute: TestData)]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/attribute")]
struct Attribute;
impl ServerHook for Attribute {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[response_body(&format!("request attribute: {request_attribute:?}"))]
    #[attribute(TEST_ATTRIBUTE_KEY => request_attribute: TestData)]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/request_body_json_result")]
struct RequestBodyJsonResult;
impl ServerHook for RequestBodyJsonResult {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[response_body(&format!("request data: {request_data_result:?}"))]
    #[request_body_json_result(request_data_result: TestData)]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/request_body_json")]
struct RequestBodyJson;
impl ServerHook for RequestBodyJson {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[response_body(&format!("request data: {request_data_result:?}"))]
    #[request_body_json(request_data_result: TestData)]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/referer")]
struct Referer;
impl ServerHook for Referer {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        referer("http://localhost"),
        response_body("referer string literal: http://localhost")
    )]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/reject_referer")]
struct RejectReferer;
impl ServerHook for RejectReferer {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        reject_referer("http://localhost"),
        response_body("referer filter string literal")
    )]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/cookies")]
struct Cookies;
impl ServerHook for Cookies {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[response_body(&format!("All cookies: {cookie_value:?}"))]
    #[request_cookies(cookie_value)]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/try_get_request_cookie")]
struct CookieOption;
impl ServerHook for CookieOption {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[response_body(&format!("Session cookie: {session_cookie1_option:?}, {session_cookie2_option:?}"))]
    #[try_get_request_cookie("test1" => session_cookie1_option, "test2" => session_cookie2_option)]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/request_cookie")]
struct Cookie;
impl ServerHook for Cookie {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[response_body(&format!("Session cookie: {session_cookie1}, {session_cookie2}"))]
    #[request_cookie("test1" => session_cookie1, "test2" => session_cookie2)]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/request_version")]
struct RequestVersionTest;
impl ServerHook for RequestVersionTest {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[response_body(&format!("HTTP Version: {is_http_version}"))]
    #[request_version(is_http_version)]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/request_path")]
struct RequestPathTest;
impl ServerHook for RequestPathTest {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[response_body(&format!("Request Path: {request_path}"))]
    #[request_path(request_path)]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/response_header")]
struct ResponseHeaderTest;
impl ServerHook for ResponseHeaderTest {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[response_body("Testing header set and replace operations")]
    #[response_header("X-Add-Header", "add-value")]
    #[response_header("X-Set-Header" => "set-value")]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/literals")]
struct Literals;
impl ServerHook for Literals {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[response_status_code(201)]
    #[response_header(CONTENT_TYPE => APPLICATION_JSON)]
    #[response_body("{\"message\": \"Resource created\"}")]
    #[response_reason_phrase(HttpStatus::Created.to_string())]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/inject/response_body")]
struct InjectResponseBody;
impl ServerHook for InjectResponseBody {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        self.response_body_with_ref_self(stream, ctx).await
    }
}
impl InjectResponseBody {
    #[response_body("response body with ref self")]
    async fn response_body_with_ref_self(&self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/inject/is_post_method")]
struct InjectPostMethod;
impl ServerHook for InjectPostMethod {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        self.post_method_with_ref_self(stream, ctx).await
    }
}
impl InjectPostMethod {
    #[prologue_macros(is_post_method, response_body("post method with ref self"))]
    async fn post_method_with_ref_self(&self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/inject/send_flush")]
struct InjectSendFlush;
impl ServerHook for InjectSendFlush {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        self.send_and_flush_with_ref_self(stream, ctx).await
    }
}
impl InjectSendFlush {
    #[epilogue_macros(try_send, flush)]
    async fn send_and_flush_with_ref_self(&self, stream: &mut Stream, ctx: &mut Context) -> Status {
        Status::Reject
    }
}
#[route("/inject/request_body")]
struct InjectRequestBody;
impl ServerHook for InjectRequestBody {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        self.extract_request_body_with_ref_self(stream, ctx).await
    }
}
impl InjectRequestBody {
    #[request_body(_raw_body)]
    async fn extract_request_body_with_ref_self(
        &self,
        _: &mut Stream,
        ctx: &mut Context,
    ) -> Status {
        Status::Continue
    }
}
#[route("/inject/multiple_methods")]
struct InjectMultipleMethods;
impl ServerHook for InjectMultipleMethods {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        self.multiple_methods_with_ref_self(stream, ctx).await
    }
}
impl InjectMultipleMethods {
    #[methods(get, post)]
    async fn multiple_methods_with_ref_self(&self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
    #[is_unknown_method]
    async fn unknown_method_with_ref_self(&self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/inject/http_")]
struct InjectHttpStream;
impl ServerHook for InjectHttpStream {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        self.http_handler_with_ref_self(stream, ctx).await
    }
}
impl InjectHttpStream {
    #[try_get_http_request(_request)]
    async fn http_handler_with_ref_self(&self, stream: &mut Stream, ctx: &mut Context) -> Status {}
}
#[route("/inject/ws_")]
struct InjectWsStream;
impl ServerHook for InjectWsStream {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        self.websocket_handler_with_ref_self(stream, ctx).await
    }
}
impl InjectWsStream {
    #[try_get_websocket_request(_request)]
    async fn websocket_handler_with_ref_self(
        &self,
        stream: &mut Stream,
        ctx: &mut Context,
    ) -> Status {
    }
}
#[route("/inject/complex_post")]
struct InjectComplexPost;
impl ServerHook for InjectComplexPost {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        self.complex_post_handler_with_ref_self(stream, ctx).await
    }
}
impl InjectComplexPost {
    #[prologue_macros(
        is_post_method,
        is_http_version,
        request_body(raw_body),
        response_status_code(201),
        response_header(CONTENT_TYPE => APPLICATION_JSON),
        response_body(&format!("Received: {raw_body:?}"))
    )]
    #[epilogue_macros(try_send, flush)]
    async fn complex_post_handler_with_ref_self(
        &self,
        stream: &mut Stream,
        ctx: &mut Context,
    ) -> Status {
        Status::Reject
    }
}
impl InjectComplexPost {
    #[is_post_method]
    async fn test_with_bool_param(_: bool, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
    #[is_get_method]
    async fn test_with_multiple_params(
        _: bool,
        _: &mut Stream,
        ctx: &mut Context,
        _: i32,
    ) -> Status {
        Status::Continue
    }
}
#[route("/test/send")]
struct TestSend;
impl ServerHook for TestSend {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        is_get_method,
        response_status_code(200),
        response_header(CONTENT_TYPE => TEXT_PLAIN),
        response_body("Test send operation")
    )]
    #[epilogue_macros(send)]
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        Status::Reject
    }
}
#[route("/test/try_send")]
struct TestTrySend;
impl ServerHook for TestTrySend {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        is_get_method,
        response_status_code(200),
        response_header(CONTENT_TYPE => TEXT_PLAIN),
        response_body("Test try send operation")
    )]
    #[epilogue_macros(try_send)]
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        Status::Reject
    }
}
#[route("/test/try_flush")]
struct TestTryFlush;
impl ServerHook for TestTryFlush {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        is_get_method,
        response_status_code(200),
        response_header(CONTENT_TYPE => TEXT_PLAIN),
        response_body("Test try flush operation")
    )]
    #[epilogue_macros(try_flush)]
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/test/closed")]
struct TestClosed;
impl ServerHook for TestClosed {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        is_get_method,
        response_status_code(200),
        response_header(CONTENT_TYPE => TEXT_PLAIN),
        response_body("Test closed operation")
    )]
    #[epilogue_macros(closed)]
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/test/flush")]
struct TestFlush;
impl ServerHook for TestFlush {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        is_get_method,
        response_status_code(200),
        response_header(CONTENT_TYPE => TEXT_PLAIN),
        response_body("Test flush operation")
    )]
    #[epilogue_macros(flush)]
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[response_body("standalone response body")]
async fn standalone_response_body_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[prologue_macros(is_get_method, response_body("standalone get handler"))]
async fn standalone_get_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[epilogue_macros(try_send, flush)]
async fn standalone_send_and_flush_handler(stream: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[request_body(_raw_body)]
async fn standalone_request_body_extractor(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[methods(get, post)]
async fn standalone_multiple_methods_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[try_get_http_request]
async fn standalone_http_handler(stream: &mut Stream, ctx: &mut Context) -> Status {}
#[try_get_websocket_request]
async fn standalone_websocket_handler(stream: &mut Stream, ctx: &mut Context) -> Status {}
#[closed]
async fn standalone_closed_handler(stream: &mut Stream, _: &mut Context) -> Status {
    Status::Continue
}
#[flush]
async fn standalone_flush_handler(stream: &mut Stream, _: &mut Context) -> Status {
    Status::Continue
}
#[try_flush]
async fn standalone_try_flush_handler(stream: &mut Stream, _: &mut Context) -> Status {
    Status::Continue
}
#[prologue_macros(
    is_get_method,
    is_http_version,
    response_status_code(200),
    response_header(CONTENT_TYPE => TEXT_PLAIN),
    response_body("standalone complex handler")
)]
#[epilogue_macros(try_send, flush)]
async fn standalone_complex_get_handler(stream: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[request_body(body1, body2, body3)]
async fn test_multi_request_body(_: &mut Stream, ctx: &mut Context) -> Status {
    println!("body1: {:?}, body2: {:?}, body3: {:?}", body1, body2, body3);
    Status::Continue
}
#[route("/test_multi_request_body_json")]
#[derive(Debug, serde::Deserialize)]
struct User {
    name: String,
}
impl ServerHook for User {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
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
        ))
    )]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
#[attribute("key1" => attr1: String, "key2" => attr2: i32)]
async fn test_multi_attribute(_: &mut Stream, ctx: &mut Context) -> Status {
    println!("attr1: {:?}, attr2: {:?}", attr1, attr2);
    Status::Continue
}
#[attributes(attrs1, attrs2)]
async fn test_multi_attributes(_: &mut Stream, ctx: &mut Context) -> Status {
    println!("attrs1: {:?}, attrs2: {:?}", attrs1, attrs2);
    Status::Continue
}
#[route_params(params1, params2)]
async fn test_multi_route_params(_: &mut Stream, ctx: &mut Context) -> Status {
    println!("params1: {:?}, params2: {:?}", params1, params2);
    Status::Continue
}
#[request_querys(querys1, querys2)]
async fn test_multi_request_querys(_: &mut Stream, ctx: &mut Context) -> Status {
    println!("querys1: {:?}, querys2: {:?}", querys1, querys2);
    Status::Continue
}
#[request_headers(headers1, headers2)]
async fn test_multi_request_headers(_: &mut Stream, ctx: &mut Context) -> Status {
    println!("headers1: {:?}, headers2: {:?}", headers1, headers2);
    Status::Continue
}
#[request_cookies(cookies1, cookies2)]
async fn test_multi_request_cookies(_: &mut Stream, ctx: &mut Context) -> Status {
    println!("cookies1: {:?}, cookies2: {:?}", cookies1, cookies2);
    Status::Continue
}
#[request_version(version1, version2)]
async fn test_multi_request_version(_: &mut Stream, ctx: &mut Context) -> Status {
    println!("version1: {:?}, version2: {:?}", version1, version2);
    Status::Continue
}
#[request_path(path1, path2)]
async fn test_multi_request_path(_: &mut Stream, ctx: &mut Context) -> Status {
    println!("path1: {:?}, path2: {:?}", path1, path2);
    Status::Continue
}
#[host("localhost", "127.0.0.1")]
async fn test_multi_host(_: &mut Stream, ctx: &mut Context) -> Status {
    println!("Host check passed");
    Status::Continue
}
#[reject_host("localhost", "127.0.0.1")]
async fn test_multi_reject_host(_: &mut Stream, ctx: &mut Context) -> Status {
    println!("Reject host check passed");
    Status::Continue
}
#[referer("http://localhost", "http://127.0.0.1")]
async fn test_multi_referer(_: &mut Stream, ctx: &mut Context) -> Status {
    println!("Referer check passed");
    Status::Continue
}
#[reject_referer("http://localhost", "http://127.0.0.1")]
async fn test_multi_reject_referer(_: &mut Stream, ctx: &mut Context) -> Status {
    println!("Reject referer check passed");
    Status::Continue
}
#[hyperlane(server1: Server, server2: Server)]
async fn test_multi_hyperlane() {
    println!("server1 and server2 initialized");
}
#[response_status_code(200)]
async fn standalone_response_status_code_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[response_reason_phrase("Custom Reason")]
async fn standalone_response_reason_phrase_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[response_header(CONTENT_TYPE => APPLICATION_JSON)]
async fn standalone_response_header_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[response_header("X-Custom-Header", "custom-value")]
async fn standalone_response_header_with_comma_handler(
    _: &mut Stream,
    ctx: &mut Context,
) -> Status {
    Status::Continue
}
#[response_version(HttpVersion::Http1_1)]
async fn standalone_response_version_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[is_connect_method]
async fn standalone_connect_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[is_delete_method]
async fn standalone_delete_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[is_head_method]
async fn standalone_head_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[is_options_method]
async fn standalone_options_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[is_patch_method]
async fn standalone_patch_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[is_put_method]
async fn standalone_put_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[is_trace_method]
async fn standalone_trace_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[is_get_method]
async fn standalone_get_handler_with_param(_: bool, _: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[is_unknown_method]
async fn standalone_unknown_method_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[methods(get, post, put)]
async fn standalone_methods_multiple_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[is_http0_9_version]
async fn standalone_http0_9_version_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[is_http1_0_version]
async fn standalone_http1_0_version_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[is_http1_1_version]
async fn standalone_http1_1_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[is_http2_version]
async fn standalone_http2_version_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[is_http3_version]
async fn standalone_http3_version_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[is_http1_1_or_higher_version]
async fn standalone_http1_1_or_higher_version_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[is_unknown_version]
async fn standalone_unknown_version_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[is_h2c_upgrade_type]
async fn standalone_h2c_upgrade_type_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[is_tls_upgrade_type]
async fn standalone_tls_upgrade_type_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[is_ws_upgrade_type]
async fn standalone_ws_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[is_unknown_upgrade_type]
async fn standalone_unknown_upgrade_type_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[filter(ctx.get_request().get_method().is_get())]
async fn standalone_filter_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[reject(ctx.get_request().get_method().is_post())]
async fn standalone_reject_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[reject_host("example.com")]
async fn standalone_reject_host_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[referer("https://example.com")]
async fn standalone_referer_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[reject_referer("https://malicious.com")]
async fn standalone_reject_referer_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[request_query("param" => _value)]
async fn standalone_request_query_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[try_get_request_query("optional_param" => _optional_value)]
async fn standalone_try_get_request_query_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[request_header(HOST => _host_value)]
async fn standalone_request_header_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[try_get_request_header(USER_AGENT => _user_agent)]
async fn standalone_try_get_request_header_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[request_querys(_querys)]
async fn standalone_request_querys_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[request_headers(_headers)]
async fn standalone_request_headers_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[request_cookies(_cookies)]
async fn standalone_request_cookies_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[request_cookie("session" => _session_cookie)]
async fn standalone_request_cookie_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[try_get_request_cookie("optional_cookie" => _optional_cookie)]
async fn standalone_try_get_request_cookie_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[request_version(_version)]
async fn standalone_request_version_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[request_path(_path)]
async fn standalone_request_path_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[attribute("key" => _attr_value: String)]
async fn standalone_attribute_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[try_get_attribute("optional_key" => _optional_attr: String)]
async fn standalone_try_get_attribute_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[attributes(_attrs)]
async fn standalone_attributes_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[route_params(_params)]
async fn standalone_route_params_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[route_param("param" => _param_value)]
async fn standalone_route_param_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[try_get_route_param("optional_param" => _optional_param_value)]
async fn standalone_try_get_route_param_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[request_body_json(_user: TestData)]
async fn standalone_request_body_json_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[request_body_json_result(_user_result: TestData)]
async fn standalone_request_body_json_result_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[try_get_http_request]
async fn standalone_try_get_http_request_with_config_handler(
    stream: &mut Stream,
    ctx: &mut Context,
) -> Status {
}
#[try_get_websocket_request]
async fn standalone_try_get_websocket_request_with_config_handler(
    stream: &mut Stream,
    ctx: &mut Context,
) -> Status {
}
#[try_get_http_request(_request)]
async fn standalone_try_get_http_request_with_request_handler(
    stream: &mut Stream,
    ctx: &mut Context,
) -> Status {
}
#[try_get_websocket_request(_request)]
async fn standalone_try_get_websocket_request_with_request_handler(
    stream: &mut Stream,
    ctx: &mut Context,
) -> Status {
}
#[try_get_http_request(_request)]
async fn standalone_try_get_http_request_full_handler(
    stream: &mut Stream,
    ctx: &mut Context,
) -> Status {
}
#[try_get_websocket_request(_request)]
async fn standalone_try_get_websocket_request_full_handler(
    stream: &mut Stream,
    ctx: &mut Context,
) -> Status {
}
#[send]
async fn standalone_send_handler_2(stream: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[send(ctx.get_mut_response().build())]
async fn standalone_send_with_data_handler(stream: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[try_send]
async fn standalone_try_send_handler_2(stream: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[try_send(ctx.get_mut_response().build())]
async fn standalone_try_send_with_data_handler(stream: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[flush]
async fn standalone_flush_handler_2(stream: &mut Stream, _: &mut Context) -> Status {
    Status::Continue
}
#[try_flush]
async fn standalone_try_flush_handler_2(stream: &mut Stream, _: &mut Context) -> Status {
    Status::Continue
}
#[closed]
async fn standalone_closed_handler_2(stream: &mut Stream, _: &mut Context) -> Status {
    Status::Continue
}
#[clear_response_headers]
async fn standalone_clear_response_headers_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[prologue_macros(
    is_get_method,
    response_status_code(200),
    response_header(CONTENT_TYPE => TEXT_PLAIN),
    response_body("prologue macros test")
)]
async fn standalone_prologue_macros_complex_handler(_: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[epilogue_macros(
    response_status_code(201),
    response_header(CONTENT_TYPE => APPLICATION_JSON),
    response_body("epilogue macros test"),
    try_send,
    flush
)]
async fn standalone_epilogue_macros_complex_handler(
    stream: &mut Stream,
    ctx: &mut Context,
) -> Status {
    Status::Continue
}
#[prologue_hooks(prologue_hooks_fn)]
async fn standalone_prologue_hooks_handler(stream: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[epilogue_hooks(epilogue_hooks_fn)]
async fn standalone_epilogue_hooks_handler(stream: &mut Stream, ctx: &mut Context) -> Status {
    Status::Continue
}
#[closed]
async fn context_macro(stream: &mut Stream, ctx: &mut Context) -> Status {
    let new_ctx: &Context = unsafe { context!(ctx) };
    let _: &Response = new_ctx.get_response();
    let new_ctx: &Context = unsafe { context!(ctx: &Context) };
    let _: &Response = new_ctx.get_response();
    let new_ctx: &mut Context = unsafe { context!(ctx: &mut Context) };
    let _: &mut Response = new_ctx.get_mut_response();
    Status::Continue
}
#[route("/hooks_expression")]
struct HooksExpression;
impl ServerHook for HooksExpression {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[is_get_method]
    #[prologue_hooks(HooksExpression::new_hook, HooksExpression::method_hook)]
    #[epilogue_hooks(HooksExpression::new_hook, HooksExpression::method_hook)]
    #[response_body("hooks expression test")]
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
impl HooksExpression {
    async fn new_hook(_: &mut Stream, _: &mut Context) -> Status {
        Status::Continue
    }
    async fn method_hook(_: &mut Stream, _: &mut Context) -> Status {
        Status::Continue
    }
}
#[route("/server_config")]
struct MultiServerConfig;
impl ServerHook for MultiServerConfig {
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[is_get_method]
    #[response_body("multi server config test")]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
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
# Path: hyperlane-cli/README.md
# hyperlane-cli
[Api Docs](https://docs.rs/hyperlane-cli/latest/)
## Description
> A command-line tool for Hyperlane framework.
## Installation
To install `hyperlane-cli` run cmd:
```shell
cargo add hyperlane-cli
```
## Contact
# Path: hyperlane-cli/src/lib.rs
```rust
mod bump;
mod command;
mod config;
mod fmt;
mod help;
mod logger;
mod new;
mod publish;
mod template;
mod version;
mod watch;
pub use {
    bump::*, command::*, config::*, fmt::*, help::*, logger::*, new::*, publish::*, template::*,
    version::*, watch::*,
};
pub(crate) use std::{
    collections::{HashMap, VecDeque},
    env::args,
    io,
    path::{Path, PathBuf},
    process::Stdio,
    str::FromStr,
    sync::{Arc, LazyLock},
};
pub(crate) use {
    notify::{Event, EventKind, RecommendedWatcher, RecursiveMode, Watcher, recommended_watcher},
    regex::{Captures, Regex},
    std::ffi::OsStr,
    tokio::{
        fs::{ReadDir, create_dir_all, read_dir, read_to_string, write},
        process::Command,
        spawn,
        sync::{
            Mutex, MutexGuard,
            watch::{Receiver, Sender, channel},
        },
        task::JoinHandle,
        time::{Duration, Interval, interval, sleep},
    },
    toml::Value,
    which::which,
};
```
# Path: hyperlane-cli/src/main.rs
```rust
use hyperlane_cli::*;
use std::process::exit;
#[tokio::main]
async fn main() {
    Logger::init(log::LevelFilter::Info);
    let args: Args = parse_args();
    match args.command {
        CommandType::Fmt => {
            if let Err(error) = execute_fmt(&args).await {
                log::error!("fmt failed: {error}");
                exit(1);
            }
        }
        CommandType::Watch => {
            if let Err(error) = execute_watch().await {
                log::error!("watch failed: {error}");
                exit(1);
            }
        }
        CommandType::Bump => {
            let manifest_path: String = args
                .manifest_path
                .unwrap_or_else(|| "Cargo.toml".to_string());
            let bump_type: BumpVersionType = args.bump_type.unwrap_or(BumpVersionType::Patch);
            match execute_bump(&manifest_path, &bump_type).await {
                Ok(new_version) => {
                    log::info!("Version bumped to {new_version}");
                }
                Err(error) => {
                    log::error!("bump failed: {error}");
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
                        log::error!("Publish completed with {failed_count} failures");
                        exit(1);
                    } else {
                        log::info!("All packages published successfully");
                    }
                }
                Err(error) => {
                    log::error!("publish failed: {error}");
                    exit(1);
                }
            }
        }
        CommandType::New => {
            if let Some(project_name) = args.project_name {
                if let Err(error) = execute_new(&project_name).await {
                    log::error!("new failed: {error}");
                    exit(1);
                }
            } else {
                log::error!(
                    "Error: Project name is required. Usage: hyperlane-cli new <PROJECT_NAME>"
                );
                exit(1);
            }
        }
        CommandType::Template => {
            let template_type: TemplateType = match args.template_type {
                Some(tt) => tt,
                None => {
                    log::error!(
                        "Error: Template type is required. Usage: hyperlane-cli template <TYPE> [SUBTYPE] <NAME>"
                    );
                    exit(1);
                }
            };
            let component_name: String = match args.component_name {
                Some(cn) => cn,
                None => {
                    log::error!(
                        "Error: Component name is required. Usage: hyperlane-cli template <TYPE> [SUBTYPE] <NAME>"
                    );
                    exit(1);
                }
            };
            if template_type == TemplateType::Model && args.model_sub_type.is_none() {
                log::error!("Error: Model type requires subtype (application|request|response)");
                exit(1);
            }
            if let Err(error) =
                execute_template(template_type, &component_name, args.model_sub_type).await
            {
                log::error!("template failed: {error}");
                exit(1);
            }
        }
        CommandType::Help => print_help(),
        CommandType::Version => print_version(),
    }
}
```
# Path: hyperlane-cli/src/fmt/static.rs
```rust
use super::*;
pub static DERIVE_REGEX: LazyLock<Regex> = LazyLock::new(|| {
    regex::Regex::new(r"#\[derive\s*\(([^)]+)\)\]").expect("Invalid regex pattern")
});
```
# Path: hyperlane-cli/src/fmt/mod.rs
```rust
mod r#fn;
mod r#static;
pub use {r#fn::*, r#static::*};
use super::*;
```
# Path: hyperlane-cli/src/fmt/fn.rs
```rust
use super::*;
fn sort_derive_in_line(line: &str) -> Option<String> {
    let captures: Captures<'_> = DERIVE_REGEX.captures(line)?;
    let derive_content: &str = captures.get(1)?.as_str();
    let mut traits: Vec<String> = derive_content
        .split(',')
        .map(|s: &str| s.trim().to_string())
        .filter(|s: &String| !s.is_empty())
        .collect();
    traits.sort_by_key(|a: &String| a.to_lowercase());
    let sorted_traits: String = traits.join(", ");
    let result: String = line.replace(derive_content, &sorted_traits);
    Some(result)
}
async fn format_derive_in_file(file_path: &Path) -> Result<bool, io::Error> {
    let content: String = read_to_string(file_path).await?;
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
        write(file_path, new_content).await?;
    }
    Ok(modified)
}
async fn find_rust_files(manifest_path: &Path) -> Result<Vec<PathBuf>, io::Error> {
    let mut files: Vec<PathBuf> = Vec::new();
    let workspace_root: &Path = manifest_path.parent().unwrap_or(Path::new("."));
    let src_dir: PathBuf = workspace_root.join("src");
    if src_dir.exists() {
        find_rust_files_in_dir(&src_dir, &mut files).await?;
    }
    let content: String = read_to_string(manifest_path).await?;
    if let Ok(doc) = toml::from_str::<Value>(&content)
        && let Some(workspace) = doc.get("workspace")
        && let Some(members) = workspace.get("members").and_then(|m: &Value| m.as_array())
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
async fn find_rust_files_in_dir(dir: &Path, files: &mut Vec<PathBuf>) -> Result<(), io::Error> {
    let mut entries: ReadDir = read_dir(dir).await?;
    while let Some(entry) = entries.next_entry().await? {
        let path: PathBuf = entry.path();
        if path.is_file() && path.extension().is_some_and(|ext: &OsStr| ext == "rs") {
            files.push(path);
        } else if path.is_dir() {
            Box::pin(find_rust_files_in_dir(&path, files)).await?;
        }
    }
    Ok(())
}
async fn format_derive_attributes(manifest_path: &str) -> Result<(), io::Error> {
    let path: &Path = Path::new(manifest_path);
    let files: Vec<PathBuf> = find_rust_files(path).await?;
    let modified_count: Arc<Mutex<usize>> = Arc::new(Mutex::new(0));
    let mut handles: Vec<JoinHandle<Result<(), io::Error>>> = Vec::new();
    for file in files {
        let counter: Arc<Mutex<usize>> = Arc::clone(&modified_count);
        let handle: JoinHandle<Result<(), io::Error>> = spawn(async move {
            if format_derive_in_file(&file).await? {
                let mut count: MutexGuard<'_, usize> = counter.lock().await;
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
        log::info!("Sorted derive attributes in {count} files");
    }
    Ok(())
}
fn is_cargo_clippy_installed() -> bool {
    which("cargo-clippy").is_ok()
}
async fn install_cargo_clippy() -> Result<(), io::Error> {
    log::warn!("cargo-clippy not found, installing...");
    let output: std::process::Output = Command::new("rustup")
        .arg("component")
        .arg("add")
        .arg("clippy")
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .output()
        .await?;
    let stdout: String = String::from_utf8_lossy(&output.stdout).trim().to_string();
    let stderr: String = String::from_utf8_lossy(&output.stderr).trim().to_string();
    if !stdout.is_empty() {
        for line in stdout.lines() {
            log::info!("{line}");
        }
    }
    if !stderr.is_empty() {
        if output.status.success() {
            for line in stderr.lines() {
                if line.is_empty() {
                    continue;
                }
                log::info!("{line}");
            }
        } else {
            for line in stderr.lines() {
                if line.is_empty() {
                    continue;
                }
                log::error!("{line}");
            }
        }
    }
    if !output.status.success() {
        return Err(io::Error::other("failed to install cargo-clippy"));
    }
    Ok(())
}
async fn execute_clippy_fix(args: &Args) -> Result<(), io::Error> {
    if !is_cargo_clippy_installed() {
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
    cmd.stdout(Stdio::piped()).stderr(Stdio::piped());
    let output: std::process::Output = cmd.output().await?;
    let stdout: String = String::from_utf8_lossy(&output.stdout).trim().to_string();
    let stderr: String = String::from_utf8_lossy(&output.stderr).trim().to_string();
    if !stdout.is_empty() {
        for line in stdout.lines() {
            log::info!("{line}");
        }
    }
    if !stderr.is_empty() {
        if output.status.success() {
            for line in stderr.lines() {
                if line.is_empty() {
                    continue;
                }
                log::info!("{line}");
            }
        } else {
            for line in stderr.lines() {
                if line.is_empty() {
                    continue;
                }
                log::error!("{line}");
            }
        }
    }
    if !output.status.success() {
        return Err(io::Error::other("cargo clippy --fix failed"));
    }
    Ok(())
}
pub async fn execute_fmt(args: &Args) -> Result<(), io::Error> {
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
    cmd.stdout(Stdio::piped()).stderr(Stdio::piped());
    let output: std::process::Output = cmd.output().await?;
    let stdout: String = String::from_utf8_lossy(&output.stdout).trim().to_string();
    let stderr: String = String::from_utf8_lossy(&output.stderr).trim().to_string();
    if !stdout.is_empty() {
        for line in stdout.lines() {
            log::info!("{line}");
        }
    }
    if !stderr.is_empty() {
        if output.status.success() {
            for line in stderr.lines() {
                if line.is_empty() {
                    continue;
                }
                log::info!("{line}");
            }
        } else {
            for line in stderr.lines() {
                if line.is_empty() {
                    continue;
                }
                log::error!("{line}");
            }
        }
    }
    if !output.status.success() {
        return Err(io::Error::other("cargo fmt failed"));
    }
    if !args.check {
        execute_clippy_fix(args).await?;
    }
    Ok(())
}
pub async fn format_path(path: &Path) -> Result<(), io::Error> {
    let mut cmd: Command = Command::new("cargo");
    cmd.arg("fmt").arg("--").arg(path);
    cmd.stdout(Stdio::null()).stderr(Stdio::null());
    cmd.status().await?;
    Ok(())
}
```
# Path: hyperlane-cli/src/help/mod.rs
```rust
mod r#fn;
pub use r#fn::*;
```
# Path: hyperlane-cli/src/help/fn.rs
```rust
pub fn print_help() {
    log::info!("hyperlane-cli [COMMAND] [OPTIONS]");
    log::info!("");
    log::info!("Commands:");
    log::info!("  bump      Bump version in Cargo.toml");
    log::info!("  fmt       Format Rust code using cargo fmt");
    log::info!("  watch     Watch files and run cargo run using cargo-watch");
    log::info!("  publish   Publish packages in monorepo with topological ordering");
    log::info!("  new       Create a new project from template");
    log::info!(
        "  template  Generate template components (controller|domain|exception|mapper|model|repository|service|utils|view)"
    );
    log::info!("  -h, --help      Print this help message");
    log::info!("  -v, --version   Print version information");
    log::info!("");
    log::info!("New Options:");
    log::info!("  <PROJECT_NAME>  Name of the project to create");
    log::info!("");
    log::info!("Bump Options:");
    log::info!("  --patch         Bump patch version (0.1.0 -> 0.1.1) [default]");
    log::info!("  --minor         Bump minor version (0.1.0 -> 0.2.0)");
    log::info!("  --major         Bump major version (0.1.0 -> 1.0.0)");
    log::info!(
        "  --alpha         Add or bump alpha version (0.1.0 -> 0.1.0-alpha, 0.1.0-alpha -> 0.1.0-alpha.1)"
    );
    log::info!(
        "  --beta          Add or bump beta version (0.1.0 -> 0.1.0-beta, 0.1.0-alpha.2 -> 0.1.0-beta.1)"
    );
    log::info!(
        "  --rc            Add or bump rc version (0.1.0 -> 0.1.0-rc, 0.1.0-beta.1 -> 0.1.0-rc.1)"
    );
    log::info!("  --release       Remove pre-release identifier (0.1.0-alpha -> 0.1.0)");
    log::info!("  --manifest-path <PATH>  Path to Cargo.toml [default: Cargo.toml]");
    log::info!("");
    log::info!("Fmt Options:");
    log::info!("  --check         Check formatting without making changes");
    log::info!("  --manifest-path <PATH>  Path to Cargo.toml");
    log::info!("");
    log::info!("Publish Options:");
    log::info!("  --manifest-path <PATH>  Path to workspace Cargo.toml [default: Cargo.toml]");
    log::info!("  --max-retries <N>       Maximum retry attempts per package [default: 3]");
}
```
# Path: hyperlane-cli/src/template/enum.rs
```rust
use super::*;
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum TemplateType {
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
pub enum ModelSubType {
    Application,
    Request,
    Response,
}
#[derive(Debug, thiserror::Error)]
pub enum TemplateError {
    #[error("IO error: {0}")]
    IoError(#[from] io::Error),
    #[error("Invalid template type: {0}")]
    InvalidTemplateType(String),
    #[error("Invalid model subtype: {0}")]
    InvalidModelSubType(String),
    #[error("Directory '{0}' already exists")]
    DirectoryExists(String),
}
```
# Path: hyperlane-cli/src/template/struct.rs
```rust
use super::*;
#[derive(Clone, Debug)]
pub struct TemplateConfig {
    pub template_type: TemplateType,
    pub component_name: String,
    pub model_sub_type: Option<ModelSubType>,
    pub base_directory: String,
}
```
# Path: hyperlane-cli/src/template/impl.rs
```rust
use super::*;
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
    pub fn new(
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
# Path: hyperlane-cli/src/template/mod.rs
```rust
mod r#enum;
mod r#fn;
mod r#impl;
mod r#struct;
pub use {r#enum::*, r#fn::*, r#struct::*};
use super::*;
```
# Path: hyperlane-cli/src/template/fn.rs
```rust
use super::*;
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
async fn ensure_directory(path: &Path) -> Result<(), TemplateError> {
    if !path.exists() {
        create_dir_all(path).await?;
    }
    Ok(())
}
async fn write_mod_rs(path: &Path, modules: &[&str]) -> Result<(), TemplateError> {
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
    write(path, content).await?;
    Ok(())
}
async fn write_empty_mod_rs(path: &Path) -> Result<(), TemplateError> {
    write(path, "\n").await?;
    Ok(())
}
async fn create_controller_template(
    target_dir: &Path,
    _component_name: &str,
) -> Result<(), TemplateError> {
    ensure_directory(target_dir).await?;
    let mod_rs: PathBuf = target_dir.join("mod.rs");
    write_mod_rs(&mod_rs, &["fn", "impl", "struct"]).await?;
    let fn_rs: PathBuf = target_dir.join("fn.rs");
    write(&fn_rs, "use super::*;\n").await?;
    let impl_rs: PathBuf = target_dir.join("impl.rs");
    write(&impl_rs, "use super::*;\n").await?;
    let struct_rs: PathBuf = target_dir.join("struct.rs");
    write(&struct_rs, "use super::*;\n").await?;
    Ok(())
}
async fn create_view_template(
    target_dir: &Path,
    _component_name: &str,
) -> Result<(), TemplateError> {
    ensure_directory(target_dir).await?;
    let mod_rs: PathBuf = target_dir.join("mod.rs");
    write_mod_rs(&mod_rs, &["fn", "impl", "struct"]).await?;
    let fn_rs: PathBuf = target_dir.join("fn.rs");
    write(&fn_rs, "use super::*;\n").await?;
    let impl_rs: PathBuf = target_dir.join("impl.rs");
    write(&impl_rs, "use super::*;\n").await?;
    let struct_rs: PathBuf = target_dir.join("struct.rs");
    write(&struct_rs, "use super::*;\n").await?;
    Ok(())
}
async fn create_service_template(
    target_dir: &Path,
    _component_name: &str,
) -> Result<(), TemplateError> {
    ensure_directory(target_dir).await?;
    let mod_rs: PathBuf = target_dir.join("mod.rs");
    write_mod_rs(&mod_rs, &["impl", "struct"]).await?;
    let impl_rs: PathBuf = target_dir.join("impl.rs");
    write(&impl_rs, "use super::*;\n").await?;
    let struct_rs: PathBuf = target_dir.join("struct.rs");
    write(&struct_rs, "use super::*;\n").await?;
    Ok(())
}
async fn create_domain_template(
    target_dir: &Path,
    _component_name: &str,
) -> Result<(), TemplateError> {
    ensure_directory(target_dir).await?;
    let mod_rs: PathBuf = target_dir.join("mod.rs");
    write_mod_rs(&mod_rs, &["impl", "struct"]).await?;
    let impl_rs: PathBuf = target_dir.join("impl.rs");
    write(&impl_rs, "use super::*;\n").await?;
    let struct_rs: PathBuf = target_dir.join("struct.rs");
    write(&struct_rs, "use super::*;\n").await?;
    Ok(())
}
async fn create_mapper_template(
    target_dir: &Path,
    _component_name: &str,
) -> Result<(), TemplateError> {
    ensure_directory(target_dir).await?;
    let mod_rs: PathBuf = target_dir.join("mod.rs");
    write_mod_rs(
        &mod_rs,
        &["const", "enum", "fn", "impl", "static", "struct"],
    )
    .await?;
    let const_rs: PathBuf = target_dir.join("const.rs");
    write(&const_rs, "use super::*;\n").await?;
    let enum_rs: PathBuf = target_dir.join("enum.rs");
    write(&enum_rs, "use super::*;\n").await?;
    let fn_rs: PathBuf = target_dir.join("fn.rs");
    write(&fn_rs, "use super::*;\n").await?;
    let impl_rs: PathBuf = target_dir.join("impl.rs");
    write(&impl_rs, "use super::*;\n").await?;
    let static_rs: PathBuf = target_dir.join("static.rs");
    write(&static_rs, "use super::*;\n").await?;
    let struct_rs: PathBuf = target_dir.join("struct.rs");
    write(&struct_rs, "use super::*;\n").await?;
    Ok(())
}
async fn create_utils_template(
    target_dir: &Path,
    _component_name: &str,
) -> Result<(), TemplateError> {
    ensure_directory(target_dir).await?;
    let mod_rs: PathBuf = target_dir.join("mod.rs");
    write_mod_rs(&mod_rs, &["fn"]).await?;
    let fn_rs: PathBuf = target_dir.join("fn.rs");
    write(&fn_rs, "use super::*;\n").await?;
    Ok(())
}
async fn create_exception_template(
    target_dir: &Path,
    _component_name: &str,
) -> Result<(), TemplateError> {
    ensure_directory(target_dir).await?;
    let mod_rs: PathBuf = target_dir.join("mod.rs");
    write_empty_mod_rs(&mod_rs).await?;
    Ok(())
}
async fn create_repository_template(
    target_dir: &Path,
    _component_name: &str,
) -> Result<(), TemplateError> {
    ensure_directory(target_dir).await?;
    let mod_rs: PathBuf = target_dir.join("mod.rs");
    write_mod_rs(&mod_rs, &["impl", "struct"]).await?;
    let impl_rs: PathBuf = target_dir.join("impl.rs");
    write(&impl_rs, "use super::*;\n").await?;
    let struct_rs: PathBuf = target_dir.join("struct.rs");
    write(&struct_rs, "use super::*;\n").await?;
    Ok(())
}
async fn create_model_template(
    target_dir: &Path,
    _component_name: &str,
    sub_type: &ModelSubType,
) -> Result<(), TemplateError> {
    let sub_type_name: String = get_model_sub_type_name(sub_type);
    let model_dir: PathBuf = target_dir.join(&sub_type_name);
    ensure_directory(&model_dir).await?;
    let mod_rs: PathBuf = model_dir.join("mod.rs");
    write_mod_rs(&mod_rs, &["struct"]).await?;
    let struct_rs: PathBuf = model_dir.join("struct.rs");
    write(&struct_rs, "use super::*;\n").await?;
    Ok(())
}
pub async fn execute_template(
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
    ensure_directory(&type_dir).await?;
    match config.template_type {
        TemplateType::Controller => {
            create_controller_template(&target_dir, &config.component_name).await?
        }
        TemplateType::View => create_view_template(&target_dir, &config.component_name).await?,
        TemplateType::Service => {
            create_service_template(&target_dir, &config.component_name).await?
        }
        TemplateType::Domain => create_domain_template(&target_dir, &config.component_name).await?,
        TemplateType::Mapper => create_mapper_template(&target_dir, &config.component_name).await?,
        TemplateType::Utils => create_utils_template(&target_dir, &config.component_name).await?,
        TemplateType::Exception => {
            create_exception_template(&target_dir, &config.component_name).await?
        }
        TemplateType::Repository => {
            create_repository_template(&target_dir, &config.component_name).await?
        }
        TemplateType::Model => {
            let sub_type: ModelSubType = config.model_sub_type.ok_or_else(|| {
                TemplateError::InvalidModelSubType("Missing model subtype".to_string())
            })?;
            create_model_template(&target_dir, &config.component_name, &sub_type).await?;
        }
    }
    let _: Result<(), io::Error> = crate::fmt::format_path(&target_dir).await;
    log::info!(
        "Created {dir_name} '{}' at {}",
        config.component_name,
        target_dir.display()
    );
    Ok(())
}
```
# Path: hyperlane-cli/src/version/mod.rs
```rust
mod r#fn;
pub use r#fn::*;
```
# Path: hyperlane-cli/src/version/fn.rs
```rust
pub fn print_version() {
    log::info!("hyperlane-cli {}", env!("CARGO_PKG_VERSION"));
}
```
# Path: hyperlane-cli/src/logger/struct.rs
```rust
use lombok_macros::{Data, New};
#[derive(Data, New)]
pub struct Logger;
```
# Path: hyperlane-cli/src/logger/const.rs
```rust
pub(crate) const LOG_SPACE: &str = " ";
pub(crate) const LOG_COLON: &str = ":";
```
# Path: hyperlane-cli/src/logger/static.rs
```rust
use super::*;
pub(crate) static LOGGER: Logger = Logger;
```
# Path: hyperlane-cli/src/logger/impl.rs
```rust
use super::*;
impl log::Log for Logger {
    fn enabled(&self, metadata: &log::Metadata) -> bool {
        metadata.level() <= log::max_level()
    }
    fn log(&self, record: &log::Record) {
        if !self.enabled(record.metadata()) {
            return;
        }
        let now_time: String = color_output::time();
        let level: log::Level = record.level();
        let args: &std::fmt::Arguments<'_> = record.args();
        let file: Option<&str> = record.file();
        let module_path: Option<&str> = record.module_path();
        let target: &str = record.target();
        let line: u32 = record.line().unwrap_or_default();
        let location: &str = file.unwrap_or(module_path.unwrap_or(target));
        let time_text: String = format!("{LOG_SPACE}{now_time}{LOG_SPACE}");
        let level_text: String = format!("{LOG_SPACE}{level}{LOG_SPACE}");
        let args_text: String = format!("{args}{LOG_SPACE}");
        let location_text: String = format!("{LOG_SPACE}{location}{LOG_COLON}{line}{LOG_SPACE}");
        let color: ColorType = match record.level() {
            log::Level::Trace => ColorType::Use(Color::Magenta),
            log::Level::Debug => ColorType::Use(Color::Cyan),
            log::Level::Info => ColorType::Use(Color::Green),
            log::Level::Warn => ColorType::Use(Color::Yellow),
            log::Level::Error => ColorType::Use(Color::Red),
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
    }
    fn flush(&self) {}
}
impl Logger {
    pub fn init(level_filter: log::LevelFilter) {
        let _: Result<(), SetLoggerError> = log::set_logger(&LOGGER);
        log::set_max_level(level_filter);
    }
}
```
# Path: hyperlane-cli/src/logger/mod.rs
```rust
mod r#const;
mod r#impl;
mod r#static;
mod r#struct;
pub use r#struct::*;
pub use {::log, color_output::*};
pub(crate) use {r#const::*, r#static::*};
use log::SetLoggerError;
```
# Path: hyperlane-cli/src/bump/enum.rs
```rust
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum BumpVersionType {
    Patch,
    Minor,
    Major,
    Release,
    Alpha,
    Beta,
    Rc,
}
```
# Path: hyperlane-cli/src/bump/struct.rs
```rust
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Version {
    pub major: u64,
    pub minor: u64,
    pub patch: u64,
    pub prerelease: Option<String>,
}
```
# Path: hyperlane-cli/src/bump/mod.rs
```rust
mod r#enum;
mod r#fn;
mod r#struct;
pub use {r#enum::*, r#fn::*, r#struct::*};
use super::*;
```
# Path: hyperlane-cli/src/bump/fn.rs
```rust
use super::*;
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
                && pre_type == target_type
                && number > 0
            {
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
pub async fn execute_bump(
    manifest_path: &str,
    bump_type: &BumpVersionType,
) -> Result<String, Box<dyn std::error::Error>> {
    let path: &Path = Path::new(manifest_path);
    let content: String = read_to_string(path).await?;
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
                    "{}{version_string}{}",
                    &line[..version_start],
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
    write(path, updated_content).await?;
    match new_version {
        Some(v) => Ok(v),
        None => Err("failed to bump version".into()),
    }
}
```
# Path: hyperlane-cli/src/config/struct.rs
```rust
use super::*;
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
# Path: hyperlane-cli/src/config/mod.rs
```rust
mod r#fn;
mod r#struct;
pub use {r#fn::*, r#struct::*};
use super::*;
```
# Path: hyperlane-cli/src/config/fn.rs
```rust
use super::*;
pub fn parse_args() -> Args {
    let raw_args: Vec<String> = args().collect();
    let mut command: CommandType = CommandType::Help;
    let mut check: bool = false;
    let mut manifest_path: Option<String> = None;
    let mut bump_type: Option<BumpVersionType> = None;
    let mut max_retries: u32 = 8;
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
            "fmt" if (command == CommandType::Help || command == CommandType::Version) => {
                command = CommandType::Fmt;
            }
            "watch" if (command == CommandType::Help || command == CommandType::Version) => {
                command = CommandType::Watch;
            }
            "bump" if (command == CommandType::Help || command == CommandType::Version) => {
                command = CommandType::Bump;
            }
            "publish" if (command == CommandType::Help || command == CommandType::Version) => {
                command = CommandType::Publish;
            }
            "new" if (command == CommandType::Help || command == CommandType::Version) => {
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
            "template" if (command == CommandType::Help || command == CommandType::Version) => {
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
                    && let Ok(n) = raw_args[i].parse::<u32>()
                {
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
# Path: hyperlane-cli/src/publish/enum.rs
```rust
use super::*;
#[derive(Debug, thiserror::Error)]
pub enum PublishError {
    #[error("Failed to parse Cargo.toml")]
    ManifestParseError,
    #[error("Circular dependency detected")]
    CircularDependency,
    #[error("IO error: {0}")]
    IoError(#[from] io::Error),
}
```
# Path: hyperlane-cli/src/publish/struct.rs
```rust
use super::*;
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Package {
    pub name: String,
    pub version: String,
    pub path: PathBuf,
    pub local_dependencies: Vec<String>,
}
#[derive(Clone, Debug)]
pub struct PublishResult {
    pub package_name: String,
    pub success: bool,
    pub error: Option<String>,
    pub retries: u32,
}
```
# Path: hyperlane-cli/src/publish/mod.rs
```rust
mod r#enum;
mod r#fn;
mod r#struct;
pub use {r#enum::*, r#fn::*, r#struct::*};
use super::*;
```
# Path: hyperlane-cli/src/publish/fn.rs
```rust
use super::*;
async fn discover_packages(workspace_root: &Path) -> Result<Vec<Package>, PublishError> {
    let content: String = read_to_string(workspace_root).await?;
    let doc: Value = toml::from_str(&content).map_err(|_| PublishError::ManifestParseError)?;
    let mut packages: Vec<Package> = Vec::new();
    if let Some(workspace) = doc.get("workspace")
        && let Some(members) = workspace
            .get("members")
            .and_then(|members_value: &Value| members_value.as_array())
    {
        for member in members {
            if let Some(pattern) = member.as_str() {
                let base_path: &Path = workspace_root.parent().unwrap_or(workspace_root);
                expand_pattern(base_path, pattern, &mut packages).await?;
            }
        }
    }
    if packages.is_empty() {
        let package: Package = read_single_package(workspace_root).await?;
        packages.push(package);
    }
    Ok(packages)
}
async fn expand_pattern(
    base_path: &Path,
    pattern: &str,
    packages: &mut Vec<Package>,
) -> Result<(), PublishError> {
    if pattern.contains('*') {
        let parent: &Path = Path::new(pattern).parent().unwrap_or(Path::new("."));
        let full_parent: PathBuf = base_path.join(parent);
        if full_parent.is_dir() {
            let mut entries: ReadDir = read_dir(&full_parent).await?;
            while let Some(entry) = entries.next_entry().await? {
                let path: PathBuf = entry.path();
                if path.is_dir() {
                    let cargo_toml: PathBuf = path.join("Cargo.toml");
                    if cargo_toml.exists() {
                        let package: Package = read_package_manifest(&cargo_toml).await?;
                        packages.push(package);
                    }
                }
            }
        }
    } else {
        let cargo_toml: PathBuf = base_path.join(pattern).join("Cargo.toml");
        if cargo_toml.exists() {
            let package: Package = read_package_manifest(&cargo_toml).await?;
            packages.push(package);
        }
    }
    Ok(())
}
async fn read_single_package(manifest_path: &Path) -> Result<Package, PublishError> {
    read_package_manifest(manifest_path).await
}
async fn read_package_manifest(manifest_path: &Path) -> Result<Package, PublishError> {
    let content: String = read_to_string(manifest_path).await?;
    let doc: Value = toml::from_str(&content).map_err(|_| PublishError::ManifestParseError)?;
    let package_table: &Value = doc.get("package").ok_or(PublishError::ManifestParseError)?;
    let name: String = package_table
        .get("name")
        .and_then(|n: &Value| n.as_str())
        .ok_or(PublishError::ManifestParseError)?
        .to_string();
    let version: String = package_table
        .get("version")
        .and_then(|v: &Value| v.as_str())
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
    doc: &Value,
    _manifest_path: &Path,
) -> Result<Vec<String>, PublishError> {
    let mut deps: Vec<String> = Vec::new();
    let dep_sections: [&str; 3] = ["dependencies", "dev-dependencies", "build-dependencies"];
    for section in &dep_sections {
        if let Some(table) = doc
            .get(section)
            .and_then(|section_value: &Value| section_value.as_table())
        {
            for (dep_name, dep_value) in table {
                let is_local: bool = match dep_value {
                    Value::Table(t) => {
                        t.get("path").is_some()
                            || t.get("workspace")
                                .and_then(|workspace_value: &Value| workspace_value.as_bool())
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
        .map(|package: &Package| (package.name.clone(), package.clone()))
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
                    sleep(Duration::from_secs(2_u64.pow(attempt))).await;
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
pub async fn execute_publish(
    manifest_path: &str,
    max_retries: u32,
) -> Result<Vec<PublishResult>, PublishError> {
    let path: &Path = Path::new(manifest_path);
    let packages: Vec<Package> = discover_packages(path).await?;
    if packages.is_empty() {
        return Ok(Vec::new());
    }
    let sorted_packages: Vec<Package> = topological_sort(&packages)?;
    let mut results: Vec<PublishResult> = Vec::new();
    for package in sorted_packages {
        log::info!("Publishing {} v{}...", package.name, package.version);
        let result: PublishResult = publish_package_with_retry(&package, max_retries).await;
        if result.success {
            if result.retries == 0 {
                log::info!("Successfully published {}", result.package_name,);
            } else {
                log::info!(
                    "Successfully published {} (retried {} times)",
                    result.package_name,
                    result.retries
                );
            }
        } else if let Some(error) = &result.error {
            log::error!("Failed to publish {}: {error}", result.package_name);
        } else {
            log::error!("Failed to publish {}", result.package_name);
        }
        results.push(result);
    }
    Ok(results)
}
```
# Path: hyperlane-cli/src/new/enum.rs
```rust
use super::*;
#[derive(Debug, thiserror::Error)]
pub enum NewError {
    #[error("IO error: {0}")]
    IoError(#[from] io::Error),
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
# Path: hyperlane-cli/src/new/struct.rs
```rust
#[derive(Clone, Debug)]
pub struct NewProjectConfig {
    pub project_name: String,
    pub template_url: String,
}
```
# Path: hyperlane-cli/src/new/impl.rs
```rust
use super::*;
impl NewProjectConfig {
    pub fn new(project_name: String) -> Self {
        Self {
            project_name,
            template_url: "https://github.com/hyperlane-dev/hyperlane-quick-start".to_string(),
        }
    }
}
```
# Path: hyperlane-cli/src/new/mod.rs
```rust
mod r#enum;
mod r#fn;
mod r#impl;
mod r#struct;
pub use {r#enum::*, r#fn::*, r#struct::*};
use super::*;
```
# Path: hyperlane-cli/src/new/fn.rs
```rust
use super::*;
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
pub async fn execute_new(project_name: &str) -> Result<(), NewError> {
    validate_project_name(project_name)?;
    check_git_available().await?;
    let config: NewProjectConfig = NewProjectConfig::new(project_name.to_string());
    log::info!(
        "Creating new project '{}' from template...",
        config.project_name
    );
    git_clone(&config).await?;
    log::info!("Successfully created project '{}'", config.project_name);
    log::info!("  cd {}", config.project_name);
    log::info!("  cargo build");
    Ok(())
}
```
# Path: hyperlane-cli/src/command/enum.rs
```rust
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum CommandType {
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
# Path: hyperlane-cli/src/command/mod.rs
```rust
mod r#enum;
pub use r#enum::*;
```
# Path: hyperlane-cli/src/watch/mod.rs
```rust
mod r#fn;
pub use r#fn::*;
use super::*;
```
# Path: hyperlane-cli/src/watch/fn.rs
```rust
use super::*;
async fn run_cargo_run() -> Result<(), io::Error> {
    let output: std::process::Output = Command::new("cargo")
        .arg("run")
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .output()
        .await?;
    let stdout: String = String::from_utf8_lossy(&output.stdout).trim().to_string();
    let stderr: String = String::from_utf8_lossy(&output.stderr).trim().to_string();
    if !stdout.is_empty() {
        for line in stdout.lines() {
            log::info!("{line}");
        }
    }
    if !stderr.is_empty() {
        if output.status.success() {
            for line in stderr.lines() {
                if line.is_empty() {
                    continue;
                }
                log::info!("{line}");
            }
        } else {
            for line in stderr.lines() {
                if line.is_empty() {
                    continue;
                }
                log::error!("{line}");
            }
            log::error!("cargo run failed");
        }
    }
    Ok(())
}
pub async fn execute_watch() -> Result<(), io::Error> {
    let src_path: PathBuf = PathBuf::from("src");
    if !src_path.exists() {
        return Err(io::Error::other(
            "src directory not found in current directory",
        ));
    }
    run_cargo_run().await?;
    let (tx, mut rx): (Sender<Event>, Receiver<Event>) = channel(Event::new(EventKind::Any));
    let mut watcher: RecommendedWatcher =
        recommended_watcher(move |result: Result<Event, notify::Error>| {
            if let Ok(event) = result {
                let _: Result<(), tokio::sync::watch::error::SendError<Event>> = tx.send(event);
            }
        })
        .map_err(|error: notify::Error| io::Error::other(error.to_string()))?;
    watcher
        .watch(&src_path, RecursiveMode::Recursive)
        .map_err(|error: notify::Error| io::Error::other(error.to_string()))?;
    log::info!("Watching src/ for changes...");
    let mut debounce: Interval = interval(Duration::from_millis(500));
    debounce.tick().await;
    while rx.changed().await.is_ok() {
        let event: Event = rx.borrow().clone();
        let has_rust_change: bool = event
            .paths
            .iter()
            .any(|path: &PathBuf| path.extension().is_some_and(|ext: &OsStr| ext == "rs"));
        if !has_rust_change {
            continue;
        }
        log::warn!("File change detected: {}", event.paths[0].display());
        debounce.reset();
        sleep(Duration::from_millis(300)).await;
        run_cargo_run().await?;
    }
    Ok(())
}
```
# Path: hyperlane-cli/tests/mod.rs
```rust
mod bump;
mod config;
mod fmt;
mod new;
mod publish;
mod version;
use hyperlane_cli::*;
use std::{
    io::{self, Error},
    path::PathBuf,
};
use tokio::fs::{create_dir_all, read_to_string, write};
```
# Path: hyperlane-cli/tests/fmt/mod.rs
```rust
mod r#fn;
use super::*;
```
# Path: hyperlane-cli/tests/fmt/fn.rs
```rust
use super::*;
#[tokio::test]
async fn test_format_path_integration() {
    let tmp_dir: PathBuf = PathBuf::from("./tmp/test_fmt");
    let _: Result<(), Error> = create_dir_all(&tmp_dir).await;
    let test_file: PathBuf = tmp_dir.join("test.rs");
    write(&test_file, "fn main() {\n    println!(\"hello\");\n}\n")
        .await
        .unwrap();
    let result: Result<(), io::Error> = format_path(&tmp_dir).await;
    assert!(result.is_ok());
}
```
# Path: hyperlane-cli/tests/version/mod.rs
```rust
mod r#fn;
use super::*;
```
# Path: hyperlane-cli/tests/version/fn.rs
```rust
use super::*;
#[test]
fn test_print_version_runs() {
    print_version();
}
```
# Path: hyperlane-cli/tests/bump/mod.rs
```rust
mod r#fn;
use super::*;
```
# Path: hyperlane-cli/tests/bump/fn.rs
```rust
use super::*;
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
#[tokio::test]
async fn test_execute_bump_integration() {
    let tmp_dir: PathBuf = PathBuf::from("./tmp/test_bump");
    create_dir_all(&tmp_dir).await.unwrap();
    let manifest_path: PathBuf = tmp_dir.join("Cargo.toml");
    let content: &str = r#"[package]
name = "test-package"
version = "0.1.0"
edition = "2024"
"#;
    write(&manifest_path, content).await.unwrap();
    let result: Result<String, Box<dyn std::error::Error>> =
        execute_bump(manifest_path.to_str().unwrap(), &BumpVersionType::Patch).await;
    assert!(result.is_ok());
    assert_eq!(result.unwrap(), "0.1.1");
    let updated_content: String = read_to_string(&manifest_path).await.unwrap();
    assert!(updated_content.contains("version = \"0.1.1\""));
}
#[tokio::test]
async fn test_execute_bump_minor() {
    let tmp_dir: PathBuf = PathBuf::from("./tmp/test_bump_minor");
    create_dir_all(&tmp_dir).await.unwrap();
    let manifest_path: PathBuf = tmp_dir.join("Cargo.toml");
    let content: &str = r#"[package]
name = "test-package"
version = "0.1.0"
edition = "2024"
"#;
    write(&manifest_path, content).await.unwrap();
    let result: Result<String, Box<dyn std::error::Error>> =
        execute_bump(manifest_path.to_str().unwrap(), &BumpVersionType::Minor).await;
    assert!(result.is_ok());
    assert_eq!(result.unwrap(), "0.2.0");
}
#[tokio::test]
async fn test_execute_bump_major() {
    let tmp_dir: PathBuf = PathBuf::from("./tmp/test_bump_major");
    create_dir_all(&tmp_dir).await.unwrap();
    let manifest_path: PathBuf = tmp_dir.join("Cargo.toml");
    let content: &str = r#"[package]
name = "test-package"
version = "0.1.0"
edition = "2024"
"#;
    write(&manifest_path, content).await.unwrap();
    let result: Result<String, Box<dyn std::error::Error>> =
        execute_bump(manifest_path.to_str().unwrap(), &BumpVersionType::Major).await;
    assert!(result.is_ok());
    assert_eq!(result.unwrap(), "1.0.0");
}
#[tokio::test]
async fn test_execute_bump_alpha() {
    let tmp_dir: PathBuf = PathBuf::from("./tmp/test_bump_alpha");
    create_dir_all(&tmp_dir).await.unwrap();
    let manifest_path: PathBuf = tmp_dir.join("Cargo.toml");
    let content: &str = r#"[package]
name = "test-package"
version = "0.1.0"
edition = "2024"
"#;
    write(&manifest_path, content).await.unwrap();
    let result: Result<String, Box<dyn std::error::Error>> =
        execute_bump(manifest_path.to_str().unwrap(), &BumpVersionType::Alpha).await;
    assert!(result.is_ok());
    assert_eq!(result.unwrap(), "0.1.0-alpha");
}
#[tokio::test]
async fn test_execute_bump_beta() {
    let tmp_dir: PathBuf = PathBuf::from("./tmp/test_bump_beta");
    create_dir_all(&tmp_dir).await.unwrap();
    let manifest_path: PathBuf = tmp_dir.join("Cargo.toml");
    let content: &str = r#"[package]
name = "test-package"
version = "0.1.0-alpha.2"
edition = "2024"
"#;
    write(&manifest_path, content).await.unwrap();
    let result: Result<String, Box<dyn std::error::Error>> =
        execute_bump(manifest_path.to_str().unwrap(), &BumpVersionType::Beta).await;
    assert!(result.is_ok());
    assert_eq!(result.unwrap(), "0.1.0-beta.1");
}
#[tokio::test]
async fn test_execute_bump_rc() {
    let tmp_dir: PathBuf = PathBuf::from("./tmp/test_bump_rc");
    create_dir_all(&tmp_dir).await.unwrap();
    let manifest_path: PathBuf = tmp_dir.join("Cargo.toml");
    let content: &str = r#"[package]
name = "test-package"
version = "0.1.0-beta.1"
edition = "2024"
"#;
    write(&manifest_path, content).await.unwrap();
    let result: Result<String, Box<dyn std::error::Error>> =
        execute_bump(manifest_path.to_str().unwrap(), &BumpVersionType::Rc).await;
    assert!(result.is_ok());
    assert_eq!(result.unwrap(), "0.1.0-rc.1");
}
#[tokio::test]
async fn test_execute_bump_release() {
    let tmp_dir: PathBuf = PathBuf::from("./tmp/test_bump_release");
    create_dir_all(&tmp_dir).await.unwrap();
    let manifest_path: PathBuf = tmp_dir.join("Cargo.toml");
    let content: &str = r#"[package]
name = "test-package"
version = "0.1.0-alpha"
edition = "2024"
"#;
    write(&manifest_path, content).await.unwrap();
    let result: Result<String, Box<dyn std::error::Error>> =
        execute_bump(manifest_path.to_str().unwrap(), &BumpVersionType::Release).await;
    assert!(result.is_ok());
    assert_eq!(result.unwrap(), "0.1.0");
}
#[tokio::test]
async fn test_execute_bump_no_version_field() {
    let tmp_dir: PathBuf = PathBuf::from("./tmp/test_bump_no_version");
    create_dir_all(&tmp_dir).await.unwrap();
    let manifest_path: PathBuf = tmp_dir.join("Cargo.toml");
    let content: &str = r#"[package]
name = "test-package"
edition = "2024"
"#;
    write(&manifest_path, content).await.unwrap();
    let result: Result<String, Box<dyn std::error::Error>> =
        execute_bump(manifest_path.to_str().unwrap(), &BumpVersionType::Patch).await;
    assert!(result.is_err());
}
```
# Path: hyperlane-cli/tests/config/mod.rs
```rust
mod r#fn;
use super::*;
```
# Path: hyperlane-cli/tests/config/fn.rs
```rust
use super::*;
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
# Path: hyperlane-cli/tests/publish/mod.rs
```rust
mod r#fn;
use super::*;
```
# Path: hyperlane-cli/tests/publish/fn.rs
```rust
use super::*;
#[test]
fn test_package_creation() {
    let package: Package = Package {
        name: "test-package".to_string(),
        version: "0.1.0".to_string(),
        path: PathBuf::from("."),
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
        path: PathBuf::from("."),
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
        path: PathBuf::from("."),
        local_dependencies: vec![],
    };
    let package2: Package = Package {
        name: "test".to_string(),
        version: "0.1.0".to_string(),
        path: PathBuf::from("."),
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
    let io_error: io::Error = io::Error::new(io::ErrorKind::NotFound, "test");
    let publish_error: PublishError = PublishError::from(io_error);
    assert!(publish_error.to_string().contains("IO error"));
}
```
# Path: hyperlane-cli/tests/new/mod.rs
```rust
mod r#fn;
use super::*;
```
# Path: hyperlane-cli/tests/new/fn.rs
```rust
use super::*;
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
    let io_error: io::Error = io::Error::new(io::ErrorKind::NotFound, "test");
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
# Path: hyperlane-log/README.md
## hyperlane-log
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
# Path: hyperlane-log/src/trait.rs
```rust
pub trait FileLoggerFuncTrait<T: AsRef<str>>: Fn(T) -> String + Send + Sync {}
```
# Path: hyperlane-log/src/lib.rs
```rust
mod r#const;
mod r#fn;
mod r#impl;
mod r#struct;
mod r#trait;
pub use {r#const::*, r#fn::*, r#struct::*, r#trait::*};
use std::{fs::read_dir, io::Error};
use {file_operation::*, hyperlane_time::*};
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
# Path: hyperlane-log/src/impl.rs
```rust
use super::*;
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
        let _: Result<(), Error> = append_to_file(&path, out.as_bytes());
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
        let _: Result<(), Error> = async_append_to_file(&path, out.as_bytes()).await;
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
# Path: hyperlane-log/src/fn.rs
```rust
use super::*;
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
# Path: hyperlane-log/tests/mod.rs
```rust
mod log;
use hyperlane_log::*;
```
# Path: hyperlane-log/tests/log/mod.rs
```rust
mod r#fn;
use super::*;
```
# Path: hyperlane-log/tests/log/fn.rs
```rust
use super::*;
#[tokio::test]
async fn test() {
    let log: FileLogger = FileLogger::new("./logs", 1_024_000);
    let trace_str: String = String::from("custom trace message");
    log.trace(trace_str, |trace: String| {
        let write_data: String = format!("User trace func => {trace:#?}\n");
        write_data
    });
    let debug_str: String = String::from("custom debug message");
    log.debug(debug_str, |debug: String| {
        let write_data: String = format!("User debug func => {debug:#?}\n");
        write_data
    });
    let info_str: String = String::from("custom info message");
    log.info(info_str, |info: String| {
        let write_data: String = format!("User info func => {info:?}\n");
        write_data
    });
    let warn_str: String = String::from("custom warn message");
    log.warn(warn_str, |warn: String| {
        let write_data: String = format!("User warn func => {warn:#?}\n");
        write_data
    });
    let error_str: String = String::from("custom error message");
    log.error(error_str, |error: String| {
        let write_data: String = format!("User error func => {error:?}\n");
        write_data
    });
    let async_trace_str: String = String::from("custom async trace message");
    log.async_trace(async_trace_str, |trace: String| {
        let write_data: String = format!("User trace func => {trace:#?}\n");
        write_data
    })
    .await;
    let async_debug_str: String = String::from("custom async debug message");
    log.async_debug(async_debug_str, |debug: String| {
        let write_data: String = format!("User debug func => {debug:#?}\n");
        write_data
    })
    .await;
    let async_info_str: String = String::from("custom async info message");
    log.async_info(async_info_str, |info: String| {
        let write_data: String = format!("User info func => {info:?}\n");
        write_data
    })
    .await;
    let async_warn_str: String = String::from("custom async warn message");
    log.async_warn(async_warn_str, |warn: String| {
        let write_data: String = format!("User warn func => {warn:#?}\n");
        write_data
    })
    .await;
    let async_error_str: String = String::from("custom async error message");
    log.async_error(async_error_str, |error: String| {
        let write_data: String = format!("User error func => {error:?}\n");
        write_data
    })
    .await;
}
#[tokio::test]
async fn test_more_log_first() {
    let log: FileLogger = FileLogger::new("./logs", DISABLE_LOG_FILE_SIZE);
    log.trace("trace data => ", |trace: &str| {
        let write_data: String = format!("User trace func => {trace:#?}\n");
        write_data
    });
    log.debug("debug data => ", |debug: &str| {
        let write_data: String = format!("User debug func => {debug:#?}\n");
        write_data
    });
    log.info("info data => ", |info: &str| {
        let write_data: String = format!("User info func => {info:?}\n");
        write_data
    });
    log.warn("warn data => ", |warn: &str| {
        let write_data: String = format!("User warn func => {warn:#?}\n");
        write_data
    });
    log.error("error data => ", |error: &str| {
        let write_data: String = format!("User error func => {error:?}\n");
        write_data
    });
    log.async_trace("async trace data => ", |trace: &str| {
        let write_data: String = format!("User trace func => {trace:#?}\n");
        write_data
    })
    .await;
    log.async_debug("async debug data => ", |debug: &str| {
        let write_data: String = format!("User debug func => {debug:#?}\n");
        write_data
    })
    .await;
    log.async_info("async info data => ", |info: &str| {
        let write_data: String = format!("User info func => {info:?}\n");
        write_data
    })
    .await;
    log.async_warn("async warn data => ", |warn: &str| {
        let write_data: String = format!("User warn func => {warn:#?}\n");
        write_data
    })
    .await;
    log.async_error("async error data => ", |error: &str| {
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
# Path: hyperlane-quick-start/README.md
## hyperlane-quick-start
> A lightweight, high-performance, and cross-platform Rust HTTP server library built on Tokio. It simplifies modern web service development by providing built-in support for middleware, WebSocket, Server-Sent Events (SSE), and raw TCP communication. With a unified and ergonomic API across Windows, Linux, and MacOS, it enables developers to build robust, scalable, and event-driven network applications with minimal overhead and maximum flexibility.
## Api Docs
- [Api Docs](https://docs.rs/hyperlane/latest/)
## Contact
# Path: hyperlane-quick-start/bootstrap/lib.rs
```rust
#![recursion_limit = "1024"]
pub mod application;
pub mod common;
pub mod framework;
use common::*;
use {
    hyperlane::*,
    hyperlane_utils::{log::*, *},
};
```
# Path: hyperlane-quick-start/bootstrap/README.md
## hyperlane-bootstrap
> Hyperlane bootstrap crate providing application initialization and framework lifecycle management.
## Api Docs
- [Api Docs](https://docs.rs/hyperlane/latest/)
## Contact
# Path: hyperlane-quick-start/bootstrap/application/mod.rs
```rust
pub mod db;
pub mod env;
pub mod logger;
use super::*;
```
# Path: hyperlane-quick-start/bootstrap/application/logger/struct.rs
```rust
use super::*;
#[derive(Clone, Copy, Data, Debug, Default)]
pub struct LoggerBootstrap;
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
# Path: hyperlane-quick-start/bootstrap/application/env/struct.rs
```rust
use super::*;
#[derive(Clone, Copy, Data, Debug, Default)]
pub struct EnvBootstrap;
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
# Path: hyperlane-quick-start/bootstrap/application/env/mod.rs
```rust
mod r#impl;
mod r#struct;
pub use r#struct::*;
use super::*;
use hyperlane_plugin::env::*;
```
# Path: hyperlane-quick-start/bootstrap/application/db/struct.rs
```rust
use super::*;
#[derive(Clone, Copy, Data, Debug, Default)]
pub struct DbBootstrap;
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
# Path: hyperlane-quick-start/bootstrap/application/db/mod.rs
```rust
mod r#impl;
mod r#struct;
pub use r#struct::*;
use super::*;
use hyperlane_plugin::{common::*, database::*, mysql::*, postgresql::*, redis::*};
use {redis::Connection, sea_orm::DatabaseConnection};
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
# Path: hyperlane-quick-start/bootstrap/framework/mod.rs
```rust
pub mod config;
pub mod runtime;
pub mod server;
use super::*;
```
# Path: hyperlane-quick-start/bootstrap/framework/runtime/struct.rs
```rust
use super::*;
#[derive(Data, Debug)]
pub struct RuntimeBootstrap {
    pub(super) runtime: Runtime,
}
```
# Path: hyperlane-quick-start/bootstrap/framework/runtime/impl.rs
```rust
use super::*;
impl BootstrapSyncInit for RuntimeBootstrap {
    fn init() -> Self {
        let runtime: Runtime = Builder::new_multi_thread()
            .worker_threads(num_cpus::get_physical() << 1)
            .max_blocking_threads(2_048)
            .max_io_events_per_tick(1_024)
            .enable_all()
            .build()
            .unwrap();
        Self { runtime }
    }
}
```
# Path: hyperlane-quick-start/bootstrap/framework/runtime/mod.rs
```rust
mod r#impl;
mod r#struct;
pub use r#struct::*;
use super::*;
use tokio::runtime::{Builder, Runtime};
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
        server_config
            .set_address(Server::format_bind_address(
                env_config.get_server_host(),
                env_config.get_server_port(),
            ))
            .set_ttl(env_config.get_server_tti())
            .set_nodelay(env_config.get_server_nodelay());
        debug!("Server config {server_config:?}");
        info!("Server initialization successful");
        Self {
            server_config,
            request_config,
        }
    }
}
```
# Path: hyperlane-quick-start/bootstrap/framework/config/mod.rs
```rust
mod r#impl;
mod r#struct;
pub use r#struct::*;
use super::*;
use hyperlane_plugin::{common::*, env::*};
```
# Path: hyperlane-quick-start/bootstrap/framework/server/struct.rs
```rust
use super::*;
#[derive(Clone, Copy, Data, Debug, Default)]
pub struct ServerBootstrap;
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
# Path: hyperlane-quick-start/bootstrap/framework/server/mod.rs
```rust
mod r#impl;
mod r#struct;
pub use r#struct::*;
use {super::*, config::*};
#[allow(unused_imports)]
use {hyperlane_application::*, hyperlane_plugin::env::*, hyperlane_plugin::shutdown::*};
```
# Path: hyperlane-quick-start/src/main.rs
```rust
#![recursion_limit = "1024"]
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
# Path: hyperlane-quick-start/resources/lib.rs
```rust
#![recursion_limit = "1024"]
pub mod docker;
pub mod env;
pub mod sql;
pub mod r#static;
pub mod templates;
```
# Path: hyperlane-quick-start/resources/README.md
## hyperlane-resources
> Hyperlane resources module containing various resources and utilities used by the framework.
## Api Docs
- [Api Docs](https://docs.rs/hyperlane/latest/)
## Contact
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
RUN apt-get update -yqq && apt-get install -yqq cmake g++ binutils lld
WORKDIR /hyperlane-quick-start
COPY . .
RUN cargo install wasm-bindgen-cli --locked && \
    cargo install wasm-pack --locked
RUN RUSTFLAGS='-C target-feature=-crt-static' cargo build --release --target x86_64-unknown-linux-gnu && \
    cp -f /hyperlane-quick-start/target/x86_64-unknown-linux-gnu/release/hyperlane-quick-start /hyperlane-quick-start/hyperlane-quick-start
EXPOSE 65002
CMD ["/hyperlane-quick-start/hyperlane-quick-start"]
```
# Path: hyperlane-quick-start/resources/docker/dev/server.dockerfile
```dockerfile
FROM rust:1.93-bookworm
RUN apt-get update -yqq && apt-get install -yqq cmake g++ binutils lld
WORKDIR /hyperlane-quick-start
COPY . .
RUN cargo install wasm-bindgen-cli --locked && \
    cargo install wasm-pack --locked
RUN cargo build && \
    cp -f /hyperlane-quick-start/target/debug/hyperlane-quick-start /hyperlane-quick-start/hyperlane-quick-start
EXPOSE 80
CMD ["/hyperlane-quick-start/hyperlane-quick-start"]
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
GPT_API_URL=http://172.17.0.1:1234/v1/chat/completions
GPT_API_KEY=
GPT_MODEL=
GPT_ENABLE_THINKING=false
MYSQL='[{"name":"mysql_default","host":"release_hyperlane_quick_start_mysql","port":3306,"database":"hyperlane","username":"hyperlane","password":"hyperlane"}]'
POSTGRESQL='[{"name":"postgres_default","host":"release_hyperlane_quick_start_postgresql","port":5432,"database":"hyperlane","username":"hyperlane","password":"hyperlane"}]'
REDIS='[{"name":"redis_default","host":"release_hyperlane_quick_start_redis","port":6379,"username":"","password":"hyperlane"}]'
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
GPT_API_URL=http://127.0.0.1:1234/v1/chat/completions
GPT_API_KEY=
GPT_MODEL=
GPT_ENABLE_THINKING=false
MYSQL='[{"name":"mysql_default","host":"dev_hyperlane_quick_start_mysql","port":3306,"database":"hyperlane","username":"hyperlane","password":"hyperlane"}]'
POSTGRESQL='[{"name":"postgres_default","host":"dev_hyperlane_quick_start_postgresql","port":5432,"database":"hyperlane","username":"hyperlane","password":"hyperlane"}]'
REDIS='[{"name":"redis_default","host":"dev_hyperlane_quick_start_redis","port":6379,"username":"","password":"hyperlane"}]'
SERVER_PORT=80
SERVER_HOST=0.0.0.0
SERVER_BUFFER=8192
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
# Path: hyperlane-quick-start/config/lib.rs
```rust
#![recursion_limit = "1024"]
pub mod application;
pub mod framework;
use hyperlane_utils::log::*;
```
# Path: hyperlane-quick-start/config/README.md
## hyperlane-config
> Hyperlane configuration module providing comprehensive configuration management capabilities for the framework.
## Api Docs
- [Api Docs](https://docs.rs/hyperlane/latest/)
## Contact
# Path: hyperlane-quick-start/config/application/mod.rs
```rust
pub mod logger;
pub mod logo_img;
use super::*;
```
# Path: hyperlane-quick-start/config/application/logo_img/const.rs
```rust
pub const LOGO_IMG_URL: &str = "/github/pages/docs-pages/pages/img/hyperlane.png";
```
# Path: hyperlane-quick-start/config/application/logo_img/mod.rs
```rust
mod r#const;
pub use r#const::*;
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
# Path: hyperlane-quick-start/config/framework/const.rs
```rust
pub const DEFAULT_CACHE_CONTROL_STATIC_ASSETS: &str = "public, max-age=31536000, immutable";
pub const DEFAULT_CACHE_CONTROL_SHORT_TERM: &str = "public, max-age=3600";
pub const DEFAULT_EXPIRES_FAR_FUTURE: &str = "Wed, 1 Apr 8888 00:00:00 GMT";
```
# Path: hyperlane-quick-start/config/framework/mod.rs
```rust
mod r#const;
pub use r#const::*;
```
# Path: hyperlane-quick-start/application/lib.rs
```rust
#![recursion_limit = "1024"]
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
# Path: hyperlane-quick-start/application/README.md
## hyperlane-application
> Hyperlane application module containing core application logic, controllers, services, and middleware components.
## Api Docs
- [Api Docs](https://docs.rs/hyperlane/latest/)
## Contact
# Path: hyperlane-quick-start/application/utils/mod.rs
```rust
pub mod json;
pub mod send;
use super::*;
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
pub async fn try_send_body_hook(
    stream: &mut Stream,
    ctx: &mut Context,
) -> Result<(), ResponseError> {
    let send_result: Result<(), ResponseError> = if ctx.get_request().is_ws_upgrade_type() {
        let body: &ResponseBody = ctx.get_response().get_body();
        let frame_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(body);
        stream.try_send_list(&frame_list).await
    } else {
        let body: &Vec<u8> = ctx.get_response().get_body();
        stream.try_send(body).await
    };
    if send_result.is_err() {
        stream.set_closed(true);
    }
    send_result
}
#[instrument_trace]
pub async fn send_body_hook(stream: &mut Stream, ctx: &mut Context) {
    try_send_body_hook(stream, ctx).await.unwrap()
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
# Path: hyperlane-quick-start/application/exception/impl.rs
```rust
use super::*;
impl ServerHook for TaskPanicHook {
    #[task_panic_data(task_panic_data)]
    #[instrument_trace]
    async fn new(_stream: &mut Stream, ctx: &mut Context) -> Self {
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
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        debug!("TaskPanicHook request => {}", ctx.get_request());
        error!("TaskPanicHook => {}", self.get_response_body());
        let api_response: ApiResponse<&str> = ApiResponse::new(
            ApiResponseStatus::InternalServerError,
            self.get_response_body(),
        );
        let response_body: Vec<u8> = api_response.to_json_bytes();
        Status::Continue
    }
}
impl ServerHook for RequestErrorHook {
    #[request_error_data(request_error_data)]
    #[instrument_trace]
    async fn new(_stream: &mut Stream, ctx: &mut Context) -> Self {
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
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        if self.get_response_status_code() == HttpStatus::BadRequest.code() {
            debug!("Context aborted");
            return Status::Reject;
        }
        if self.get_response_status_code() != HttpStatus::RequestTimeout.code() {
            debug!("RequestErrorHook request => {}", ctx.get_request());
            error!("RequestErrorHook => {}", self.get_response_body());
        }
        let api_response: ApiResponse<&str> = ApiResponse::new(
            ApiResponseStatus::InternalServerError,
            self.get_response_body(),
        );
        let response_body: Vec<u8> = api_response.to_json_bytes();
        Status::Continue
    }
}
```
# Path: hyperlane-quick-start/application/exception/mod.rs
```rust
mod r#impl;
mod r#struct;
pub use r#struct::*;
use {super::*, model::response::common::*};
```
# Path: hyperlane-quick-start/application/middleware/mod.rs
```rust
pub mod request;
pub mod response;
use {super::*, utils::json::*};
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
# Path: hyperlane-quick-start/application/middleware/response/impl.rs
```rust
use super::*;
impl ServerHook for SendMiddleware {
    #[instrument_trace]
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        reject(ctx.get_request().is_ws_upgrade_type()),
        try_send
    )]
    #[instrument_trace]
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
impl ServerHook for LogMiddleware {
    #[instrument_trace]
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[instrument_trace]
    async fn handle(self, _: &mut Stream, ctx: &mut Context) -> Status {
        let request_json: String = get_request_json(ctx).await;
        let response_json: String = get_response_json(ctx).await;
        info!("{request_json}");
        info!("{response_json}");
        Status::Continue
    }
}
```
# Path: hyperlane-quick-start/application/middleware/response/mod.rs
```rust
mod r#impl;
mod r#struct;
pub use r#struct::*;
use super::*;
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
pub struct OptionMethodMiddleware;
#[request_middleware(6)]
#[derive(Clone, Copy, Data, Debug, Default)]
pub struct UpgradeMiddleware;
```
# Path: hyperlane-quick-start/application/middleware/request/impl.rs
```rust
use super::*;
impl ServerHook for HttpRequestMiddleware {
    #[instrument_trace]
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        reject(ctx.get_request().get_version().is_http()),
        send,
    )]
    #[instrument_trace]
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        stream.set_closed(true);
        Status::Continue
    }
}
impl ServerHook for CrossMiddleware {
    #[instrument_trace]
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[response_version(HttpVersion::Http1_1)]
    #[response_header(ACCESS_CONTROL_ALLOW_ORIGIN => WILDCARD_ANY)]
    #[response_header(ACCESS_CONTROL_ALLOW_METHODS => ALL_METHODS)]
    #[response_header(ACCESS_CONTROL_ALLOW_HEADERS => WILDCARD_ANY)]
    #[instrument_trace]
    async fn handle(self, _stream: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
impl ServerHook for ResponseHeaderMiddleware {
    #[instrument_trace]
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[response_header(DATE => gmt())]
    #[response_header(SERVER => HYPERLANE)]
    #[response_header(CONNECTION => KEEP_ALIVE)]
    #[response_header(TRACE => uuid::Uuid::new_v4().to_string())]
    #[epilogue_macros(response_header(CONTENT_TYPE => content_type))]
    #[instrument_trace]
    async fn handle(self, _stream: &mut Stream, ctx: &mut Context) -> Status {
        let content_type: String = ContentType::format_content_type_with_charset(TEXT_HTML, UTF8);
        Status::Continue
    }
}
impl ServerHook for ResponseStatusCodeMiddleware {
    #[instrument_trace]
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[response_status_code(200)]
    #[instrument_trace]
    async fn handle(self, _stream: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
impl ServerHook for OptionMethodMiddleware {
    #[instrument_trace]
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        filter(ctx.get_request().get_method().is_options()),
        send
    )]
    #[instrument_trace]
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        Status::Reject
    }
}
impl ServerHook for UpgradeMiddleware {
    #[instrument_trace]
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        is_ws_upgrade_type,
        response_version(HttpVersion::Http1_1),
        response_status_code(101),
        response_body(&vec![]),
        response_header(UPGRADE => WEBSOCKET),
        response_header(CONNECTION => UPGRADE),
        response_header(SEC_WEBSOCKET_ACCEPT => WebSocketFrame::generate_accept_key(ctx.get_request().get_header_back(SEC_WEBSOCKET_KEY))),
        send
    )]
    #[instrument_trace]
    async fn handle(self, stream: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
```
# Path: hyperlane-quick-start/application/middleware/request/mod.rs
```rust
mod r#impl;
mod r#struct;
pub use r#struct::*;
use super::*;
```
# Path: hyperlane-quick-start/application/view/mod.rs
```rust
mod favicon;
use super::*;
```
# Path: hyperlane-quick-start/application/view/favicon/struct.rs
```rust
use super::*;
#[route("/favicon.ico")]
#[derive(Clone, Copy, Data, Debug, Default)]
pub struct FaviconRoute;
```
# Path: hyperlane-quick-start/application/view/favicon/impl.rs
```rust
use super::*;
impl ServerHook for FaviconRoute {
    #[instrument_trace]
    async fn new(_: &mut Stream, _: &mut Context) -> Self {
        Self
    }
    #[prologue_macros(
        is_get_method,
        response_status_code(302),
        response_header(LOCATION => LOGO_IMG_URL)
    )]
    #[instrument_trace]
    async fn handle(self, _stream: &mut Stream, ctx: &mut Context) -> Status {
        Status::Continue
    }
}
```
# Path: hyperlane-quick-start/application/view/favicon/mod.rs
```rust
mod r#impl;
mod r#struct;
pub use r#struct::*;
use super::*;
use hyperlane_config::application::logo_img::*;
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
# Path: hyperlane-quick-start/application/model/response/common/enum.rs
```rust
use super::*;
#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize, ToSchema)]
pub enum ApiResponseStatus {
    Success,
    InvalidRequest,
    Unauthorized,
    Forbidden,
    ResourceNotFound,
    DatabaseError,
    BusinessLogicError,
    InternalServerError,
    ExternalServiceError,
    RateLimitExceeded,
    RequestTimeout,
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
    #[set(type(AsRef<str>))]
    pub(super) message: String,
    pub(super) data: Option<T>,
    #[get(type(copy))]
    pub(super) timestamp: Option<i64>,
}
```
# Path: hyperlane-quick-start/application/model/response/common/impl.rs
```rust
use super::*;
impl From<ApiResponseStatus> for i32 {
    fn from(status: ApiResponseStatus) -> Self {
        match status {
            ApiResponseStatus::Success => 200,
            ApiResponseStatus::InvalidRequest => 400,
            ApiResponseStatus::Unauthorized => 401,
            ApiResponseStatus::Forbidden => 403,
            ApiResponseStatus::ResourceNotFound => 404,
            ApiResponseStatus::DatabaseError => 500,
            ApiResponseStatus::BusinessLogicError => 500,
            ApiResponseStatus::InternalServerError => 500,
            ApiResponseStatus::ExternalServiceError => 502,
            ApiResponseStatus::RateLimitExceeded => 429,
            ApiResponseStatus::RequestTimeout => 408,
        }
    }
}
impl Display for ApiResponseStatus {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        let message: &str = match self {
            Self::Success => "Success",
            Self::InvalidRequest => "Invalid request",
            Self::Unauthorized => "Unauthorized",
            Self::Forbidden => "Forbidden",
            Self::ResourceNotFound => "Resource not found",
            Self::DatabaseError => "Database error",
            Self::BusinessLogicError => "Business logic error",
            Self::InternalServerError => "Internal server error",
            Self::ExternalServiceError => "External service error",
            Self::RateLimitExceeded => "Rate limit exceeded",
            Self::RequestTimeout => "Request timeout",
        };
        write!(f, "{}", message)
    }
}
impl<T> ApiResponse<T>
where
    T: Clone + Default + Serialize,
{
    #[instrument_trace]
    pub fn new(status: ApiResponseStatus, data: T) -> Self {
        let mut instance: ApiResponse<T> = Self::default();
        instance
            .set_code(status.into())
            .set_message(status.to_string())
            .set_data(Some(data))
            .set_timestamp(Some(Utc::now().timestamp_millis()));
        instance
    }
    #[instrument_trace]
    pub fn try_to_json_string(&self) -> serde_json::Result<String> {
        serde_json::to_string(self)
    }
    #[instrument_trace]
    pub fn to_json_string(&self) -> String {
        self.try_to_json_string().unwrap_or_default()
    }
    #[instrument_trace]
    pub fn try_to_json_bytes(&self) -> serde_json::Result<Vec<u8>> {
        serde_json::to_vec(self)
    }
    #[instrument_trace]
    pub fn to_json_bytes(&self) -> Vec<u8> {
        self.try_to_json_bytes().unwrap_or_default()
    }
}
```
# Path: hyperlane-quick-start/application/model/response/common/mod.rs
```rust
mod r#enum;
mod r#impl;
mod r#struct;
pub use {r#enum::*, r#struct::*};
use super::*;
use std::fmt::{self, Display, Formatter};
```
# Path: hyperlane-quick-start/plugin/lib.rs
```rust
#![recursion_limit = "1024"]
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
# Path: hyperlane-quick-start/plugin/README.md
## hyperlane-plugin
> A powerful and extensible plugin system for the hyperlane framework, providing modularity and customization capabilities.
## Api Docs
- [Api Docs](https://docs.rs/hyperlane/latest/)
## Contact
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
# Path: hyperlane-quick-start/plugin/mysql/const.rs
```rust
pub const DEFAULT_MYSQL_INSTANCE_NAME: &str = "mysql_default";
```
# Path: hyperlane-quick-start/plugin/mysql/static.rs
```rust
use super::*;
pub static MYSQL_CONNECTIONS: OnceLock<
    RwLock<HashMap<String, ConnectionCache<DatabaseConnection>>>,
> = OnceLock::new();
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
# Path: hyperlane-quick-start/plugin/database/const.rs
```rust
pub const MYSQL_DISPLAY_NAME: &str = "MySQL";
pub const POSTGRESQL_DISPLAY_NAME: &str = "PostgreSQL";
pub const REDIS_DISPLAY_NAME: &str = "Redis";
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
# Path: hyperlane-quick-start/plugin/postgresql/const.rs
```rust
pub const DEFAULT_POSTGRESQL_INSTANCE_NAME: &str = "postgres_default";
```
# Path: hyperlane-quick-start/plugin/postgresql/static.rs
```rust
use super::*;
pub static POSTGRESQL_CONNECTIONS: OnceLock<
    RwLock<HashMap<String, ConnectionCache<DatabaseConnection>>>,
> = OnceLock::new();
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
# Path: hyperlane-quick-start/plugin/process/struct.rs
```rust
use super::*;
#[derive(Clone, Copy, Data, Debug, Default)]
pub struct ProcessPlugin;
```
# Path: hyperlane-quick-start/plugin/process/const.rs
```rust
pub const CMD_STOP: &str = "stop";
pub const CMD_RESTART: &str = "restart";
pub const DAEMON_FLAG: &str = "-d";
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
# Path: hyperlane-quick-start/plugin/process/mod.rs
```rust
mod r#const;
mod r#impl;
mod r#struct;
pub use r#struct::*;
use {super::*, r#const::*};
use std::{env::args, future::Future};
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
# Path: hyperlane-quick-start/plugin/env/static.rs
```rust
use super::*;
pub static GLOBAL_ENV_CONFIG: OnceLock<EnvConfig> = OnceLock::new();
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
            .map_err(|_: EnvConfig| {
                "Failed to initialize global environment configuration".to_string()
            })?;
        Ok(())
    }
}
impl MySqlInstanceConfig {
    #[instrument_trace]
    pub(crate) fn load() -> Result<Self, String> {
        dotenvy::from_path(SERVER_ENV_FILE_PATH)
            .map_err(|error: dotenvy::Error| format!("Failed to load env file {error}"))?;
        let get_env_required = |key: &str| -> Result<String, String> {
            var(key).map_err(|_: VarError| format!("Environment variable {key} is not set"))
        };
        let get_env_u16 = |key: &str| -> Result<u16, String> {
            var(key)
                .map_err(|_: VarError| format!("Environment variable {key} is not set"))?
                .parse::<u16>()
                .map_err(|_: ParseIntError| {
                    format!("Environment variable {key} must be a valid u16")
                })
        };
        let get_env_u32 = |key: &str| -> Result<u32, String> {
            var(key)
                .map_err(|_: VarError| format!("Environment variable {key} is not set"))?
                .parse::<u32>()
                .map_err(|_: ParseIntError| {
                    format!("Environment variable {key} must be a valid u32")
                })
        };
        let get_env_u64 = |key: &str| -> Result<u64, String> {
            var(key)
                .map_err(|_: VarError| format!("Environment variable {key} is not set"))?
                .parse::<u64>()
                .map_err(|_: ParseIntError| {
                    format!("Environment variable {key} must be a valid u64")
                })
        };
        let get_env_usize = |key: &str| -> Result<usize, String> {
            var(key)
                .map_err(|_: VarError| format!("Environment variable {key} is not set"))?
                .parse::<usize>()
                .map_err(|_: ParseIntError| {
                    format!("Environment variable {key} must be a valid usize")
                })
        };
        let get_env_bool = |key: &str| -> Result<bool, String> {
            let value: String =
                var(key).map_err(|_: VarError| format!("Environment variable {key} is not set"))?;
            if value.eq_ignore_ascii_case("true") || value.eq_ignore_ascii_case("1") {
                Ok(true)
            } else if value.eq_ignore_ascii_case("false") || value.eq_ignore_ascii_case("0") {
                Ok(false)
            } else {
                Err(format!(
                    "Environment variable {key} must be true/false or 1/0"
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
        let mut instances: Vec<MySqlInstanceConfig> = serde_json::from_str(
            var(ENV_KEY_MYSQL)
                .map_err(|_: VarError| format!("Environment variable {ENV_KEY_MYSQL} is not set"))?
                .trim_matches('\''),
        )
        .map_err(|error: serde_json::Error| format!("Failed to parse {ENV_KEY_MYSQL}: {error}"))?;
        instances
            .iter_mut()
            .for_each(|instance: &mut MySqlInstanceConfig| {
                if instance.get_port() == 0 {
                    instance.set_port(docker_config.get_mysql_port().unwrap_or(3306));
                }
            });
        Ok(instances)
    }
    fn parse_postgresql_instances(
        docker_config: &DockerComposeConfig,
    ) -> Result<Vec<PostgreSqlInstanceConfig>, String> {
        let mut instances: Vec<PostgreSqlInstanceConfig> = serde_json::from_str(
            var(ENV_KEY_POSTGRESQL)
                .map_err(|_: VarError| {
                    format!("Environment variable {ENV_KEY_POSTGRESQL} is not set")
                })?
                .trim_matches('\''),
        )
        .map_err(|error: serde_json::Error| {
            format!("Failed to parse {ENV_KEY_POSTGRESQL}: {error}")
        })?;
        instances
            .iter_mut()
            .for_each(|instance: &mut PostgreSqlInstanceConfig| {
                if instance.get_port() == 0 {
                    instance.set_port(docker_config.get_postgresql_port().unwrap_or(5432));
                }
            });
        Ok(instances)
    }
    fn parse_redis_instances(
        docker_config: &DockerComposeConfig,
    ) -> Result<Vec<RedisInstanceConfig>, String> {
        let mut instances: Vec<RedisInstanceConfig> = serde_json::from_str(
            var(ENV_KEY_REDIS)
                .map_err(|_: VarError| format!("Environment variable {ENV_KEY_REDIS} is not set"))?
                .trim_matches('\''),
        )
        .map_err(|error: serde_json::Error| format!("Failed to parse {ENV_KEY_REDIS}: {error}"))?;
        instances
            .iter_mut()
            .for_each(|instance: &mut RedisInstanceConfig| {
                if instance.get_port() == 0 {
                    instance.set_port(docker_config.get_redis_port().unwrap_or(6379));
                }
            });
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
            .and_then(|services: &serde_yaml::Value| services.get(DOCKER_SERVICE_MYSQL))
        {
            if let Some(env) = mysql.get(DOCKER_YAML_ENVIRONMENT) {
                if let Some(database) = env
                    .get(DOCKER_MYSQL_DATABASE)
                    .and_then(|value: &serde_yaml::Value| value.as_str())
                    .map(String::from)
                {
                    config.set_mysql_database(Some(database));
                }
                if let Some(username) = env
                    .get(DOCKER_MYSQL_USER)
                    .and_then(|value: &serde_yaml::Value| value.as_str())
                    .map(String::from)
                {
                    config.set_mysql_username(Some(username));
                }
                if let Some(password) = env
                    .get(DOCKER_MYSQL_PASSWORD)
                    .and_then(|value: &serde_yaml::Value| value.as_str())
                    .map(String::from)
                {
                    config.set_mysql_password(Some(password));
                }
            }
            if let Some(ports) = mysql
                .get(DOCKER_YAML_PORTS)
                .and_then(|ports_value: &serde_yaml::Value| ports_value.as_sequence())
                && let Some(port_mapping) = ports
                    .first()
                    .and_then(|port: &serde_yaml::Value| port.as_str())
                && let Some(host_port) = port_mapping.split(COLON).next()
                && let Ok(port) = host_port.parse()
            {
                config.set_mysql_port(Some(port));
            }
        }
        if let Some(postgresql) = yaml
            .get(DOCKER_YAML_SERVICES)
            .and_then(|services: &serde_yaml::Value| services.get(DOCKER_SERVICE_POSTGRESQL))
        {
            if let Some(env) = postgresql.get(DOCKER_YAML_ENVIRONMENT) {
                if let Some(database) = env
                    .get(DOCKER_POSTGRES_DB)
                    .and_then(|value: &serde_yaml::Value| value.as_str())
                    .map(String::from)
                {
                    config.set_postgresql_database(Some(database));
                }
                if let Some(username) = env
                    .get(DOCKER_POSTGRES_USER)
                    .and_then(|value: &serde_yaml::Value| value.as_str())
                    .map(String::from)
                {
                    config.set_postgresql_username(Some(username));
                }
                if let Some(password) = env
                    .get(DOCKER_POSTGRES_PASSWORD)
                    .and_then(|value: &serde_yaml::Value| value.as_str())
                    .map(String::from)
                {
                    config.set_postgresql_password(Some(password));
                }
            }
            if let Some(ports) = postgresql
                .get(DOCKER_YAML_PORTS)
                .and_then(|ports_value: &serde_yaml::Value| ports_value.as_sequence())
                && let Some(port_mapping) = ports
                    .first()
                    .and_then(|port: &serde_yaml::Value| port.as_str())
                && let Some(host_port) = port_mapping.split(COLON).next()
                && let Ok(port) = host_port.parse()
            {
                config.set_postgresql_port(Some(port));
            }
        }
        if let Some(redis) = yaml
            .get(DOCKER_YAML_SERVICES)
            .and_then(|services: &serde_yaml::Value| services.get(DOCKER_SERVICE_REDIS))
        {
            if let Some(command) = redis
                .get(DOCKER_YAML_COMMAND)
                .and_then(|command_value: &serde_yaml::Value| command_value.as_str())
                && let Some(password_part) = command.split(DOCKER_REDIS_PASSWORD_FLAG).nth(1)
            {
                config.set_redis_password(Some(password_part.trim().to_string()));
            }
            if let Some(ports) = redis
                .get(DOCKER_YAML_PORTS)
                .and_then(|ports_value: &serde_yaml::Value| ports_value.as_sequence())
                && let Some(port_mapping) = ports
                    .first()
                    .and_then(|port: &serde_yaml::Value| port.as_str())
                && let Some(host_port) = port_mapping.split(COLON).next()
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
# Path: hyperlane-quick-start/plugin/env/mod.rs
```rust
mod r#const;
mod r#impl;
mod r#static;
mod r#struct;
pub use {r#const::*, r#struct::*};
use {super::*, r#static::*};
use hyperlane_resources::{docker::*, env::*};
use std::{
    env::{VarError, var},
    num::ParseIntError,
    sync::OnceLock,
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
# Path: hyperlane-quick-start/plugin/shutdown/mod.rs
```rust
mod r#impl;
mod r#static;
mod r#struct;
pub use r#struct::*;
use {super::*, r#static::*};
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
# Path: hyperlane-quick-start/plugin/redis/const.rs
```rust
pub const DEFAULT_REDIS_INSTANCE_NAME: &str = "redis_default";
```
# Path: hyperlane-quick-start/plugin/redis/static.rs
```rust
use super::*;
pub static REDIS_CONNECTIONS: OnceLock<RwLock<RedisConnectionMap>> = OnceLock::new();
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
