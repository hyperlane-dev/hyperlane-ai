## 🔍 File Content Details

### 📄 File #1 - `.gitignore`
- **Path**: `hyperlane\.gitignore`
- **Size**: `30 B`
- **Modified Time**: `2025-09-15T22:37:10.290504`

#### Content Preview



### 📄 File #2 - `Cargo.toml`
- **Path**: `hyperlane\Cargo.toml`
- **Size**: `1,333 B`
- **Modified Time**: `2025-10-01T21:58:27.401735`

#### Content Preview



### 📄 File #3 - `LICENSE`
- **Path**: `hyperlane\LICENSE`
- **Size**: `1,066 B`
- **Modified Time**: `2025-09-15T22:37:10.290504`

#### Content Preview



### 📄 File #4 - `README.md`
- **Path**: `hyperlane\README.md`
- **Size**: `6,530 B`
- **Modified Time**: `2025-09-15T22:37:10.290504`

#### Content Preview

```markdown
<center>

## hyperlane

<img src="https://docs.ltpp.vip/img/hyperlane.png" alt="" height="160">

[![](https://img.shields.io/crates/v/hyperlane.svg)](https://crates.io/crates/hyperlane)
[![](https://img.shields.io/crates/d/hyperlane.svg)](https://img.shields.io/crates/d/hyperlane.svg)
[![](https://docs.rs/hyperlane/badge.svg)](https://docs.rs/hyperlane)
[![](https://github.com/hyperlane-dev/hyperlane/workflows/Rust/badge.svg)](https://github.com/hyperlane-dev/hyperlane/actions?query=workflow:Rust)
[![](https://img.shields.io/crates/l/hyperlane.svg)](./LICENSE)

</center>

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

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Contact

For any inquiries, please reach out to the author at [root@ltpp.vip](mailto:root@ltpp.vip).

```

### 📄 File #5 - `config`
- **Path**: `hyperlane\.git\config`
- **Size**: `319 B`
- **Modified Time**: `2025-09-15T22:37:10.281501`

#### Content Preview



### 📄 File #6 - `description`
- **Path**: `hyperlane\.git\description`
- **Size**: `73 B`
- **Modified Time**: `2025-09-15T22:37:07.094785`

#### Content Preview



### 📄 File #7 - `FETCH_HEAD`
- **Path**: `hyperlane\.git\FETCH_HEAD`
- **Size**: `218 B`
- **Modified Time**: `2025-10-01T21:58:27.346993`

#### Content Preview



### 📄 File #8 - `HEAD`
- **Path**: `hyperlane\.git\HEAD`
- **Size**: `23 B`
- **Modified Time**: `2025-09-15T22:37:10.274784`

#### Content Preview



### 📄 File #9 - `index`
- **Path**: `hyperlane\.git\index`
- **Size**: `5,106 B`
- **Modified Time**: `2025-10-01T21:58:27.401735`

#### Content Preview



### 📄 File #10 - `ORIG_HEAD`
- **Path**: `hyperlane\.git\ORIG_HEAD`
- **Size**: `41 B`
- **Modified Time**: `2025-09-15T22:44:07.075363`

#### Content Preview



### 📄 File #11 - `packed-refs`
- **Path**: `hyperlane\.git\packed-refs`
- **Size**: `114 B`
- **Modified Time**: `2025-09-15T22:37:10.262589`

#### Content Preview



### 📄 File #12 - `shallow`
- **Path**: `hyperlane\.git\shallow`
- **Size**: `41 B`
- **Modified Time**: `2025-09-15T22:37:10.142773`

#### Content Preview



### 📄 File #13 - `applypatch-msg.sample`
- **Path**: `hyperlane\.git\hooks\applypatch-msg.sample`
- **Size**: `478 B`
- **Modified Time**: `2025-09-15T22:37:07.095785`

#### Content Preview



### 📄 File #14 - `commit-msg.sample`
- **Path**: `hyperlane\.git\hooks\commit-msg.sample`
- **Size**: `896 B`
- **Modified Time**: `2025-09-15T22:37:07.095785`

#### Content Preview



### 📄 File #15 - `fsmonitor-watchman.sample`
- **Path**: `hyperlane\.git\hooks\fsmonitor-watchman.sample`
- **Size**: `4,726 B`
- **Modified Time**: `2025-09-15T22:37:07.095785`

#### Content Preview



### 📄 File #16 - `post-update.sample`
- **Path**: `hyperlane\.git\hooks\post-update.sample`
- **Size**: `189 B`
- **Modified Time**: `2025-09-15T22:37:07.095785`

#### Content Preview



### 📄 File #17 - `pre-applypatch.sample`
- **Path**: `hyperlane\.git\hooks\pre-applypatch.sample`
- **Size**: `424 B`
- **Modified Time**: `2025-09-15T22:37:07.095785`

#### Content Preview



### 📄 File #18 - `pre-commit.sample`
- **Path**: `hyperlane\.git\hooks\pre-commit.sample`
- **Size**: `1,649 B`
- **Modified Time**: `2025-09-15T22:37:07.096785`

#### Content Preview



### 📄 File #19 - `pre-merge-commit.sample`
- **Path**: `hyperlane\.git\hooks\pre-merge-commit.sample`
- **Size**: `416 B`
- **Modified Time**: `2025-09-15T22:37:07.096785`

#### Content Preview



### 📄 File #20 - `pre-push.sample`
- **Path**: `hyperlane\.git\hooks\pre-push.sample`
- **Size**: `1,374 B`
- **Modified Time**: `2025-09-15T22:37:07.096785`

#### Content Preview



### 📄 File #21 - `pre-rebase.sample`
- **Path**: `hyperlane\.git\hooks\pre-rebase.sample`
- **Size**: `4,898 B`
- **Modified Time**: `2025-09-15T22:37:07.096785`

#### Content Preview



### 📄 File #22 - `pre-receive.sample`
- **Path**: `hyperlane\.git\hooks\pre-receive.sample`
- **Size**: `544 B`
- **Modified Time**: `2025-09-15T22:37:07.097785`

#### Content Preview



### 📄 File #23 - `prepare-commit-msg.sample`
- **Path**: `hyperlane\.git\hooks\prepare-commit-msg.sample`
- **Size**: `1,492 B`
- **Modified Time**: `2025-09-15T22:37:07.097785`

#### Content Preview



### 📄 File #24 - `push-to-checkout.sample`
- **Path**: `hyperlane\.git\hooks\push-to-checkout.sample`
- **Size**: `2,783 B`
- **Modified Time**: `2025-09-15T22:37:07.097785`

#### Content Preview



### 📄 File #25 - `sendemail-validate.sample`
- **Path**: `hyperlane\.git\hooks\sendemail-validate.sample`
- **Size**: `2,308 B`
- **Modified Time**: `2025-09-15T22:37:07.097785`

#### Content Preview



### 📄 File #26 - `update.sample`
- **Path**: `hyperlane\.git\hooks\update.sample`
- **Size**: `3,650 B`
- **Modified Time**: `2025-09-15T22:37:07.097785`

#### Content Preview



### 📄 File #27 - `exclude`
- **Path**: `hyperlane\.git\info\exclude`
- **Size**: `240 B`
- **Modified Time**: `2025-09-15T22:37:07.098784`

#### Content Preview



### 📄 File #28 - `HEAD`
- **Path**: `hyperlane\.git\logs\HEAD`
- **Size**: `337 B`
- **Modified Time**: `2025-10-01T21:58:27.410736`

#### Content Preview



### 📄 File #29 - `master`
- **Path**: `hyperlane\.git\logs\refs\heads\master`
- **Size**: `337 B`
- **Modified Time**: `2025-10-01T21:58:27.411232`

#### Content Preview



### 📄 File #30 - `HEAD`
- **Path**: `hyperlane\.git\logs\refs\remotes\origin\HEAD`
- **Size**: `184 B`
- **Modified Time**: `2025-09-15T22:37:10.273785`

#### Content Preview



### 📄 File #31 - `master`
- **Path**: `hyperlane\.git\logs\refs\remotes\origin\master`
- **Size**: `153 B`
- **Modified Time**: `2025-10-01T21:58:27.338365`

#### Content Preview



### 📄 File #32 - `90ea77382c07c3064fae70d95b16d2d82d5f4d`
- **Path**: `hyperlane\.git\objects\0c\90ea77382c07c3064fae70d95b16d2d82d5f4d`
- **Size**: `211 B`
- **Modified Time**: `2025-10-01T21:58:27.286167`

#### Content Preview



### 📄 File #33 - `39fcaeed20f85d156f59154fe85c083ff917f9`
- **Path**: `hyperlane\.git\objects\15\39fcaeed20f85d156f59154fe85c083ff917f9`
- **Size**: `5,979 B`
- **Modified Time**: `2025-10-01T21:58:27.286167`

#### Content Preview



### 📄 File #34 - `cf033a6790633ef10ca1beb62018531330f301`
- **Path**: `hyperlane\.git\objects\1b\cf033a6790633ef10ca1beb62018531330f301`
- **Size**: `164 B`
- **Modified Time**: `2025-10-01T21:58:27.286167`

#### Content Preview



### 📄 File #35 - `538c81f4ab791da627eda05b604c16d8054649`
- **Path**: `hyperlane\.git\objects\80\538c81f4ab791da627eda05b604c16d8054649`
- **Size**: `352 B`
- **Modified Time**: `2025-10-01T21:58:27.286167`

#### Content Preview



### 📄 File #36 - `d9a914ec18f56fb17565bf74bd99051effad72`
- **Path**: `hyperlane\.git\objects\ea\d9a914ec18f56fb17565bf74bd99051effad72`
- **Size**: `141 B`
- **Modified Time**: `2025-10-01T21:58:27.286167`

#### Content Preview



### 📄 File #37 - `038e7d43c78923ca8b12ba982c310f60f9290c`
- **Path**: `hyperlane\.git\objects\ec\038e7d43c78923ca8b12ba982c310f60f9290c`
- **Size**: `758 B`
- **Modified Time**: `2025-10-01T21:58:27.286167`

#### Content Preview



### 📄 File #38 - `pack-9981d3ebc5423107c7b99ac7ce88ac2573ef186f.idx`
- **Path**: `hyperlane\.git\objects\pack\pack-9981d3ebc5423107c7b99ac7ce88ac2573ef186f.idx`
- **Size**: `2,976 B`
- **Modified Time**: `2025-09-15T22:37:10.228009`

#### Content Preview



### 📄 File #39 - `pack-9981d3ebc5423107c7b99ac7ce88ac2573ef186f.pack`
- **Path**: `hyperlane\.git\objects\pack\pack-9981d3ebc5423107c7b99ac7ce88ac2573ef186f.pack`
- **Size**: `44,622 B`
- **Modified Time**: `2025-09-15T22:37:10.228009`

#### Content Preview



### 📄 File #40 - `pack-9981d3ebc5423107c7b99ac7ce88ac2573ef186f.rev`
- **Path**: `hyperlane\.git\objects\pack\pack-9981d3ebc5423107c7b99ac7ce88ac2573ef186f.rev`
- **Size**: `324 B`
- **Modified Time**: `2025-09-15T22:37:10.229008`

#### Content Preview



### 📄 File #41 - `master`
- **Path**: `hyperlane\.git\refs\heads\master`
- **Size**: `41 B`
- **Modified Time**: `2025-10-01T21:58:27.401735`

#### Content Preview



### 📄 File #42 - `HEAD`
- **Path**: `hyperlane\.git\refs\remotes\origin\HEAD`
- **Size**: `32 B`
- **Modified Time**: `2025-09-15T22:37:10.272785`

#### Content Preview



### 📄 File #43 - `master`
- **Path**: `hyperlane\.git\refs\remotes\origin\master`
- **Size**: `41 B`
- **Modified Time**: `2025-10-01T21:58:27.338365`

#### Content Preview



### 📄 File #44 - `v9.4.4`
- **Path**: `hyperlane\.git\refs\tags\v9.4.4`
- **Size**: `41 B`
- **Modified Time**: `2025-09-15T22:37:10.271784`

#### Content Preview



### 📄 File #45 - `v9.4.5`
- **Path**: `hyperlane\.git\refs\tags\v9.4.5`
- **Size**: `41 B`
- **Modified Time**: `2025-10-01T21:58:27.338365`

#### Content Preview



### 📄 File #46 - `rust.yml`
- **Path**: `hyperlane\.github\workflows\rust.yml`
- **Size**: `9,636 B`
- **Modified Time**: `2025-09-15T22:37:10.289504`

#### Content Preview

```yaml
name: Rust
on:
  push:
    branches: [master]
env:
  CARGO_TERM_COLOR: always
jobs:
  setup:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.read.outputs.version }}
      tag: ${{ steps.read.outputs.tag }}
      package_name: ${{ steps.read.outputs.package_name }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Install rust-toolchain
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
          components: rustfmt, clippy
      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: |
            ~/.cargo/registry
            ~/.cargo/git
            target
          key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}
      - name: Install toml-cli
        run: cargo install toml-cli
      - name: Cache toml-cli
        uses: actions/cache@v3
        with:
          path: ~/.cargo/bin/toml
          key: toml-cli-${{ runner.os }}
      - name: Read cargo metadata
        id: read
        run: |
          VERSION=$(toml get Cargo.toml package.version --raw)
          PACKAGE_NAME=$(toml get Cargo.toml package.name --raw)
          echo "📦 Detected package: $PACKAGE_NAME v$VERSION"
          if [ -z "$VERSION" ] || [ -z "$PACKAGE_NAME" ]; then
            echo "❌ Failed to read package info from Cargo.toml"
          fi
          echo "version=$VERSION" >> $GITHUB_OUTPUT
          echo "tag=v$VERSION" >> $GITHUB_OUTPUT
          echo "package_name=$PACKAGE_NAME" >> $GITHUB_OUTPUT

  check:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup rust
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
          components: rustfmt
      - name: Format check
        run: cargo fmt -- --check

  tests:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Prepare environment
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
      - name: Run tests
        run: cargo test --all-features -- --nocapture

  clippy:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Load clippy
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
          components: clippy
      - name: Run clippy
        run: cargo clippy --all-features -- -A warnings

  build:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup build
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
      - name: Build release
        run: cargo check --release --all-features

  publish:
    needs: [setup, check, tests, clippy, build]
    if: needs.setup.outputs.tag != ''
    runs-on: ubuntu-latest
    outputs:
      published: ${{ steps.publish.outputs.published }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Restore toml-cli
        uses: actions/cache@v3
        with:
          path: ~/.cargo/bin/toml
          key: toml-cli-${{ runner.os }}
      - name: Publish to crates.io
        id: publish
        env:
          CARGO_REGISTRY_TOKEN: ${{ secrets.CARGO_REGISTRY_TOKEN }}
        run: |
          set -e
          echo "published=false" >> $GITHUB_OUTPUT
          echo "${{ secrets.CARGO_REGISTRY_TOKEN }}" | cargo login
          PACKAGE_NAME=$(toml get Cargo.toml package.name --raw)
          VERSION=${{ needs.setup.outputs.version }}
          if cargo publish --allow-dirty; then
            echo "published=true" >> $GITHUB_OUTPUT
            echo "🎉🎉🎉 PUBLISH SUCCESSFUL 🎉🎉🎉"
            echo "✅ Successfully published $PACKAGE_NAME v$VERSION to crates.io"
            echo "📦 Crates.io: [https://crates.io/crates/$PACKAGE_NAME/$VERSION](https://crates.io/crates/$PACKAGE_NAME/$VERSION)"
            echo "📚 Docs.rs: [https://docs.rs/$PACKAGE_NAME/$VERSION](https://docs.rs/$PACKAGE_NAME/$VERSION)"
          else
            echo "❌ Publish failed"
          fi

  release:
    needs: [setup, check, tests, clippy, build]
    permissions:
      contents: write
      packages: write
    if: needs.setup.outputs.tag != ''
    runs-on: ubuntu-latest
    outputs:
      released: ${{ steps.release.outputs.released }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Get package name
        id: package_info
        run: |
          echo "package_name=${{ needs.setup.outputs.package_name }}" >> $GITHUB_OUTPUT
      - name: Check tag status
        id: check_tag
        run: |
          if git tag -l | grep -q "^${{ needs.setup.outputs.tag }}$"; then
            echo "tag_exists=true" >> $GITHUB_OUTPUT
            echo "🏷️ Tag ${{ needs.setup.outputs.tag }} exists locally"
          else
            echo "tag_exists=false" >> $GITHUB_OUTPUT
            echo "🏷️ Tag ${{ needs.setup.outputs.tag }} does not exist locally"
          fi
          if git ls-remote --tags origin | grep -q "refs/tags/${{ needs.setup.outputs.tag }}$"; then
            echo "remote_tag_exists=true" >> $GITHUB_OUTPUT
            echo "🌐 Tag ${{ needs.setup.outputs.tag }} exists on remote"
          else
            echo "remote_tag_exists=false" >> $GITHUB_OUTPUT
            echo "🌐 Tag ${{ needs.setup.outputs.tag }} does not exist on remote"
          fi
      - name: Check release status
        id: check_release
        run: |
          if gh release view "${{ needs.setup.outputs.tag }}" > /dev/null 2>&1; then
            echo "release_exists=true" >> $GITHUB_OUTPUT
            echo "📦 Release ${{ needs.setup.outputs.tag }} already exists"
          else
            echo "release_exists=false" >> $GITHUB_OUTPUT
            echo "📦 Release ${{ needs.setup.outputs.tag }} does not exist"
          fi
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - name: Create or update release
        id: release
        run: |
          set -e
          echo "released=false" >> $GITHUB_OUTPUT
          PACKAGE_NAME="${{ steps.package_info.outputs.package_name }}"
          VERSION="${{ needs.setup.outputs.version }}"
          TAG="${{ needs.setup.outputs.tag }}"
          echo "📦 Building source archives..."
          git archive --format=zip --prefix="${PACKAGE_NAME}-${VERSION}/" HEAD > "${PACKAGE_NAME}-${VERSION}.zip"
          git archive --format=tar.gz --prefix="${PACKAGE_NAME}-${VERSION}/" HEAD > "${PACKAGE_NAME}-${VERSION}.tar.gz"
          if [ "${{ steps.check_release.outputs.release_exists }}" = "true" ]; then
            echo "🔄 Updating existing release: $TAG"
            gh release view "$TAG" --json assets --jq '.assets[].name' | while read asset; do
              if [ -n "$asset" ]; then
                echo "🗑️ Deleting asset: $asset"
                gh release delete-asset "$TAG" "$asset" --yes || true
              fi
            done
            if gh release edit "$TAG" \
              --title "$TAG (Updated $(date '+%Y-%m-%d %H:%M:%S'))" \
              --notes "Release $TAG - Updated at $(date '+%Y-%m-%d %H:%M:%S UTC')
            ## Changes
            - Version: $VERSION
            - Package: $PACKAGE_NAME
            ## Links
            📦 [Crate on crates.io](https://crates.io/crates/$PACKAGE_NAME/$VERSION)
            📚 [Documentation on docs.rs](https://docs.rs/$PACKAGE_NAME/$VERSION)
            📋 [Commit History](https://github.com/${{ github.repository }}/commits/$TAG)" && \
               gh release upload "$TAG" "${PACKAGE_NAME}-${VERSION}.zip" "${PACKAGE_NAME}-${VERSION}.tar.gz" --clobber; then
              echo "released=true" >> $GITHUB_OUTPUT
              echo "✅ Updated release $TAG"
              echo "🔖 Tag: $TAG"
              echo "🚀 Release: [GitHub Release](${{ github.server_url }}/${{ github.repository }}/releases/tag/$TAG)"
            else
              echo "❌ Failed to update release"
            fi
          else
            if [ "${{ steps.check_tag.outputs.remote_tag_exists }}" = "false" ]; then
              echo "🏷️ Creating and pushing tag: $TAG"
              git tag "$TAG"
              git push origin "$TAG"
            fi
            echo "🆕 Creating new release: $TAG"
            if gh release create "$TAG" \
              --title "$TAG (Created $(date '+%Y-%m-%d %H:%M:%S'))" \
              --notes "Release $TAG - Created at $(date '+%Y-%m-%d %H:%M:%S UTC')
            ## Changes
            - Version: $VERSION
            - Package: $PACKAGE_NAME
            ## Links
            📦 [Crate on crates.io](https://crates.io/crates/$PACKAGE_NAME/$VERSION)
            📚 [Documentation on docs.rs](https://docs.rs/$PACKAGE_NAME/$VERSION)
            📋 [Commit History](https://github.com/${{ github.repository }}/commits/$TAG)" \
              --latest && \
               gh release upload "$TAG" "${PACKAGE_NAME}-${VERSION}.zip" "${PACKAGE_NAME}-${VERSION}.tar.gz"; then
              echo "released=true" >> $GITHUB_OUTPUT
              echo "✅ Created release $TAG"
              echo "🔖 Tag: $TAG"
              echo "🚀 Release: [GitHub Release](${{ github.server_url }}/${{ github.repository }}/releases/tag/$TAG)"
            else
              echo "❌ Failed to create release"
            fi
          fi
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

```

### 📄 File #47 - `lib.rs`
- **Path**: `hyperlane\src\lib.rs`
- **Size**: `1,435 B`
- **Modified Time**: `2025-09-15T22:37:10.294505`

#### Content Preview

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

pub(crate) use lifecycle::*;

pub(crate) use std::{
    any::Any,
    borrow::Borrow,
    cmp::Ordering,
    collections::{HashMap, HashSet},
    future::Future,
    net::SocketAddr,
    panic::Location,
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

```

### 📄 File #48 - `enum.rs`
- **Path**: `hyperlane\src\attribute\enum.rs`
- **Size**: `868 B`
- **Modified Time**: `2025-09-15T22:37:10.290504`

#### Content Preview

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
    /// The attribute key for send body hook.
    SendBodyHook,
    /// The attribute key for send hook.
    SendHook,
}

```

### 📄 File #49 - `impl.rs`
- **Path**: `hyperlane\src\attribute\impl.rs`
- **Size**: `1,228 B`
- **Modified Time**: `2025-09-15T22:37:10.291505`

#### Content Preview

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
    fn from(key: InternalAttribute) -> Self {
        Attribute::Internal(key)
    }
}

```

### 📄 File #50 - `mod.rs`
- **Path**: `hyperlane\src\attribute\mod.rs`
- **Size**: `116 B`
- **Modified Time**: `2025-09-15T22:37:10.291505`

#### Content Preview

```rust
pub(crate) mod r#enum;
pub(crate) mod r#impl;
pub(crate) mod r#type;

pub use r#type::*;

pub(crate) use r#enum::*;

```

### 📄 File #51 - `type.rs`
- **Path**: `hyperlane\src\attribute\type.rs`
- **Size**: `258 B`
- **Modified Time**: `2025-09-15T22:37:10.291505`

#### Content Preview

```rust
use crate::*;

/// A type alias for a HashMap storing string keys and thread-safe, shareable values.
///
/// This type is used for storing attributes that can be safely shared across threads.
pub type HashMapArcAnySendSync = HashMap<String, ArcAnySendSync>;

```

### 📄 File #52 - `impl.rs`
- **Path**: `hyperlane\src\config\impl.rs`
- **Size**: `6,766 B`
- **Modified Time**: `2025-09-15T22:37:10.291505`

#### Content Preview

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
    /// A `ServerConfigInner` instance with default settings.
    fn default() -> Self {
        Self {
            host: DEFAULT_HOST.to_owned(),
            port: DEFAULT_WEB_PORT,
            buffer: DEFAULT_BUFFER_SIZE,
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
    /// A `ServerConfig` instance with default settings.
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
    /// - `&Self`: The other `ServerConfig` to compare against.
    ///
    /// # Returns
    ///
    /// A `bool` indicating whether the configurations are equal.
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
    /// A new `ServerConfig` instance.
    pub async fn new() -> Self {
        Self::default()
    }

    /// Acquires a read lock on the server configuration.
    ///
    /// # Returns
    ///
    /// A `RwLockReadGuardServerConfigInner` for the inner configuration.
    async fn read(&self) -> RwLockReadGuardServerConfigInner {
        self.get_0().read().await
    }

    /// Acquires a write lock on the server configuration.
    ///
    /// # Returns
    ///
    /// A `RwLockWriteGuardServerConfigInner` for the inner configuration.
    async fn write(&self) -> RwLockWriteGuardServerConfigInner {
        self.get_0().write().await
    }

    /// Retrieves a clone of the inner server configuration.
    ///
    /// This function provides a snapshot of the current configuration by acquiring a read lock
    /// and cloning the inner `ServerConfigInner`.
    ///
    /// # Returns
    ///
    /// A `ServerConfigInner` instance containing the current server configuration.
    pub(crate) async fn get_inner(&self) -> ServerConfigInner {
        self.read().await.clone()
    }

    /// Sets the host address for the server.
    ///
    /// # Arguments
    ///
    /// - `H`: The host address to set.
    ///
    /// # Returns
    ///
    /// A reference to `Self` for method chaining.
    pub async fn host<H: ToString>(&self, host: H) -> &Self {
        self.write().await.set_host(host.to_string());
        self
    }

    /// Sets the port for the server.
    ///
    /// # Arguments
    ///
    /// - `usize`: The port number to set.
    ///
    /// # Returns
    ///
    /// A reference to `Self` for method chaining.
    pub async fn port(&self, port: usize) -> &Self {
        self.write().await.set_port(port);
        self
    }

    /// Sets the HTTP buffer size.
    ///
    /// # Arguments
    ///
    /// - `usize`: The HTTP buffer size to set.
    ///
    /// # Returns
    ///
    /// A reference to `Self` for method chaining.
    pub async fn buffer(&self, buffer: usize) -> &Self {
        self.write().await.set_buffer(buffer);
        self
    }

    /// Sets the `TCP_NODELAY` option.
    ///
    /// # Arguments
    ///
    /// - `bool`: The `bool` value for `TCP_NODELAY`.
    ///
    /// # Returns
    ///
    /// A reference to `Self` for method chaining.
    pub async fn nodelay(&self, nodelay: bool) -> &Self {
        self.write().await.set_nodelay(Some(nodelay));
        self
    }

    /// Enables the `TCP_NODELAY` option.
    ///
    /// # Returns
    ///
    /// A reference to `Self` for method chaining.
    pub async fn enable_nodelay(&self) -> &Self {
        self.nodelay(true).await
    }

    /// Disables the `TCP_NODELAY` option.
    ///
    /// # Returns
    ///
    /// A reference to `Self` for method chaining.
    pub async fn disable_nodelay(&self) -> &Self {
        self.nodelay(false).await
    }

    /// Sets the `SO_LINGER` option.
    ///
    /// # Arguments
    ///
    /// - `OptionDuration`: The `Duration` value for `SO_LINGER`.
    ///
    /// # Returns
    ///
    /// A reference to `Self` for method chaining.
    pub async fn linger(&self, linger_opt: OptionDuration) -> &Self {
        self.write().await.set_linger(linger_opt);
        self
    }

    /// Enables the `SO_LINGER` option.
    ///
    /// # Arguments
    ///
    /// - `Duration`: The `Duration` value for `SO_LINGER`.
    ///
    /// # Returns
    ///
    /// A reference to `Self` for method chaining.
    pub async fn enable_linger(&self, linger: Duration) -> &Self {
        self.linger(Some(linger)).await;
        self
    }

    /// Disables the `SO_LINGER` option.
    ///
    /// # Returns
    ///
    /// A reference to `Self` for method chaining.
    pub async fn disable_linger(&self) -> &Self {
        self.linger(None).await;
        self
    }

    /// Sets the `IP_TTL` option.
    ///
    /// # Arguments
    ///
    /// - `u32`: The `u32` value for `IP_TTL`.
    ///
    /// # Returns
    ///
    /// A reference to `Self` for method chaining.
    pub async fn ttl(&self, ttl: u32) -> &Self {
        self.write().await.set_ttl(Some(ttl));
        self
    }

    /// Creates a `ServerConfig` from a JSON string.
    ///
    /// # Arguments
    ///
    /// - `&str`: The JSON string to parse.
    ///
    /// # Returns
    ///
    /// A `ServerConfigResult` which is a `Result` containing either the `ServerConfig` or a `serde_json::Error`.
    pub fn from_str(config_str: &str) -> ServerConfigResult {
        serde_json::from_str(config_str).map(|config: ServerConfigInner| Self(arc_rwlock(config)))
    }
}

```

### 📄 File #53 - `mod.rs`
- **Path**: `hyperlane\src\config\mod.rs`
- **Size**: `112 B`
- **Modified Time**: `2025-09-15T22:37:10.291505`

#### Content Preview

```rust
pub(crate) mod r#impl;
pub(crate) mod r#struct;
pub(crate) mod r#type;

pub use r#struct::*;
pub use r#type::*;

```

### 📄 File #54 - `struct.rs`
- **Path**: `hyperlane\src\config\struct.rs`
- **Size**: `1,714 B`
- **Modified Time**: `2025-09-15T22:37:10.291505`

#### Content Preview

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
    pub(super) port: usize,
    /// The buffer size for HTTP connections.
    #[get(pub(crate))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    pub(super) buffer: usize,
    /// The `TCP_NODELAY` option for sockets.
    #[get(pub(crate))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    pub(super) nodelay: OptionBool,
    /// The `SO_LINGER` option for sockets.
    #[get(pub(crate))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    pub(super) linger: OptionDuration,
    /// The `IP_TTL` option for sockets.
    #[get(pub(crate))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    pub(super) ttl: OptionU32,
}

/// Represents the thread-safe, shareable server configuration.
///
/// This structure wraps `ServerConfigInner` in an `Arc<RwLock<ServerConfigInner>>`
/// to allow for safe concurrent access and modification of the server settings.
#[derive(Clone, Getter, CustomDebug, DisplayDebug)]
pub struct ServerConfig(#[get(pub(super))] pub(super) ArcRwLockServerConfigInner);

```

### 📄 File #55 - `type.rs`
- **Path**: `hyperlane\src\config\type.rs`
- **Size**: `736 B`
- **Modified Time**: `2025-09-15T22:37:10.292505`

#### Content Preview

```rust
use crate::*;

/// A type alias for a `Result<ServerConfig, serde_json::Error>`.
///
/// This is used for operations that can fail during `ServerConfig` deserialization.
pub type ServerConfigResult = Result<ServerConfig, serde_json::Error>;
/// A type alias for `RwLockReadGuard<'a, ServerConfigInner>`.
///
/// This provides read-only access to the `ServerConfigInner` wrapped in a `RwLock`.
pub(crate) type RwLockReadGuardServerConfigInner<'a> = RwLockReadGuard<'a, ServerConfigInner>;
/// A type alias for `RwLockWriteGuard<'a, ServerConfigInner>`.
///
/// This provides mutable access to the `ServerConfigInner` wrapped in a `RwLock`.
pub(crate) type RwLockWriteGuardServerConfigInner<'a> = RwLockWriteGuard<'a, ServerConfigInner>;

```

### 📄 File #56 - `impl.rs`
- **Path**: `hyperlane\src\context\impl.rs`
- **Size**: `50,212 B`
- **Modified Time**: `2025-09-15T22:37:10.292505`

#### Content Preview

```rust
use crate::*;

/// Implementation of methods for `Context` structure.
impl Context {
    /// Creates a new `Context` from an internal context instance.
    ///
    /// # Arguments
    ///
    /// - `ContextInner` - The wrapped context data.
    ///
    /// # Returns
    ///
    /// - `Context` - The newly created context instance.
    pub(crate) fn from_internal_context(ctx: ContextInner) -> Self {
        Self(arc_rwlock(ctx))
    }

    /// Creates a new `Context` for a given stream and request.
    ///
    /// # Arguments
    ///
    /// - `&ArcRwLockStream` - The network stream.
    /// - `&Request` - The HTTP request.
    ///
    /// # Returns
    ///
    /// - `Context` - The newly created context.
    pub(crate) fn create_context(stream: &ArcRwLockStream, request: &Request) -> Context {
        Context::from_internal_context({
            let mut internal_ctx: ContextInner = ContextInner::default();
            internal_ctx
                .set_stream(Some(stream.clone()))
                .set_request(request.clone());
            internal_ctx
        })
    }

    /// Acquires a read lock on the inner context data.
    ///
    /// # Returns
    ///
    /// - `RwLockReadContextInner` - The read guard for the inner context.
    async fn read(&self) -> RwLockReadContextInner {
        self.get_0().read().await
    }

    /// Acquires a write lock on the inner context data.
    ///
    /// # Returns
    ///
    /// - `RwLockWriteContextInner` - The write guard for the inner context.
    async fn write(&self) -> RwLockWriteContextInner {
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

    /// Checks if the connection has been terminated (aborted and closed).
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
    /// - `OptionArcRwLockStream` - The thread-safe, shareable network stream if it exists.
    pub async fn try_get_stream(&self) -> OptionArcRwLockStream {
        self.read().await.get_stream().clone()
    }

    /// Retrieves the remote socket address of the connection.
    ///
    /// # Returns
    ///
    /// - `OptionSocketAddr` - The socket address of the remote peer if available.
    pub async fn try_get_socket_addr(&self) -> OptionSocketAddr {
        let stream_result: OptionArcRwLockStream = self.try_get_stream().await;
        if stream_result.is_none() {
            return None;
        }
        stream_result.unwrap().read().await.peer_addr().ok()
    }

    /// Retrieves the remote socket address or a default value if unavailable.
    ///
    /// # Returns
    ///
    /// - `SocketAddr` - The socket address of the remote peer, or default if unavailable.
    pub async fn get_socket_addr(&self) -> SocketAddr {
        let stream_result: OptionArcRwLockStream = self.try_get_stream().await;
        if stream_result.is_none() {
            return DEFAULT_SOCKET_ADDR;
        }
        stream_result
            .unwrap()
            .read()
            .await
            .peer_addr()
            .unwrap_or(DEFAULT_SOCKET_ADDR)
    }

    /// Retrieves the remote socket address as a string.
    ///
    /// # Returns
    ///
    /// - `OptionString` - The string representation of the socket address if available.
    pub async fn try_get_socket_addr_string(&self) -> OptionString {
        self.try_get_socket_addr()
            .await
            .map(|data| data.to_string())
    }

    /// Retrieves the remote socket address as a string, or a default value if unavailable.
    ///
    /// # Returns
    ///
    /// - `String` - The string representation of the socket address, or default if unavailable.
    pub async fn get_socket_addr_string(&self) -> String {
        self.get_socket_addr().await.to_string()
    }

    /// Retrieves the IP address part of the remote socket address.
    ///
    /// # Returns
    ///
    /// - `OptionSocketHost` - The IP address of the remote peer if available.
    pub async fn try_get_socket_host(&self) -> OptionSocketHost {
        self.try_get_socket_addr()
            .await
            .map(|socket_addr: SocketAddr| socket_addr.ip())
    }

    /// Retrieves the port number part of the remote socket address.
    ///
    /// # Returns
    ///
    /// - `OptionSocketPort` - The port number of the remote peer if available.
    pub async fn try_get_socket_port(&self) -> OptionSocketPort {
        self.try_get_socket_addr()
            .await
            .map(|socket_addr: SocketAddr| socket_addr.port())
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

    /// Retrieves a specific query parameter by its key.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The query parameter key.
    ///
    /// # Returns
    ///
    /// - `OptionRequestQuerysValue` - The query parameter value if exists.
    pub async fn try_get_request_query<K>(&self, key: K) -> OptionRequestQuerysValue
    where
        K: AsRef<str>,
    {
        self.read().await.get_request().try_get_query(key)
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
    /// - `ResultJsonError<J>` - The deserialized type `J` or a JSON error.
    pub async fn get_request_body_json<J>(&self) -> ResultJsonError<J>
    where
        J: DeserializeOwned,
    {
        self.read().await.get_request().get_body_json()
    }

    /// Retrieves a specific request header by its key.
    ///
    /// Gets a request header by key.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The header key.
    ///
    /// # Returns
    ///
    /// - `OptionRequestHeadersValue` - The header values if exists.
    pub async fn try_get_request_header<K>(&self, key: K) -> OptionRequestHeadersValue
    where
        K: AsRef<str>,
    {
        self.read().await.get_request().try_get_header(key)
    }

    /// Retrieves all request headers.
    ///
    /// # Returns
    ///
    /// - `RequestHeaders` - A clone of the request's header map.
    pub async fn get_request_headers(&self) -> RequestHeaders {
        self.read().await.get_request().get_headers().clone()
    }

    /// Retrieves the first value of a specific request header.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The key of the header.
    ///
    /// # Returns
    ///
    /// - `OptionRequestHeadersValueItem` - The first value of the header if it exists.
    pub async fn try_get_request_header_front<K>(&self, key: K) -> OptionRequestHeadersValueItem
    where
        K: AsRef<str>,
    {
        self.read().await.get_request().try_get_header_front(key)
    }

    /// Retrieves the last value of a specific request header.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The key of the header.
    ///
    /// # Returns
    ///
    /// - `OptionRequestHeadersValueItem` - The last value of the header if it exists.
    pub async fn try_get_request_header_back<K>(&self, key: K) -> OptionRequestHeadersValueItem
    where
        K: AsRef<str>,
    {
        self.read().await.get_request().try_get_header_back(key)
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

    /// Retrieves the total number of request headers.
    ///
    /// # Returns
    ///
    /// - `usize` - The total number of headers in the request.
    pub async fn get_request_headers_length(&self) -> usize {
        self.read().await.get_request().get_headers_length()
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

    /// Retrieves a specific cookie by its name from the request.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The cookie name.
    ///
    /// # Returns
    ///
    /// - `OptionCookiesValue` - The cookie value if exists.
    pub async fn try_get_request_cookie<K>(&self, key: K) -> OptionCookiesValue
    where
        K: AsRef<str>,
    {
        self.get_request_cookies().await.get(key.as_ref()).cloned()
    }

    /// Retrieves the upgrade type of the request.
    ///
    /// # Returns
    ///
    /// - `UpgradeType` - Indicates if the request is for a WebSocket connection.
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

    /// Retrieves a specific response header by its key.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The key of the header to retrieve.
    ///
    /// # Returns
    ///
    /// - `OptionResponseHeadersValue` - The header values if the header exists.
    pub async fn try_get_response_header<K>(&self, key: K) -> OptionResponseHeadersValue
    where
        K: AsRef<str>,
    {
        self.read().await.get_response().try_get_header(key)
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

    /// Retrieves the first value of a specific response header.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The key of the header.
    ///
    /// # Returns
    ///
    /// - `OptionResponseHeadersValueItem` - The first value of the header if it exists.
    pub async fn try_get_response_header_front<K>(&self, key: K) -> OptionResponseHeadersValueItem
    where
        K: AsRef<str>,
    {
        self.read().await.get_response().try_get_header_front(key)
    }

    /// Retrieves the last value of a specific response header.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The key of the header.
    ///
    /// # Returns
    ///
    /// - `OptionResponseHeadersValueItem` - The last value of the header if it exists.
    pub async fn try_get_response_header_back<K>(&self, key: K) -> OptionResponseHeadersValueItem
    where
        K: AsRef<str>,
    {
        self.read().await.get_response().try_get_header_back(key)
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

    /// Retrieves the number of values for a specific response header.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The key of the header.
    ///
    /// # Returns
    ///
    /// - `usize` - The number of values for the specified header.
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

    /// Retrieves a specific cookie by its name from the response.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The name of the cookie to retrieve.
    ///
    /// # Returns
    ///
    /// - `OptionCookiesValue` - The cookie's value if it exists.
    pub async fn try_get_response_cookie<K>(&self, key: K) -> OptionCookiesValue
    where
        K: AsRef<str>,
    {
        self.get_response_cookies().await.get(key.as_ref()).cloned()
    }

    /// Retrieves the body of the response.
    ///
    /// # Returns
    ///
    /// - `ResponseBody` - A clone of the response's body.
    pub async fn get_response_body(&self) -> ResponseBody {
        self.read().await.get_response().get_body().clone()
    }

    /// Sets the body of the response.
    ///
    /// # Arguments
    ///
    /// - `B` - The body to set for the response.
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
    /// - `ResultJsonError<J>` - The deserialized type `J` or a JSON error.
    pub async fn get_response_body_json<J>(&self) -> ResultJsonError<J>
    where
        J: DeserializeOwned,
    {
        self.read().await.get_response().get_body_json()
    }

    /// Retrieves the reason phrase of the response's status code.
    ///
    /// # Returns
    ///
    /// - `ResponseReasonPhrase` - The reason phrase associated with the response's status code.
    pub async fn get_response_reason_phrase(&self) -> ResponseReasonPhrase {
        self.read().await.get_response().get_reason_phrase().clone()
    }

    /// Sets the reason phrase for the response's status code.
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
    /// The status code of the response.
    pub async fn get_response_status_code(&self) -> ResponseStatusCode {
        self.read().await.get_response().get_status_code().clone()
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

    /// Retrieves a specific route parameter by its name.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The name of the route parameter to retrieve.
    ///
    /// # Returns
    ///
    /// - `OptionString` - The value of the route parameter if it exists.
    pub async fn try_get_route_param<T>(&self, name: T) -> OptionString
    where
        T: AsRef<str>,
    {
        self.read()
            .await
            .get_route_params()
            .get(name.as_ref())
            .cloned()
    }

    /// Retrieves all attributes stored in the context.
    ///
    /// # Returns
    ///
    /// - `HashMapArcAnySendSync` - A map containing all attributes.
    pub async fn get_attributes(&self) -> HashMapArcAnySendSync {
        self.read().await.get_attributes().clone()
    }

    /// Retrieves a specific attribute by its key, casting it to the specified type.
    ///
    /// # Arguments
    ///
    /// - `AsRef<str>` - The key of the attribute to retrieve.
    ///
    /// # Returns
    ///
    /// - `Option<V>` - The attribute's value if it exists and can be cast to the specified type.
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
    /// - `Option<V>` - The attribute's value if it exists and can be cast to the specified type.
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
    /// - `OptionPanic` - The panic information if a panic was caught.
    pub async fn try_get_panic(&self) -> OptionPanic {
        self.try_get_internal_attribute(InternalAttribute::Panic)
            .await
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

    /// Sets the send function for the context.
    ///
    /// # Arguments
    ///
    /// - `F: FnContextSendSyncStatic<Fut, ()>, Fut: FutureSendStatic<()>` - The send function to store.
    ///
    /// # Returns
    ///
    /// - `&Self` - A reference to the modified context.
    pub async fn set_send_hook<F, Fut>(&self, hook: F) -> &Self
    where
        F: FnContextSendSyncStatic<Fut, ()>,
        Fut: FutureSendStatic<()>,
    {
        let send_hook: ArcFnContextPinBoxSendSync<()> =
            Arc::new(move |ctx: Context| -> PinBoxFutureSend<()> { Box::pin(hook(ctx)) });
        self.set_internal_attribute(InternalAttribute::SendHook, send_hook)
            .await
    }

    /// Retrieves the send function if it has been set.
    ///
    /// # Returns
    ///
    /// - `OptionArcFnContextPinBoxSendSync<()>` - The send function if it has been set.
    pub async fn try_get_send_hook(&self) -> OptionArcFnContextPinBoxSendSync<()> {
        self.try_get_internal_attribute(InternalAttribute::SendHook)
            .await
    }

    /// Sets the send body function for the context.
    ///
    /// # Arguments
    ///
    /// - `F` - The send body function to store.
    ///
    /// # Returns
    ///
    /// - `&Self` - A reference to the modified context.
    pub async fn set_send_body_hook<F, Fut>(&self, hook: F) -> &Self
    where
        F: FnContextSendSyncStatic<Fut, ()>,
        Fut: FutureSendStatic<()>,
    {
        let send_body_hook: ArcFnContextPinBoxSendSync<()> =
            Arc::new(move |ctx: Context| -> PinBoxFutureSend<()> { Box::pin(hook(ctx)) });
        self.set_internal_attribute(InternalAttribute::SendBodyHook, send_body_hook)
            .await
    }

    /// Retrieves the send body function if it has been set.
    ///
    /// # Returns
    ///
    /// - `OptionArcFnContextPinBoxSendSync<()>` - The send body function if it has been set.
    pub async fn try_get_send_body_hook(&self) -> OptionArcFnContextPinBoxSendSync<()> {
        self.try_get_internal_attribute(InternalAttribute::SendBodyHook)
            .await
    }

    /// Updates the lifecycle status based on the current context state.
    ///
    /// # Arguments
    ///
    /// - `&mut Lifecycle` - The lifecycle to update.
    pub(crate) async fn update_lifecycle_status(&self, lifecycle: &mut Lifecycle) {
        let keep_alive: bool = !self.get_closed().await && lifecycle.is_keep_alive();
        let aborted: bool = self.get_aborted().await;
        lifecycle.update_status(aborted, keep_alive);
    }

    /// Sends the response headers and body to the client.
    ///
    /// # Returns
    ///
    /// - `ResponseResult` - The outcome of the send operation.
    pub async fn send(&self) -> ResponseResult {
        let response_data: ResponseData = self.write().await.get_mut_response().build();
        self.send_with_data(response_data).await
    }

    /// Sends the response and then closes the connection.
    ///
    /// After sending, the connection will be marked as closed.
    ///
    /// # Returns
    ///
    /// - `ResponseResult` - The outcome of the send operation.
    pub async fn send_once(&self) -> ResponseResult {
        let response_data: ResponseData = self.write().await.get_mut_response().build();
        self.send_once_with_data(response_data).await
    }

    /// Sends only the response body to the client.
    ///
    /// This is useful for streaming data or for responses where headers have already been sent.
    ///
    /// # Returns
    ///
    /// - `ResponseResult` - The outcome of the send operation.
    pub async fn send_body(&self) -> ResponseResult {
        let response_body: ResponseBody = self.get_response_body().await;
        self.send_body_with_data(response_body).await
    }

    /// Sends only the response body and then closes the connection.
    ///
    /// After sending the body, the connection will be marked as closed.
    ///
    /// # Returns
    ///
    /// - `ResponseResult` - The outcome of the send operation.
    pub async fn send_body_once(&self) -> ResponseResult {
        let response_body: ResponseBody = self.get_response_body().await;
        self.send_body_once_with_data(response_body).await
    }

    /// Sends the response headers and body to the client with additional data.
    ///
    /// # Arguments
    ///
    /// - `AsRef<[u8]>` - The additional data to send.
    ///
    /// # Returns
    ///
    /// - `ResponseResult` - The outcome of the send operation.
    pub async fn send_with_data<D>(&self, data: D) -> ResponseResult
    where
        D: AsRef<[u8]>,
    {
        if self.is_terminated().await {
            return Err(ResponseError::Terminated);
        }
        if let Some(stream) = self.try_get_stream().await {
            return stream.send(data).await;
        }
        Err(ResponseError::NotFoundStream)
    }

    /// Sends the response and then closes the connection with additional data.
    ///
    /// After sending, the connection will be marked as closed.
    ///
    /// # Arguments
    ///
    /// - `AsRef<[u8]>` - The additional data to send.
    ///
    /// # Returns
    ///
    /// - `ResponseResult` - The outcome of the send operation.
    pub async fn send_once_with_data<D>(&self, data: D) -> ResponseResult
    where
        D: AsRef<[u8]>,
    {
        let res: ResponseResult = self.send_with_data(data).await;
        self.closed().await;
        res
    }

    /// Sends only the response body to the client with additional data.
    ///
    /// This is useful for streaming data or for responses where headers have already been sent.
    ///
    /// # Arguments
    ///
    /// - `AsRef<[u8]>` - The additional data to send as the body.
    ///
    /// # Returns
    ///
    /// - `ResponseResult` - The outcome of the send operation.
    pub async fn send_body_with_data<D>(&self, data: D) -> ResponseResult
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

    /// Sends only the response body and then closes the connection with additional data.
    ///
    /// After sending the body, the connection will be marked as closed.
    ///
    /// # Arguments
    ///
    /// - `AsRef<[u8]>` - The additional data to send as the body.
    ///
    /// # Returns
    ///
    /// - `ResponseResult` - The outcome of the send operation.
    pub async fn send_body_once_with_data<D>(&self, data: D) -> ResponseResult
    where
        D: AsRef<[u8]>,
    {
        let res: ResponseResult = self.send_body_with_data(data).await;
        self.closed().await;
        res
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
    /// - `ResponseResult` - The outcome of the send operation.
    pub async fn send_body_list_with_data<I, D>(&self, data_iter: I) -> ResponseResult
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

    /// Sends a list of response bodies and then closes the connection with additional data.
    ///
    /// After sending the body list, the connection will be marked as closed.
    ///
    /// # Arguments
    ///
    /// - `I: IntoIterator<Item = D>, D: AsRef<[u8]>` - The additional data to send as a list of bodies.
    ///
    /// # Returns
    ///
    /// - `ResponseResult` - The outcome of the send operation.
    pub async fn send_body_list_once_with_data<I, D>(&self, data_iter: I) -> ResponseResult
    where
        I: IntoIterator<Item = D>,
        D: AsRef<[u8]>,
    {
        let res: ResponseResult = self.send_body_list_with_data(data_iter).await;
        self.closed().await;
        res
    }

    /// Flushes the underlying network stream, ensuring all buffered data is sent.
    ///
    /// # Returns
    ///
    /// - `ResponseResult` - The outcome of the flush operation.
    pub async fn flush(&self) -> ResponseResult {
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
    /// - `usize` - The read buffer size.
    ///
    /// # Returns
    ///
    /// - `RequestReaderHandleResult` - The parsed request or error.
    pub async fn http_from_stream(&self, buffer: usize) -> RequestReaderHandleResult {
        if self.get_aborted().await {
            return Err(RequestError::RequestAborted);
        }
        if let Some(stream) = self.try_get_stream().await.as_ref() {
            let request_res: RequestReaderHandleResult =
                Request::http_from_stream(stream, buffer).await;
            if let Ok(request) = request_res.as_ref() {
                self.set_request(request).await;
            }
            return request_res;
        };
        Err(RequestError::GetTcpStream)
    }

    /// Reads a WebSocket frame from the underlying stream.
    ///
    /// # Arguments
    ///
    /// - `usize` - The read buffer size.
    ///
    /// # Returns
    ///
    /// - `RequestReaderHandleResult` - The parsed frame or error.
    pub async fn ws_from_stream(&self, buffer: usize) -> RequestReaderHandleResult {
        if self.get_aborted().await {
            return Err(RequestError::RequestAborted);
        }
        if let Some(stream) = self.try_get_stream().await.as_ref() {
            let mut last_request: Request = self.get_request().await;
            let request_res: RequestReaderHandleResult =
                Request::ws_from_stream(stream, buffer, &mut last_request).await;
            match request_res.as_ref() {
                Ok(request) => {
                    self.set_request(&request).await;
                }
                Err(_) => {
                    self.set_request(&last_request).await;
                }
            }
            return request_res;
        };
        Err(RequestError::GetTcpStream)
    }
}

```

### 📄 File #57 - `mod.rs`
- **Path**: `hyperlane\src\context\mod.rs`
- **Size**: `120 B`
- **Modified Time**: `2025-09-15T22:37:10.292505`

#### Content Preview

```rust
pub(crate) mod r#impl;
pub(crate) mod r#struct;
pub(crate) mod r#type;

pub use r#struct::*;

pub(crate) use r#type::*;

```

### 📄 File #58 - `struct.rs`
- **Path**: `hyperlane\src\context\struct.rs`
- **Size**: `1,814 B`
- **Modified Time**: `2025-09-15T22:37:10.292505`

#### Content Preview

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
    stream: OptionArcRwLockStream,
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
    attributes: HashMapArcAnySendSync,
}

/// The main application context, providing thread-safe access to request and response data.
///
/// This is a wrapper around `ContextInner` that uses an `Arc<RwLock<>>` to allow
/// for shared, mutable access across asynchronous tasks.
#[derive(Clone, Default, Getter, CustomDebug, DisplayDebug)]
pub struct Context(#[get(pub(super))] pub(super) ArcRwLock<ContextInner>);

```

### 📄 File #59 - `type.rs`
- **Path**: `hyperlane\src\context\type.rs`
- **Size**: `451 B`
- **Modified Time**: `2025-09-15T22:37:10.292505`

#### Content Preview

```rust
use crate::*;

/// A type alias for a write guard on the inner context data.
///
/// This provides exclusive, mutable access to the `ContextInner` data.
pub(crate) type RwLockWriteContextInner<'a> = RwLockWriteGuard<'a, ContextInner>;
/// A type alias for a read guard on the inner context data.
///
/// This provides shared, immutable access to the `ContextInner` data.
pub(crate) type RwLockReadContextInner<'a> = RwLockReadGuard<'a, ContextInner>;

```

### 📄 File #60 - `enum.rs`
- **Path**: `hyperlane\src\error\enum.rs`
- **Size**: `931 B`
- **Modified Time**: `2025-09-15T22:37:10.293505`

#### Content Preview

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

### 📄 File #61 - `mod.rs`
- **Path**: `hyperlane\src\error\mod.rs`
- **Size**: `43 B`
- **Modified Time**: `2025-09-15T22:37:10.293505`

#### Content Preview

```rust
pub(crate) mod r#enum;

pub use r#enum::*;

```

### 📄 File #62 - `enum.rs`
- **Path**: `hyperlane\src\hook\enum.rs`
- **Size**: `1,157 B`
- **Modified Time**: `2025-09-15T22:37:10.293505`

#### Content Preview

```rust
use crate::*;

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
    /// - `Option<isize>`: Optional priority of the panic hook. `None` means default.
    PanicHook(Option<isize>),
    /// Executed before a request reaches its designated route handler.
    ///
    /// - `Option<isize>`: Optional priority of the request middleware.
    RequestMiddleware(Option<isize>),
    /// Represents a route handler for a specific path.
    ///
    /// - `&'static str`: The route path handled by this hook.
    Route(&'static str),
    /// Executed after a route handler but before the response is sent.
    ///
    /// - `Option<isize>`: Optional priority of the response middleware.
    ResponseMiddleware(Option<isize>),
}

```

### 📄 File #63 - `fn.rs`
- **Path**: `hyperlane\src\hook\fn.rs`
- **Size**: `1,007 B`
- **Modified Time**: `2025-09-15T22:37:10.293505`

#### Content Preview

```rust
use crate::*;

/// Verify that each `Hook` in the list with the same type and non-zero priority is unique.
///
/// This function iterates over all provided `Hook` items and ensures that no two
/// `Hook` items of the same type define the same non-zero `order`. If a duplicate
/// is found, the function will panic at runtime.
///
/// # Arguments
///
/// - `Vec<HookMacro>`: A vector of `HookMacro` instances to be checked.
///
/// # Panics
///
/// - Panics if two or more `Hook` items of the same type define the same non-zero `order`.
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

### 📄 File #64 - `impl.rs`
- **Path**: `hyperlane\src\hook\impl.rs`
- **Size**: `4,264 B`
- **Modified Time**: `2025-09-15T22:37:10.293505`

#### Content Preview

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
impl<F, T> FnContextPinBoxSendSync<T> for F where F: FnContextSendSync<PinBoxFutureSend<T>> {}

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
impl<T, O> FnPinBoxFutureSend<O> for T where T: Fn() -> PinBoxFutureSend<O> + Send + Sync {}

/// Provides a default implementation for `ServerHook`.
impl Default for ServerHook {
    /// Creates a new `ServerHook` instance with default no-op hooks.
    ///
    /// The default `wait_hook` and `shutdown_hook` do nothing, allowing the server
    /// to run without specific shutdown or wait logic unless configured otherwise.
    ///
    /// # Returns
    ///
    /// - `Self` - A new `ServerHook` instance with default hooks.
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
impl ServerHook {
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

### 📄 File #65 - `mod.rs`
- **Path**: `hyperlane\src\hook\mod.rs`
- **Size**: `236 B`
- **Modified Time**: `2025-09-15T22:37:10.293505`

#### Content Preview

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

### 📄 File #66 - `struct.rs`
- **Path**: `hyperlane\src\hook\struct.rs`
- **Size**: `1,621 B`
- **Modified Time**: `2025-09-15T22:37:10.293505`

#### Content Preview

```rust
use crate::*;

/// Represents the hooks for managing the server's lifecycle, specifically for waiting and shutting down.
///
/// This struct is returned by the `run` method and provides two key hooks:
/// - `wait_hook`: A future that resolves when the server has stopped accepting new connections.
/// - `shutdown_hook`: A function that can be called to gracefully shut down the server.
#[derive(Clone, CustomDebug, DisplayDebug, Getter, Setter)]
pub struct ServerHook {
    /// A hook that returns a future, which completes when the server's main task finishes.
    /// This is typically used to wait for the server to stop accepting connections before
    /// the application exits.
    #[debug(skip)]
    #[get(pub)]
    #[set(pub(crate))]
    pub(super) wait_hook: ArcFnPinBoxFutureSend<()>,
    /// A hook that, when called, initiates a graceful shutdown of the server.
    /// This will stop the server from accepting new connections and allow existing ones
    /// to complete.
    #[debug(skip)]
    #[get(pub)]
    #[set(pub(crate))]
    pub(super) shutdown_hook: ArcFnPinBoxFutureSend<()>,
}

/// Represents a route definition created by a macro.
///
/// This struct encapsulates the necessary information to register a new hook.
#[derive(Getter, Setter, Clone, Debug, PartialEq, Eq)]
pub struct HookMacro {
    /// Represents the asynchronous handler function that is executed when
    /// the associated hook is triggered.
    pub handler: fn(Context) -> PinBoxFutureSend<()>,
    /// Represents the type of the hook that determines when the handler
    /// should be executed.
    pub hook_type: HookType,
}

```

### 📄 File #67 - `trait.rs`
- **Path**: `hyperlane\src\hook\trait.rs`
- **Size**: `1,719 B`
- **Modified Time**: `2025-09-15T22:37:10.293505`

#### Content Preview

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
pub trait FnContextPinBoxSendSync<T>: FnContextSendSync<PinBoxFutureSend<T>> {}
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
/// that futures can be safely managed by the async runtime without lifetime issues.
pub trait FutureSendStatic<T>: Future<Output = T> + Send + 'static {}
/// A trait for `Send`-able futures with a generic output.
pub trait FutureSend<T>: Future<Output = T> + Send {}
/// A trait for thread-safe, reference-counted closures that produce a `PinBoxFutureSend`.
pub trait FnPinBoxFutureSend<T>: Fn() -> PinBoxFutureSend<T> + Send + Sync {}

```

### 📄 File #68 - `type.rs`
- **Path**: `hyperlane\src\hook\type.rs`
- **Size**: `1,639 B`
- **Modified Time**: `2025-09-15T22:37:10.294505`

#### Content Preview

```rust
use crate::*;

/// A type alias for a thread-safe, shareable, pinned, boxed, sendable, synchronous function.
///
/// This type is used for storing handlers in a shared context, allowing multiple
/// parts of the application to safely access and execute the same handler.
pub type ArcFnContextPinBoxSendSync<T> = Arc<dyn FnContextPinBoxSendSync<T>>;
/// An optional, thread-safe, shareable handler function.
///
/// This is used when a handler may or may not be present, such as for optional
/// middleware or hooks.
pub type OptionArcFnContextPinBoxSendSync<T> = Option<ArcFnContextPinBoxSendSync<T>>;
/// A vector of thread-safe, shareable handler functions.
///
/// This type is used to represent a chain of middleware or hooks that can be
/// executed sequentially.
pub type VecArcFnContextPinBoxSendSync<T> = Vec<ArcFnContextPinBoxSendSync<T>>;
/// A type alias for a pinned, boxed, sendable, static future.
///
/// This is a common return type for asynchronous handlers, providing a type-erased
/// future that can be easily managed by the async runtime.
pub type PinBoxFutureSendStatic = Pin<Box<(dyn Future<Output = ()> + Send + 'static)>>;
/// A type alias for a pinned, boxed, `Send`-able future with a generic output.
///
/// This is often used to represent an asynchronous task that can be sent across threads.
pub type PinBoxFutureSend<T> = Pin<Box<dyn Future<Output = T> + Send>>;
/// A type alias for a thread-safe, reference-counted closure that produces a `FnPinBoxFutureSend`.
///
/// This is useful for creating and sharing asynchronous task factories.
pub type ArcFnPinBoxFutureSend<T> = Arc<dyn FnPinBoxFutureSend<T>>;

```

### 📄 File #69 - `enum.rs`
- **Path**: `hyperlane\src\lifecycle\enum.rs`
- **Size**: `789 B`
- **Modified Time**: `2025-09-15T22:37:10.294505`

#### Content Preview

```rust
/// Represents the control flow state of a request's lifecycle.
///
/// This enum is used internally to manage whether the request processing pipeline
/// should proceed to the next stage or be terminated prematurely. It also tracks
/// whether the underlying connection should be kept alive for subsequent requests.
#[derive(Debug, Clone, PartialEq, Eq)]
pub(crate) enum Lifecycle {
    /// Indicates that the request processing should be aborted.
    /// The boolean value specifies whether the connection should be kept alive (`true`) or closed (`false`).
    Abort(bool),
    /// Indicates that the request processing should continue to the next stage.
    /// The boolean value specifies whether the connection should be kept alive (`true`) or closed (`false`).
    Continue(bool),
}

```

### 📄 File #70 - `impl.rs`
- **Path**: `hyperlane\src\lifecycle\impl.rs`
- **Size**: `1,795 B`
- **Modified Time**: `2025-09-15T22:37:10.294505`

#### Content Preview

```rust
use super::*;

/// Implementation of methods for the `Lifecycle` enum.
impl Lifecycle {
    /// Creates a new Lifecycle instance with Continue state.
    ///
    /// # Arguments
    ///
    /// - `bool` - Whether the connection should be kept alive.
    ///
    /// # Returns
    ///
    /// - `Lifecycle` - A new Lifecycle::Continue instance.
    pub(crate) fn new(keep_alive: bool) -> Self {
        Self::Continue(keep_alive)
    }

    /// Updates the lifecycle status based on abort and keep-alive flags.
    ///
    /// # Arguments
    ///
    /// - `&mut self` - A mutable reference to the `Lifecycle` instance.
    /// - `bool` - Whether the request processing has been aborted.
    /// - `bool` - Whether the connection should be kept alive.
    pub(crate) fn update_status(&mut self, aborted: bool, keep_alive: bool) {
        *self = if aborted {
            Lifecycle::Abort(keep_alive)
        } else {
            Lifecycle::Continue(keep_alive)
        };
    }

    /// Checks if the lifecycle state is Abort.
    ///
    /// # Returns
    ///
    /// - `bool` - true if in Abort state, false otherwise.
    pub(crate) fn is_abort(&self) -> bool {
        matches!(self, Lifecycle::Abort(_))
    }

    /// Checks if the connection should be kept alive.
    ///
    /// # Returns
    ///
    /// - `bool` - true if keep-alive flag is set, false otherwise.
    pub(crate) fn is_keep_alive(&self) -> bool {
        matches!(self, Lifecycle::Continue(true) | Lifecycle::Abort(true))
    }

    /// Returns the keep-alive status of the connection.
    ///
    /// # Returns
    ///
    /// - `bool` - The keep-alive flag value.
    pub(crate) fn keep_alive(&self) -> bool {
        match self {
            Lifecycle::Continue(res) | Lifecycle::Abort(res) => *res,
        }
    }
}

```

### 📄 File #71 - `mod.rs`
- **Path**: `hyperlane\src\lifecycle\mod.rs`
- **Size**: `73 B`
- **Modified Time**: `2025-09-15T22:37:10.294505`

#### Content Preview

```rust
pub(crate) mod r#enum;
pub(crate) mod r#impl;

pub(crate) use r#enum::*;

```

### 📄 File #72 - `impl.rs`
- **Path**: `hyperlane\src\panic\impl.rs`
- **Size**: `2,379 B`
- **Modified Time**: `2025-09-15T22:37:10.295504`

#### Content Preview

```rust
use crate::*;

/// Implementation of methods for the `Panic` struct.
impl Panic {
    /// Creates a new `Panic` instance from its constituent parts.
    ///
    /// # Arguments
    ///
    /// - `OptionString` - The panic message.
    /// - `OptionString` - The source code location of the panic.
    /// - `OptionString` - The panic payload.
    ///
    /// # Returns
    ///
    /// - `Panic` - A new panic instance.
    pub(crate) fn new(
        message: OptionString,
        location: OptionString,
        payload: OptionString,
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
    /// - `OptionString` - The extracted message, or None if the payload is not a string type.
    fn try_extract_panic_message(panic_payload: &dyn Any) -> OptionString {
        if let Some(s) = panic_payload.downcast_ref::<&str>() {
            Some(s.to_string())
        } else if let Some(s) = panic_payload.downcast_ref::<String>() {
            Some(s.clone())
        } else {
            None
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
        let mut message: OptionString = if let Ok(panic_join_error) = join_error.try_into_panic() {
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

### 📄 File #73 - `mod.rs`
- **Path**: `hyperlane\src\panic\mod.rs`
- **Size**: `112 B`
- **Modified Time**: `2025-09-15T22:37:10.295504`

#### Content Preview

```rust
pub(crate) mod r#impl;
pub(crate) mod r#struct;
pub(crate) mod r#type;

pub use r#struct::*;
pub use r#type::*;

```

### 📄 File #74 - `struct.rs`
- **Path**: `hyperlane\src\panic\struct.rs`
- **Size**: `897 B`
- **Modified Time**: `2025-09-15T22:37:10.295504`

#### Content Preview

```rust
use crate::*;

/// Represents detailed information about a panic that has occurred within the server.
///
/// This struct captures essential details about a panic, such as the message,
/// source code location, and payload. It is used by the server's panic handling
/// mechanism and passed to the configured panic hook for custom processing.
#[derive(CustomDebug, Default, PartialEq, Eq, Clone, Getter, DisplayDebug)]
pub struct Panic {
    /// The message associated with the panic.
    /// This is `None` if the panic payload is not a string.
    #[get(pub)]
    pub(super) message: OptionString,
    /// The source code location where the panic occurred.
    #[get(pub)]
    pub(super) location: OptionString,
    /// The payload of the panic, often a string literal.
    /// The handler attempts to downcast it to a `&str` or `String`.
    #[get(pub)]
    pub(super) payload: OptionString,
}

```

### 📄 File #75 - `type.rs`
- **Path**: `hyperlane\src\panic\type.rs`
- **Size**: `623 B`
- **Modified Time**: `2025-09-15T22:37:10.295504`

#### Content Preview

```rust
use crate::*;

/// A type alias for an `Option` that may contain a `Panic` struct.
///
/// This is used in contexts where a panic might not have occurred, allowing for
/// graceful handling of both panic and non-panic scenarios.
pub type OptionPanic = Option<Panic>;
/// A type alias for an optional reference to a `Location`.
///
/// The lifetimes `'a` and `'b` are tied to the `PanicHookInfo` from which the
/// location information is sourced. This ensures that the reference does not
/// outlive the panic information itself, preventing dangling pointers.
pub type OptionLocationRef<'a, 'b> = Option<&'a Location<'b>>;

```

### 📄 File #76 - `const.rs`
- **Path**: `hyperlane\src\route\const.rs`
- **Size**: `259 B`
- **Modified Time**: `2025-09-15T22:37:10.295504`

#### Content Preview

```rust
/// The character used to denote the beginning of a dynamic route segment.
pub(crate) const DYNAMIC_ROUTE_LEFT_BRACKET: &str = "{";
/// The character used to denote the end of a dynamic route segment.
pub(crate) const DYNAMIC_ROUTE_RIGHT_BRACKET: &str = "}";

```

### 📄 File #77 - `enum.rs`
- **Path**: `hyperlane\src\route\enum.rs`
- **Size**: `998 B`
- **Modified Time**: `2025-09-15T22:37:10.295504`

#### Content Preview

```rust
use crate::*;

/// Represents the different types of segments that can make up a route path.
///
/// A route path is parsed into a sequence of these segments. For example, the path
/// `/users/:id/posts` would be broken down into `Static("users")`, `Dynamic("id")`,
/// and `Static("posts")`.
#[derive(CustomDebug, Clone)]
pub(crate) enum RouteSegment {
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

### 📄 File #78 - `fn.rs`
- **Path**: `hyperlane\src\route\fn.rs`
- **Size**: `918 B`
- **Modified Time**: `2025-09-15T22:37:10.295504`

#### Content Preview

```rust
use crate::*;

/// Extracts a comparable key from a `RoutePattern`.
///
/// This function iterates over all segments in the pattern and converts
/// each `RouteSegment` into a string slice. For `Regex` segments, only
/// the parameter name is included, ignoring the actual compiled regex.
///
/// # Arguments
///
/// - `&RoutePattern` - A reference to the `RoutePattern` to extract keys from.
///
/// # Returns
///
/// - `Vec<&str>` - A vector of string slices representing each segment of the route.
///   This vector can be used for comparison or hashing purposes.
pub(crate) fn segment_key(pattern: &RoutePattern) -> Vec<&str> {
    pattern
        .get_0()
        .iter()
        .map(|seg| match seg {
            RouteSegment::Static(key) => key.as_str(),
            RouteSegment::Dynamic(key) => key.as_str(),
            RouteSegment::Regex(key, _) => key.as_str(),
        })
        .collect::<Vec<_>>()
}

```

### 📄 File #79 - `impl.rs`
- **Path**: `hyperlane\src\route\impl.rs`
- **Size**: `16,488 B`
- **Modified Time**: `2025-09-15T22:37:10.295504`

#### Content Preview

```rust
use crate::*;

// Collects route macro definitions for the inventory system.
collect!(HookMacro);

/// Provides a default implementation for RouteMatcher.
impl Default for RouteMatcher {
    /// Creates a new, empty RouteMatcher.
    ///
    /// # Returns
    ///
    /// - `RouteMatcher` - A new RouteMatcher with empty storage for static, dynamic, and regex routes.
    fn default() -> Self {
        Self {
            static_routes: hash_map_xx_hash3_64(),
            dynamic_routes: Vec::new(),
            regex_routes: Vec::new(),
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
    /// - `&Self`: The other `RoutePattern` instance to compare against.
    ///
    /// # Returns
    ///
    /// - `bool`: `true` if the instances are equal, `false` otherwise.
    fn eq(&self, other: &Self) -> bool {
        self.get_0() == other.get_0()
    }
}

/// Implements the `Eq` trait for `RoutePattern`.
///
/// This indicates that `RoutePattern` has a total equality relation.
impl Eq for RoutePattern {}

/// Implements the `PartialOrd` trait for `RoutePattern`.
///
/// This allows for partial ordering of `RoutePattern` instances.
impl PartialOrd for RoutePattern {
    /// Partially compares two `RoutePattern` instances.
    ///
    /// # Arguments
    ///
    /// - `&Self`: The other `RoutePattern` instance to compare against.
    ///
    /// # Returns
    ///
    /// - `Option<Ordering>`: The ordering of the two instances.
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
    /// - `&Self`: The other `RoutePattern` instance to compare against.
    ///
    /// # Returns
    ///
    /// - `Ordering`: The ordering of the two instances.
    fn cmp(&self, other: &Self) -> Ordering {
        self.get_0().cmp(&other.get_0())
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
    /// - `&Self`: The other `RouteMatcher` instance to compare against.
    ///
    /// # Returns
    ///
    /// - `bool`: `true` if the instances are equal, `false` otherwise.
    fn eq(&self, other: &Self) -> bool {
        let self_static_keys: HashSet<&String> = self.static_routes.keys().collect();
        let other_static_keys: HashSet<&String> = other.static_routes.keys().collect();
        if self_static_keys != other_static_keys {
            return false;
        }
        let self_dynamic_patterns: HashSet<Vec<&str>> = self
            .dynamic_routes
            .iter()
            .map(|(p, _)| segment_key(p))
            .collect();
        let other_dynamic_patterns: HashSet<Vec<&str>> = other
            .dynamic_routes
            .iter()
            .map(|(p, _)| segment_key(p))
            .collect();
        if self_dynamic_patterns != other_dynamic_patterns {
            return false;
        }
        let self_regex_patterns: HashSet<Vec<&str>> = self
            .regex_routes
            .iter()
            .map(|(p, _)| segment_key(p))
            .collect();
        let other_regex_patterns: HashSet<Vec<&str>> = other
            .regex_routes
            .iter()
            .map(|(p, _)| segment_key(p))
            .collect();
        if self_regex_patterns != other_regex_patterns {
            return false;
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
    /// - `&Self`: The other `RouteSegment` instance to compare against.
    ///
    /// # Returns
    ///
    /// - `Option<Ordering>`: The ordering of the two instances.
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
    /// - `&Self`: The other `RouteSegment` instance to compare against.
    ///
    /// # Returns
    ///
    /// - `Ordering`: The ordering of the two instances.
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
    /// - `&Self`: The other `RouteSegment` instance to compare against.
    ///
    /// # Returns
    ///
    /// - `bool`: `true` if the instances are equal, `false` otherwise.
    fn eq(&self, other: &Self) -> bool {
        match (self, other) {
            (Self::Static(l0), Self::Static(r0)) => l0 == r0,
            (Self::Dynamic(l0), Self::Dynamic(r0)) => l0 == r0,
            (Self::Regex(l0, l1), Self::Regex(r0, r1)) => l0 == r0 && l1.as_str() == r1.as_str(),
            _ => false,
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
    pub(crate) fn new(route: &str) -> ResultRoutePatternRouteError {
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
    /// - `Result<Vec<RouteSegment>, RouteError>` - Vector of RouteSegments on success, or RouteError on failure.
    fn parse_route(route: &str) -> ResultVecRouteSegmentRouteError {
        if route.is_empty() {
            return Err(RouteError::EmptyPattern);
        }
        let route: &str = route.trim_start_matches(DEFAULT_HTTP_PATH);
        if route.is_empty() {
            return Ok(Vec::new());
        }
        let estimated_segments: usize = route.matches(DEFAULT_HTTP_PATH).count() + 1;
        let mut segments: VecRouteSegment = Vec::with_capacity(estimated_segments);
        for segment in route.split(DEFAULT_HTTP_PATH) {
            if segment.starts_with(DYNAMIC_ROUTE_LEFT_BRACKET)
                && segment.ends_with(DYNAMIC_ROUTE_RIGHT_BRACKET)
            {
                let content: &str = &segment[1..segment.len() - 1];
                if let Some((name, pattern)) = content.split_once(':') {
                    match Regex::new(pattern) {
                        Ok(regex) => {
                            segments.push(RouteSegment::Regex(name.to_owned(), regex));
                        }
                        Err(err) => {
                            return Err(RouteError::InvalidRegexPattern(format!(
                                "Invalid regex pattern '{}{}{}",
                                pattern, COLON_SPACE, err
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
    pub(crate) fn try_match_path(&self, path: &str) -> OptionRouteParams {
        let path: &str = path.trim_start_matches(DEFAULT_HTTP_PATH);
        let route_segments_len: usize = self.get_0().len();
        let is_tail_regex: bool = matches!(self.get_0().last(), Some(RouteSegment::Regex(_, _)));
        if path.is_empty() {
            if route_segments_len == 0 {
                return Some(hash_map_xx_hash3_64());
            }
            return None;
        }
        let mut path_segments: VecStrRef = Vec::with_capacity(route_segments_len);
        let mut segment_start: usize = 0;
        let path_bytes: &[u8] = path.as_bytes();
        let path_separator_byte: u8 = b'/';
        for i in 0..path_bytes.len() {
            if path_bytes[i] == path_separator_byte {
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
                    let Some(value) = path_segments.get(idx) else {
                        return None;
                    };
                    params.insert(param_name.clone(), value.to_string());
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
    pub(crate) fn is_dynamic(&self) -> bool {
        self.get_0()
            .iter()
            .any(|seg| matches!(seg, RouteSegment::Dynamic(_)))
            && self
                .get_0()
                .iter()
                .all(|seg| !matches!(seg, RouteSegment::Regex(_, _)))
    }
}

/// Manages a collection of routes, enabling efficient lookup and dispatch.
///
/// This struct stores routes categorized by type (static, dynamic, regex)
/// to quickly find the appropriate handler for incoming requests.
impl RouteMatcher {
    /// Creates a new, empty RouteMatcher.
    ///
    /// # Returns
    ///
    /// - `RouteMatcher` - A new RouteMatcher instance with empty route stores.
    pub(crate) fn new() -> Self {
        Self {
            static_routes: hash_map_xx_hash3_64(),
            dynamic_routes: Vec::new(),
            regex_routes: Vec::new(),
        }
    }

    /// Adds a new route and its handler to the matcher.
    ///
    /// The route is categorized as static, dynamic, or regex based on its pattern.
    ///
    /// # Arguments
    ///
    /// - `&str` - The route pattern string.
    /// - `ArcFnContextPinBoxSendSync` - The handler function for this route.
    ///
    /// # Returns
    ///
    /// - `Result<(), RouteError>` - Ok on success, or RouteError if pattern is duplicate.
    pub(crate) fn add(
        &mut self,
        pattern: &str,
        handler: ArcFnContextPinBoxSendSync<()>,
    ) -> ResultAddRoute {
        let route_pattern: RoutePattern = RoutePattern::new(pattern)?;
        if route_pattern.is_static() {
            if self.get_static_routes().contains_key(pattern) {
                return Err(RouteError::DuplicatePattern(pattern.to_owned()));
            }
            self.get_mut_static_routes()
                .insert(pattern.to_string(), handler);
            return Ok(());
        }
        let target_vec: &mut VecRoutePatternArcFnPinBoxSendSync<()> = if route_pattern.is_dynamic()
        {
            self.get_mut_dynamic_routes()
        } else {
            self.get_mut_regex_routes()
        };
        let has_same_pattern: bool = target_vec
            .iter()
            .any(|(tmp_pattern, _)| tmp_pattern == &route_pattern);
        if has_same_pattern {
            return Err(RouteError::DuplicatePattern(pattern.to_owned()));
        }
        target_vec.push((route_pattern, handler));
        Ok(())
    }

    /// Finds the handler for a path by matching against registered routes.
    ///
    /// # Arguments
    ///
    /// - `&Context` - The request context.
    /// - `&str` - The request path to resolve.
    ///
    /// # Returns
    ///
    /// - `Option<ArcFnContextPinBoxSendSync>` - Some handler if match found, None otherwise.
    pub(crate) async fn try_resolve_route(
        &self,
        ctx: &Context,
        path: &str,
    ) -> OptionArcFnContextPinBoxSendSync<()> {
        if let Some(handler) = self.get_static_routes().get(path) {
            ctx.set_route_params(RouteParams::default()).await;
            return Some(handler.clone());
        }
        for (pattern, handler) in self.get_dynamic_routes().iter() {
            if let Some(params) = pattern.try_match_path(path) {
                ctx.set_route_params(params).await;
                return Some(handler.clone());
            }
        }
        for (pattern, handler) in self.get_regex_routes().iter() {
            if let Some(params) = pattern.try_match_path(path) {
                ctx.set_route_params(params).await;
                return Some(handler.clone());
            }
        }
        None
    }
}

```

### 📄 File #80 - `mod.rs`
- **Path**: `hyperlane\src\route\mod.rs`
- **Size**: `265 B`
- **Modified Time**: `2025-09-15T22:37:10.297007`

#### Content Preview

```rust
pub(crate) mod r#const;
pub(crate) mod r#enum;
pub(crate) mod r#fn;
pub(crate) mod r#impl;
pub(crate) mod r#struct;
pub(crate) mod r#type;

pub use r#type::*;

pub(crate) use r#const::*;
pub(crate) use r#enum::*;
pub(crate) use r#fn::*;
pub(crate) use r#struct::*;

```

### 📄 File #81 - `struct.rs`
- **Path**: `hyperlane\src\route\struct.rs`
- **Size**: `1,966 B`
- **Modified Time**: `2025-09-15T22:37:10.297007`

#### Content Preview

```rust
use crate::*;

/// Represents a parsed and structured route pattern.
///
/// This struct wraps a vector of `RouteSegment`s, which are the individual components
/// of a URL path. It is used internally by the `RouteMatcher` to perform efficient
/// route matching against incoming requests.
#[derive(Debug, Clone, Getter, DisplayDebug)]
pub(crate) struct RoutePattern(
    /// The collection of segments that make up the route pattern.
    #[get(pub(super))]
    pub(super) VecRouteSegment,
);

/// The core routing engine responsible for matching request paths to their corresponding handlers.
///
/// The matcher categorizes routes into three types for optimized performance:
/// 1.  `static_routes`: For exact path matches, offering the fastest lookups.
/// 2.  `dynamic_routes`: For paths with variable segments.
/// 3.  `regex_routes`: For complex matching based on regular expressions.
///
/// When a request comes in, the matcher checks these categories in order to find the appropriate handler.
#[derive(Clone, CustomDebug, Getter, GetterMut, DisplayDebug)]
pub(crate) struct RouteMatcher {
    /// A hash map for storing and quickly retrieving handlers for static routes.
    /// These are routes without any variable path segments.
    #[debug(skip)]
    #[get(pub(super))]
    #[get_mut(pub(super))]
    pub(super) static_routes: HashMapStringArcFnPinBoxSendSyncXxHash3_64<()>,
    /// A vector of routes that contain dynamic segments.
    /// These are evaluated sequentially if no static route matches.
    #[debug(skip)]
    #[get(pub(super))]
    #[get_mut(pub(super))]
    pub(super) dynamic_routes: VecRoutePatternArcFnPinBoxSendSync<()>,
    /// A vector of routes that use regular expressions for matching.
    /// These provide the most flexibility but are evaluated last due to their performance overhead.
    #[debug(skip)]
    #[get(pub(super))]
    #[get_mut(pub(super))]
    pub(super) regex_routes: VecRoutePatternArcFnPinBoxSendSync<()>,
}

```

### 📄 File #82 - `type.rs`
- **Path**: `hyperlane\src\route\type.rs`
- **Size**: `1,826 B`
- **Modified Time**: `2025-09-15T22:37:10.297007`

#### Content Preview

```rust
use crate::*;

/// A type alias for a hash map that stores captured route parameters.
///
/// The key is the parameter name and the value is the captured string.
pub type RouteParams = HashMapXxHash3_64<String, String>;
/// A type alias for a vector of `RouteSegment`s.
///
/// This is used to represent a parsed route.
pub(crate) type VecRouteSegment = Vec<RouteSegment>;
/// A type alias for a vector of string slices.
///
/// This is often used for path components.
pub(crate) type VecStrRef<'a> = Vec<&'a str>;
/// A type alias for a vector containing tuples of a `RoutePattern` and its associated handler function.
///
/// This is used for storing dynamic and regex routes.
pub(crate) type VecRoutePatternArcFnPinBoxSendSync<T> =
    Vec<(RoutePattern, ArcFnContextPinBoxSendSync<T>)>;
/// A type alias for a hash map that stores static routes and their handlers.
///
/// The key is the exact path string.
pub(crate) type HashMapStringArcFnPinBoxSendSyncXxHash3_64<T> =
    HashMapXxHash3_64<String, ArcFnContextPinBoxSendSync<T>>;
/// A type alias for a `Result` returned when adding a new route.
///
/// This indicates success or a `RouteError`.
pub(crate) type ResultAddRoute = Result<(), RouteError>;
/// A type alias for a `Result` from parsing a route string.
///
/// This yields a vector of `RouteSegment`s or a `RouteError`.
pub(crate) type ResultVecRouteSegmentRouteError = Result<VecRouteSegment, RouteError>;
/// A type alias for a `Result` from creating a `RoutePattern`.
///
/// This can fail with a `RouteError`.
pub(crate) type ResultRoutePatternRouteError = Result<RoutePattern, RouteError>;
/// A type alias for an optional `RouteParams` map.
///
/// It is `Some` if a dynamic or regex route matches and captures parameters, and `None` otherwise.
pub(crate) type OptionRouteParams = Option<RouteParams>;

```

### 📄 File #83 - `impl.rs`
- **Path**: `hyperlane\src\server\impl.rs`
- **Size**: `22,949 B`
- **Modified Time**: `2025-10-01T21:58:27.401735`

#### Content Preview

```rust
use crate::*;

/// Provides a default implementation for ServerInner.
impl Default for ServerInner {
    /// Creates a new ServerInner instance with default values.
    ///
    /// # Returns
    ///
    /// - `Self` - A new instance with default configuration.
    fn default() -> Self {
        Self {
            config: ServerConfigInner::default(),
            panic_hook: vec![],
            request_middleware: vec![],
            route: RouteMatcher::new(),
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
    /// - `&Self`: The other `ServerInner` instance to compare against.
    ///
    /// # Returns
    ///
    /// - `bool`: `true` if the instances are equal, `false` otherwise.
    fn eq(&self, other: &Self) -> bool {
        self.config == other.config
            && self.route == other.route
            && self.request_middleware.len() == other.request_middleware.len()
            && self.response_middleware.len() == other.response_middleware.len()
            && self.panic_hook.len() == other.panic_hook.len()
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
            && self
                .panic_hook
                .iter()
                .zip(other.panic_hook.iter())
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
    /// - `&Self`: The other `Server` instance to compare against.
    ///
    /// # Returns
    ///
    /// - `bool`: `true` if the instances are equal, `false` otherwise.
    fn eq(&self, other: &Self) -> bool {
        if Arc::ptr_eq(&self.get_0(), &other.get_0()) {
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
impl<'a> HandlerState {
    /// Creates a new HandlerState instance.
    ///
    /// # Arguments
    ///
    /// - `&'a ArcRwLockStream` - The network stream.
    /// - `&'a Context` - The request context.
    /// - `usize` - The buffer size for reading HTTP requests.
    ///
    /// # Returns
    ///
    /// - `Self` - The newly created handler state.
    pub(super) fn new(stream: ArcRwLockStream, ctx: Context, buffer: usize) -> Self {
        Self {
            stream,
            ctx,
            buffer,
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
    /// - `RwLockReadGuardServerInner` - The read guard for ServerInner.
    async fn read(&self) -> RwLockReadGuardServerInner {
        self.get_0().read().await
    }

    /// Acquires a write lock on the inner server data.
    ///
    /// # Returns
    ///
    /// - `RwLockWriteGuardServerInner` - The write guard for ServerInner.
    async fn write(&self) -> RwLockWriteGuardServerInner {
        self.get_0().write().await
    }

    /// Handle a given hook macro asynchronously.
    ///
    /// This function dispatches the provided `HookMacro` to the appropriate
    /// internal handler based on its `HookType`. Supported hook types include
    /// panic hooks, disable HTTP/WS hooks, connected hooks, pre-upgrade hooks,
    /// request/response middleware, and routes.
    ///
    /// # Arguments
    ///
    /// - `HookMacro`: The `HookMacro` instance containing the `HookType` and its handler.
    pub async fn handle_hook(&self, hook: HookMacro) {
        match hook.hook_type {
            HookType::PanicHook(_) => {
                self.panic_hook(hook.handler).await;
            }
            HookType::RequestMiddleware(_) => {
                self.request_middleware(hook.handler).await;
            }
            HookType::Route(path) => {
                self.route(path, hook.handler).await;
            }
            HookType::ResponseMiddleware(_) => {
                self.response_middleware(hook.handler).await;
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
        let config: ServerConfig = ServerConfig::from_str(&config_str.to_string()).unwrap();
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

    /// Sets a custom panic hook for request processing.
    ///
    /// # Arguments
    ///
    /// - `F: FnContextSendSyncStatic<Fut, ()>` - The panic handler function.
    /// - `Fut: FutureSendStatic<()>` - The future returned by the panic handler.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to self for method chaining.
    pub async fn panic_hook<F, Fut>(&self, hook: F) -> &Self
    where
        F: FnContextSendSyncStatic<Fut, ()>,
        Fut: FutureSendStatic<()>,
    {
        let panic_hook: ArcFnContextPinBoxSendSync<()> =
            Arc::new(move |ctx: Context| -> PinBoxFutureSend<()> { Box::pin(hook(ctx)) });
        self.write().await.get_mut_panic_hook().push(panic_hook);
        self
    }

    /// Adds a route handler for a specific path.
    ///
    /// # Arguments
    ///
    /// - `R: ToString` - The route path pattern.
    /// - `F: FnContextSendSyncStatic<Fut, ()>` - The handler function for the route.
    /// - `Fut: FutureSendStatic<()>` - The future returned by the handler.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to self for method chaining.
    pub async fn route<R, F, Fut>(&self, route: R, hook: F) -> &Self
    where
        R: ToString,
        F: FnContextSendSyncStatic<Fut, ()>,
        Fut: FutureSendStatic<()>,
    {
        let route_str: String = route.to_string();
        let route_hook: ArcFnContextPinBoxSendSync<()> =
            Arc::new(move |ctx: Context| -> PinBoxFutureSend<()> { Box::pin(hook(ctx)) });
        self.write()
            .await
            .get_mut_route()
            .add(&route_str, route_hook)
            .unwrap();
        self
    }

    /// Adds request middleware to the processing pipeline.
    ///
    /// # Arguments
    ///
    /// - `F: FnContextSendSyncStatic<Fut, ()>` - The middleware function.
    /// - `Fut: FutureSendStatic<()>` - The future returned by the middleware.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to self for method chaining.
    pub async fn request_middleware<F, Fut>(&self, hook: F) -> &Self
    where
        F: FnContextSendSyncStatic<Fut, ()>,
        Fut: FutureSendStatic<()>,
    {
        let request_middleware_hook: ArcFnContextPinBoxSendSync<()> =
            Arc::new(move |ctx: Context| -> PinBoxFutureSend<()> { Box::pin(hook(ctx)) });
        self.write()
            .await
            .get_mut_request_middleware()
            .push(request_middleware_hook);
        self
    }

    /// Adds response middleware to the processing pipeline.
    ///
    /// # Arguments
    ///
    /// - `F: FnContextSendSyncStatic<Fut, ()>` - The middleware function.
    /// - `Fut: FutureSendStatic<()>` - The future returned by the middleware.
    ///
    /// # Returns
    ///
    /// - `&Self` - Reference to self for method chaining.
    pub async fn response_middleware<F, Fut>(&self, hook: F) -> &Self
    where
        F: FnContextSendSyncStatic<Fut, ()>,
        Fut: FutureSendStatic<()>,
    {
        let response_middleware_hook: ArcFnContextPinBoxSendSync<()> =
            Arc::new(move |ctx: Context| -> PinBoxFutureSend<()> { Box::pin(hook(ctx)) });
        self.write()
            .await
            .get_mut_response_middleware()
            .push(response_middleware_hook);
        self
    }

    /// Formats the host and port into a bindable address string.
    ///
    /// # Arguments
    ///
    /// - `H: ToString` - The host address.
    /// - `usize` - The port number.
    ///
    /// # Returns
    ///
    /// - `String` - The formatted address string.
    pub fn format_host_port<H: ToString>(host: H, port: usize) -> String {
        format!("{}{}{}", host.to_string(), COLON_SPACE_SYMBOL, port)
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
            hook(ctx.clone()).await;
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
        self.handle_panic_with_context(&ctx, &panic).await;
    }

    /// Executes a given hook function within a spawned task and manages the request lifecycle.
    ///
    /// This function also handles panics that may occur within the hook's execution.
    ///
    /// # Arguments
    ///
    /// - `ctx: &Context` - The request context.
    /// - `lifecycle: &mut Lifecycle` - A mutable reference to the current `Lifecycle` state.
    /// - `hook: ArcFnContextPinBoxSendSync<()>` - The hook function to execute.
    async fn run_hook_with_lifecycle(
        &self,
        ctx: &Context,
        lifecycle: &mut Lifecycle,
        hook: &ArcFnContextPinBoxSendSync<()>,
    ) {
        let result: ResultJoinError<()> = spawn(hook(ctx.clone())).await;
        ctx.update_lifecycle_status(lifecycle).await;
        if let Err(join_error) = result {
            if join_error.is_panic() {
                self.handle_task_panic(&ctx, join_error).await;
            }
        }
    }

    /// Creates and binds a `TcpListener` based on the server's configuration.
    ///
    /// # Returns
    ///
    /// Returns a `ServerResult` containing the bound `TcpListener` on success,
    /// or a `ServerError` on failure.
    async fn create_tcp_listener(&self) -> ServerResult<TcpListener> {
        let config: ServerConfigInner = self.read().await.get_config().clone();
        let host: String = config.get_host().clone();
        let port: usize = *config.get_port();
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
    /// - `ServerResult<()>` - A `ServerResult` which is typically `Ok(())` unless an unrecoverable
    /// error occurs.
    async fn accept_connections(&self, tcp_listener: &TcpListener) -> ServerResult<()> {
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
        let server_inner: RwLockReadGuardServerInner = self.read().await;
        let config: &ServerConfigInner = server_inner.get_config();
        let linger_opt: &OptionDuration = config.get_linger();
        let nodelay_opt: &OptionBool = config.get_nodelay();
        let ttl_opt: &OptionU32 = config.get_ttl();
        let _ = stream.set_linger(*linger_opt);
        if let Some(nodelay) = nodelay_opt {
            let _ = stream.set_nodelay(*nodelay);
        }
        if let Some(ttl) = ttl_opt {
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
        let buffer: usize = *self.read().await.get_config().get_buffer();
        spawn(async move {
            server.handle_connection(stream, buffer).await;
        });
    }

    /// Handles a single client connection, determining whether it's an HTTP or WebSocket request.
    ///
    /// It reads the initial request from the stream and dispatches it to the appropriate handler.
    ///
    /// # Arguments
    ///
    /// - `ArcRwLockStream` - The stream for the client connection.
    /// - `usize` - The buffer size to use for reading the initial HTTP request.
    async fn handle_connection(&self, stream: ArcRwLockStream, buffer: usize) {
        if let Ok(request) = Request::http_from_stream(&stream, buffer).await {
            let ctx: Context = Context::create_context(&stream, &request);
            let handler: HandlerState = HandlerState::new(stream, ctx, buffer);
            self.handle_http_requests(&handler, &request).await;
        }
    }

    /// Executes all registered request middleware in sequence.
    ///
    /// # Arguments
    ///
    /// - `&Context` - The request context.
    /// - `&mut Lifecycle` - A mutable reference to the request lifecycle state.
    ///
    /// # Returns
    ///
    /// - `bool` - `true` if the lifecycle was aborted, `false` otherwise.
    async fn run_request_middleware(&self, ctx: &Context, lifecycle: &mut Lifecycle) -> bool {
        for hook in self.read().await.get_request_middleware().iter() {
            self.run_hook_with_lifecycle(ctx, lifecycle, hook).await;
            if lifecycle.is_abort() {
                return true;
            }
        }
        false
    }

    /// Executes the matched route handler.
    ///
    /// # Arguments
    ///
    /// - `&Context` - The request context.
    /// - `&OptionArcFnContextPinBoxSendSync` - An `Option` containing the handler function if a route was matched.
    /// - `&mut Lifecycle` - A mutable reference to the request lifecycle state.
    ///
    /// # Returns
    ///
    /// - `bool` - `true` if the lifecycle was aborted, `false` otherwise.
    async fn run_route_hook(
        &self,
        ctx: &Context,
        handler: &OptionArcFnContextPinBoxSendSync<()>,
        lifecycle: &mut Lifecycle,
    ) -> bool {
        if let Some(hook) = handler {
            self.run_hook_with_lifecycle(ctx, lifecycle, hook).await;
        }
        lifecycle.is_abort()
    }

    /// Executes all registered response middleware in sequence.
    ///
    /// # Arguments
    ///
    /// - `&Context` - The request context.
    /// - `&mut Lifecycle` - A mutable reference to the request lifecycle state.
    ///
    /// # Returns
    ///
    /// - `bool` - `true` if the lifecycle was aborted, `false` otherwise.
    async fn run_response_middleware(&self, ctx: &Context, lifecycle: &mut Lifecycle) -> bool {
        for hook in self.read().await.get_response_middleware().iter() {
            self.run_hook_with_lifecycle(ctx, lifecycle, hook).await;
            if lifecycle.is_abort() {
                return true;
            }
        }
        false
    }

    /// The core request handling pipeline.
    ///
    /// This function orchestrates the execution of request middleware, the route handler,
    /// and response middleware.
    ///
    /// # Arguments
    ///
    /// - `&HandlerState` - The `HandlerState` for the current connection.
    /// - `&Request` - The incoming request to be processed.
    ///
    /// # Returns
    ///
    /// - `bool` - A boolean indicating whether the connection should be kept alive.
    async fn request_hook<'a>(&self, state: &HandlerState, request: &Request) -> bool {
        let route: &str = request.get_path();
        let ctx: &Context = state.get_ctx();
        ctx.set_request(request).await;
        let mut lifecycle: Lifecycle = Lifecycle::new(request.is_enable_keep_alive());
        let route_hook: OptionArcFnContextPinBoxSendSync<()> = self
            .read()
            .await
            .get_route()
            .try_resolve_route(ctx, route)
            .await;
        if self.run_request_middleware(ctx, &mut lifecycle).await {
            return lifecycle.keep_alive();
        }
        if self.run_route_hook(ctx, &route_hook, &mut lifecycle).await {
            return lifecycle.keep_alive();
        }
        self.run_response_middleware(ctx, &mut lifecycle).await;
        lifecycle.keep_alive()
    }

    /// Handles subsequent HTTP requests on a persistent (keep-alive) connection.
    ///
    /// # Arguments
    ///
    /// - `&HandlerState` - The `HandlerState` for the current connection.
    /// - `&Request` - The initial request that established the keep-alive connection.
    async fn handle_http_requests<'a>(&self, state: &HandlerState, request: &Request) {
        if self.request_hook(state, request).await {
            return;
        }
        let stream: &ArcRwLockStream = state.get_stream();
        let buffer: usize = *state.get_buffer();
        while let Ok(new_request) = &Request::http_from_stream(stream, buffer).await {
            if !self.request_hook(state, new_request).await {
                return;
            }
        }
    }

    /// Starts the server, binds to the configured address, and begins listening for connections.
    ///
    /// This is the main entry point to launch the server. It will initialize the panic hook,
    /// create a TCP listener, and then enter the connection acceptance loop in a background task.
    ///
    /// # Returns
    ///
    /// Returns a `ServerResult` containing a shutdown function on success.
    /// Calling this function will shut down the server by aborting its main task.
    /// Returns an error if the server fails to start.
    pub async fn run(&self) -> ServerResult<ServerHook> {
        let tcp_listener: TcpListener = self.create_tcp_listener().await?;
        let server: Server = self.clone();
        let (wait_sender, wait_receiver) = channel(());
        let (shutdown_sender, mut shutdown_receiver) = channel(());
        let accept_connections: JoinHandle<()> = spawn(async move {
            let _ = server.accept_connections(&tcp_listener).await;
            let _ = wait_sender.send(());
        });
        let wait_hook: ArcFnPinBoxFutureSend<()> = Arc::new(move || {
            let mut wait_receiver_clone: Receiver<()> = wait_receiver.clone();
            Box::pin(async move {
                let _ = wait_receiver_clone.changed().await;
            })
        });
        let shutdown_hook: ArcFnPinBoxFutureSend<()> = Arc::new(move || {
            let shutdown_sender_clone: Sender<()> = shutdown_sender.clone();
            Box::pin(async move {
                let _ = shutdown_sender_clone.send(());
            })
        });
        spawn(async move {
            let _ = shutdown_receiver.changed().await;
            accept_connections.abort();
        });
        let mut server_hook: ServerHook = ServerHook::default();
        server_hook.set_shutdown_hook(shutdown_hook);
        server_hook.set_wait_hook(wait_hook);
        Ok(server_hook)
    }
}

```

### 📄 File #84 - `mod.rs`
- **Path**: `hyperlane\src\server\mod.rs`
- **Size**: `112 B`
- **Modified Time**: `2025-09-15T22:37:10.297518`

#### Content Preview

```rust
pub(crate) mod r#impl;
pub(crate) mod r#struct;
pub(crate) mod r#type;

pub use r#struct::*;
pub use r#type::*;

```

### 📄 File #85 - `struct.rs`
- **Path**: `hyperlane\src\server\struct.rs`
- **Size**: `3,247 B`
- **Modified Time**: `2025-09-15T22:37:10.298034`

#### Content Preview

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
    /// This provides access to the raw TCP stream for reading and writing data.
    pub(super) stream: ArcRwLockStream,
    /// A reference to the context of the current request.
    /// This contains request-specific information, such as headers, method, and URI.
    pub(super) ctx: Context,
    /// The size of the buffer used for reading HTTP requests.
    /// This is used to determine the maximum size of the request body.
    pub(super) buffer: usize,
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
    pub(super) route: RouteMatcher,
    /// A collection of middleware functions that are executed for every incoming request
    /// before it is passed to the corresponding route handler.
    #[debug(skip)]
    #[get(pub(super))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    pub(super) request_middleware: VecArcFnContextPinBoxSendSync<()>,
    /// A collection of middleware functions that are executed for every outgoing response
    /// before it is sent back to the client.
    #[debug(skip)]
    #[get(pub(super))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    pub(super) response_middleware: VecArcFnContextPinBoxSendSync<()>,
    /// A custom error handler that is invoked when a panic occurs during request processing.
    /// This allows for graceful error recovery and customized error responses.
    #[debug(skip)]
    #[get(pub(super))]
    #[get_mut(pub(super))]
    #[set(pub(super))]
    pub(super) panic_hook: VecArcFnContextPinBoxSendSync<()>,
}

/// The primary server structure that provides a thread-safe interface to the server's state.
///
/// This struct acts as a public-facing wrapper around an `Arc<RwLock<ServerInner>>`.
/// It allows multiple parts of the application to safely share and modify the server's
/// configuration and state across different threads and asynchronous tasks.
#[derive(Clone, Getter, CustomDebug, DisplayDebug, Default)]
pub struct Server(#[get(pub(super))] pub(super) ArcRwLockServerInner);

```

### 📄 File #86 - `type.rs`
- **Path**: `hyperlane\src\server\type.rs`
- **Size**: `1,331 B`
- **Modified Time**: `2025-09-15T22:37:10.298034`

#### Content Preview

```rust
use crate::*;

/// A type alias for a `Result` that returns a `ServerError` on failure.
///
/// This is commonly used throughout the server's public-facing API.
pub type ServerResult<T> = Result<T, ServerError>;
/// A type alias for a `Result` that returns a `JoinError` on failure.
///
/// This is used when waiting for asynchronous tasks to complete.
pub type ResultJoinError<T> = Result<T, JoinError>;
/// A type alias for a thread-safe, reference-counted read-write lock over `ServerInner`.
///
/// This is the core mechanism for sharing server state across threads.
pub(crate) type ArcRwLockServerInner = ArcRwLock<ServerInner>;
/// A type alias for a thread-safe, reference-counted read-write lock over `ServerConfigInner`.
///
/// This is the core mechanism for sharing server config state across threads.
pub(crate) type ArcRwLockServerConfigInner = ArcRwLock<ServerConfigInner>;
/// A type alias for a read guard on the `ServerInner`'s `RwLock`.
///
/// This provides read-only access to the server's internal state.
pub(crate) type RwLockReadGuardServerInner<'a> = RwLockReadGuard<'a, ServerInner>;
/// A type alias for a write guard on the `ServerInner`'s `RwLock`.
///
/// This provides mutable access to the server's internal state.
pub(crate) type RwLockWriteGuardServerInner<'a> = RwLockWriteGuard<'a, ServerInner>;

```

### 📄 File #87 - `attribute.rs`
- **Path**: `hyperlane\src\tests\attribute.rs`
- **Size**: `2,282 B`
- **Modified Time**: `2025-09-15T22:37:10.298034`

#### Content Preview

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
    let func: &(dyn Fn(&str) -> String + Send + Sync) = &|msg: &str| {
        return msg.to_string();
    };
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
    ctx.set_send_body_hook(send_body_hook_fn).await;
    assert!(ctx.try_get_send_body_hook().await.is_some());
}

```

### 📄 File #88 - `config.rs`
- **Path**: `hyperlane\src\tests\config.rs`
- **Size**: `730 B`
- **Modified Time**: `2025-09-15T22:37:10.298034`

#### Content Preview

```rust
use crate::*;

#[tokio::test]
async fn config_from_str() {
    let config_str: &'static str = r#"
        {
            "host": "0.0.0.0",
            "port": 80,           
            "buffer": 4096,
            "nodelay": true,
            "linger": { "secs": 64, "nanos": 0 },
            "ttl": 64
        }
    "#;
    let config: ServerConfig = ServerConfig::from_str(config_str).unwrap();
    let new_config: ServerConfig = ServerConfig::new().await;
    new_config.host("0.0.0.0").await;
    new_config.port(80).await;
    new_config.buffer(4096).await;
    new_config.enable_nodelay().await;
    new_config.linger(Some(Duration::from_secs(64))).await;
    new_config.ttl(64).await;
    assert_eq!(config, new_config);
}

```

### 📄 File #89 - `context.rs`
- **Path**: `hyperlane\src\tests\context.rs`
- **Size**: `1,649 B`
- **Modified Time**: `2025-09-15T22:37:10.298034`

#### Content Preview

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
    let id: OptionString = ctx.try_get_route_param("id").await;
    assert_eq!(id, Some("123".to_string()));
    let name: OptionString = ctx.try_get_route_param("name").await;
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

### 📄 File #90 - `error.rs`
- **Path**: `hyperlane\src\tests\error.rs`
- **Size**: `1,803 B`
- **Modified Time**: `2025-09-15T22:37:10.298034`

#### Content Preview

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

### 📄 File #91 - `lifecycle.rs`
- **Path**: `hyperlane\src\tests\lifecycle.rs`
- **Size**: `2,405 B`
- **Modified Time**: `2025-09-15T22:37:10.298034`

#### Content Preview

```rust
use crate::*;

#[tokio::test]
async fn lifecycle_new() {
    let lifecycle: Lifecycle = Lifecycle::new(true);
    assert_eq!(lifecycle, Lifecycle::Continue(true));
    assert!(lifecycle.is_keep_alive());
    assert!(!lifecycle.is_abort());
}

#[tokio::test]
async fn lifecycle_update_status() {
    let mut lifecycle: Lifecycle = Lifecycle::new(true);
    lifecycle.update_status(true, true);
    assert_eq!(lifecycle, Lifecycle::Abort(true));
    assert!(lifecycle.is_abort());
    assert!(lifecycle.is_keep_alive());
    lifecycle.update_status(true, false);
    assert_eq!(lifecycle, Lifecycle::Abort(false));
    assert!(lifecycle.is_abort());
    assert!(!lifecycle.is_keep_alive());
    lifecycle.update_status(false, true);
    assert_eq!(lifecycle, Lifecycle::Continue(true));
    assert!(!lifecycle.is_abort());
    assert!(lifecycle.is_keep_alive());
    lifecycle.update_status(false, false);
    assert_eq!(lifecycle, Lifecycle::Continue(false));
    assert!(!lifecycle.is_abort());
    assert!(!lifecycle.is_keep_alive());
}

#[tokio::test]
async fn lifecycle_is_abort() {
    let abort_true: Lifecycle = Lifecycle::Abort(true);
    assert!(abort_true.is_abort());
    let abort_false: Lifecycle = Lifecycle::Abort(false);
    assert!(abort_false.is_abort());
    let continue_true: Lifecycle = Lifecycle::Continue(true);
    assert!(!continue_true.is_abort());
    let continue_false: Lifecycle = Lifecycle::Continue(false);
    assert!(!continue_false.is_abort());
}

#[tokio::test]
async fn lifecycle_is_keep_alive() {
    let abort_true: Lifecycle = Lifecycle::Abort(true);
    assert!(abort_true.is_keep_alive());
    let abort_false: Lifecycle = Lifecycle::Abort(false);
    assert!(!abort_false.is_keep_alive());
    let continue_true: Lifecycle = Lifecycle::Continue(true);
    assert!(continue_true.is_keep_alive());
    let continue_false: Lifecycle = Lifecycle::Continue(false);
    assert!(!continue_false.is_keep_alive());
}

#[tokio::test]
async fn lifecycle_keep_alive() {
    let abort_true: Lifecycle = Lifecycle::Abort(true);
    assert!(abort_true.keep_alive());
    let abort_false: Lifecycle = Lifecycle::Abort(false);
    assert!(!abort_false.keep_alive());
    let continue_true: Lifecycle = Lifecycle::Continue(true);
    assert!(continue_true.keep_alive());
    let continue_false: Lifecycle = Lifecycle::Continue(false);
    assert!(!continue_false.keep_alive());
}

```

### 📄 File #92 - `mod.rs`
- **Path**: `hyperlane\src\tests\mod.rs`
- **Size**: `110 B`
- **Modified Time**: `2025-09-15T22:37:10.299039`

#### Content Preview

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

### 📄 File #93 - `panic.rs`
- **Path**: `hyperlane\src\tests\panic.rs`
- **Size**: `875 B`
- **Modified Time**: `2025-09-15T22:37:10.299039`

#### Content Preview

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

### 📄 File #94 - `route.rs`
- **Path**: `hyperlane\src\tests\route.rs`
- **Size**: `1,734 B`
- **Modified Time**: `2025-09-15T22:37:10.299039`

#### Content Preview

```rust
use crate::*;

#[cfg(test)]
async fn assert_panic_message_contains<F, Fut>(future_factory: F, expected_msg: &str)
where
    F: Fn() -> Fut + Send + 'static,
    Fut: Future<Output = ()> + Send + 'static,
{
    let result: ResultJoinError<_> = spawn(future_factory()).await;
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
        *s
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

#[tokio::test]
async fn empty_route() {
    assert_panic_message_contains(
        || async {
            let _server: &Server = Server::new()
                .await
                .route(EMPTY_STR, |_| async move {})
                .await;
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
                .route(ROOT_PATH, |_| async move {})
                .await
                .route(ROOT_PATH, |_| async move {})
                .await;
        },
        &RouteError::DuplicatePattern(ROOT_PATH.to_string()).to_string(),
    )
    .await;
}

```

### 📄 File #95 - `send.rs`
- **Path**: `hyperlane\src\tests\send.rs`
- **Size**: `1,533 B`
- **Modified Time**: `2025-09-15T22:37:10.299039`

#### Content Preview

```rust
use crate::*;

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
        .route("/test", |_| async move {})
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
            .route("/test", |_| async move {})
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

### 📄 File #96 - `server.rs`
- **Path**: `hyperlane\src\tests\server.rs`
- **Size**: `5,970 B`
- **Modified Time**: `2025-09-15T22:37:10.299039`

#### Content Preview

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
async fn server() {
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
        let server_hook_clone: ServerHook = server_hook.clone();
        tokio::spawn(async move {
            tokio::time::sleep(std::time::Duration::from_secs(60)).await;
            server_hook.shutdown().await;
        });
        server_hook_clone.wait().await;
    }

    main().await;
}

```

### 📄 File #97 - `.gitignore`
- **Path**: `hyperlane-broadcast\.gitignore`
- **Size**: `18 B`
- **Modified Time**: `2025-09-15T22:37:19.370238`

#### Content Preview



### 📄 File #98 - `Cargo.toml`
- **Path**: `hyperlane-broadcast\Cargo.toml`
- **Size**: `1,128 B`
- **Modified Time**: `2025-09-15T22:37:19.370238`

#### Content Preview



### 📄 File #99 - `LICENSE`
- **Path**: `hyperlane-broadcast\LICENSE`
- **Size**: `1,066 B`
- **Modified Time**: `2025-09-15T22:37:19.370238`

#### Content Preview



### 📄 File #100 - `README.md`
- **Path**: `hyperlane-broadcast\README.md`
- **Size**: `2,406 B`
- **Modified Time**: `2025-09-15T22:37:19.370238`

#### Content Preview

```markdown
<center>

## hyperlane-broadcast

[![](https://img.shields.io/crates/v/hyperlane-broadcast.svg)](https://crates.io/crates/hyperlane-broadcast)
[![](https://img.shields.io/crates/d/hyperlane-broadcast.svg)](https://img.shields.io/crates/d/hyperlane-broadcast.svg)
[![](https://docs.rs/hyperlane-broadcast/badge.svg)](https://docs.rs/hyperlane-broadcast)
[![](https://github.com/hyperlane-dev/hyperlane-broadcast/workflows/Rust/badge.svg)](https://github.com/hyperlane-dev/hyperlane-broadcast/actions?query=workflow:Rust)
[![](https://img.shields.io/crates/l/hyperlane_broadcast.svg)](./LICENSE)

</center>

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

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Contact

For any inquiries, please reach out to the author at [root@ltpp.vip](mailto:root@ltpp.vip).

```

### 📄 File #101 - `config`
- **Path**: `hyperlane-broadcast\.git\config`
- **Size**: `329 B`
- **Modified Time**: `2025-09-15T22:37:19.361731`

#### Content Preview



### 📄 File #102 - `description`
- **Path**: `hyperlane-broadcast\.git\description`
- **Size**: `73 B`
- **Modified Time**: `2025-09-15T22:37:17.377937`

#### Content Preview



### 📄 File #103 - `FETCH_HEAD`
- **Path**: `hyperlane-broadcast\.git\FETCH_HEAD`
- **Size**: `114 B`
- **Modified Time**: `2025-10-01T21:58:41.163589`

#### Content Preview



### 📄 File #104 - `HEAD`
- **Path**: `hyperlane-broadcast\.git\HEAD`
- **Size**: `23 B`
- **Modified Time**: `2025-09-15T22:37:19.350057`

#### Content Preview



### 📄 File #105 - `index`
- **Path**: `hyperlane-broadcast\.git\index`
- **Size**: `1,777 B`
- **Modified Time**: `2025-09-15T22:44:15.549267`

#### Content Preview



### 📄 File #106 - `ORIG_HEAD`
- **Path**: `hyperlane-broadcast\.git\ORIG_HEAD`
- **Size**: `41 B`
- **Modified Time**: `2025-09-15T22:44:17.295684`

#### Content Preview



### 📄 File #107 - `packed-refs`
- **Path**: `hyperlane-broadcast\.git\packed-refs`
- **Size**: `114 B`
- **Modified Time**: `2025-09-15T22:37:19.340000`

#### Content Preview



### 📄 File #108 - `shallow`
- **Path**: `hyperlane-broadcast\.git\shallow`
- **Size**: `41 B`
- **Modified Time**: `2025-09-15T22:37:19.272119`

#### Content Preview



### 📄 File #109 - `applypatch-msg.sample`
- **Path**: `hyperlane-broadcast\.git\hooks\applypatch-msg.sample`
- **Size**: `478 B`
- **Modified Time**: `2025-09-15T22:37:17.377937`

#### Content Preview



### 📄 File #110 - `commit-msg.sample`
- **Path**: `hyperlane-broadcast\.git\hooks\commit-msg.sample`
- **Size**: `896 B`
- **Modified Time**: `2025-09-15T22:37:17.378936`

#### Content Preview



### 📄 File #111 - `fsmonitor-watchman.sample`
- **Path**: `hyperlane-broadcast\.git\hooks\fsmonitor-watchman.sample`
- **Size**: `4,726 B`
- **Modified Time**: `2025-09-15T22:37:17.378936`

#### Content Preview



### 📄 File #112 - `post-update.sample`
- **Path**: `hyperlane-broadcast\.git\hooks\post-update.sample`
- **Size**: `189 B`
- **Modified Time**: `2025-09-15T22:37:17.378936`

#### Content Preview



### 📄 File #113 - `pre-applypatch.sample`
- **Path**: `hyperlane-broadcast\.git\hooks\pre-applypatch.sample`
- **Size**: `424 B`
- **Modified Time**: `2025-09-15T22:37:17.378936`

#### Content Preview



### 📄 File #114 - `pre-commit.sample`
- **Path**: `hyperlane-broadcast\.git\hooks\pre-commit.sample`
- **Size**: `1,649 B`
- **Modified Time**: `2025-09-15T22:37:17.378936`

#### Content Preview



### 📄 File #115 - `pre-merge-commit.sample`
- **Path**: `hyperlane-broadcast\.git\hooks\pre-merge-commit.sample`
- **Size**: `416 B`
- **Modified Time**: `2025-09-15T22:37:17.378936`

#### Content Preview



### 📄 File #116 - `pre-push.sample`
- **Path**: `hyperlane-broadcast\.git\hooks\pre-push.sample`
- **Size**: `1,374 B`
- **Modified Time**: `2025-09-15T22:37:17.379936`

#### Content Preview



### 📄 File #117 - `pre-rebase.sample`
- **Path**: `hyperlane-broadcast\.git\hooks\pre-rebase.sample`
- **Size**: `4,898 B`
- **Modified Time**: `2025-09-15T22:37:17.379936`

#### Content Preview



### 📄 File #118 - `pre-receive.sample`
- **Path**: `hyperlane-broadcast\.git\hooks\pre-receive.sample`
- **Size**: `544 B`
- **Modified Time**: `2025-09-15T22:37:17.379936`

#### Content Preview



### 📄 File #119 - `prepare-commit-msg.sample`
- **Path**: `hyperlane-broadcast\.git\hooks\prepare-commit-msg.sample`
- **Size**: `1,492 B`
- **Modified Time**: `2025-09-15T22:37:17.379936`

#### Content Preview



### 📄 File #120 - `push-to-checkout.sample`
- **Path**: `hyperlane-broadcast\.git\hooks\push-to-checkout.sample`
- **Size**: `2,783 B`
- **Modified Time**: `2025-09-15T22:37:17.379936`

#### Content Preview



### 📄 File #121 - `sendemail-validate.sample`
- **Path**: `hyperlane-broadcast\.git\hooks\sendemail-validate.sample`
- **Size**: `2,308 B`
- **Modified Time**: `2025-09-15T22:37:17.380937`

#### Content Preview



### 📄 File #122 - `update.sample`
- **Path**: `hyperlane-broadcast\.git\hooks\update.sample`
- **Size**: `3,650 B`
- **Modified Time**: `2025-09-15T22:37:17.380937`

#### Content Preview



### 📄 File #123 - `exclude`
- **Path**: `hyperlane-broadcast\.git\info\exclude`
- **Size**: `240 B`
- **Modified Time**: `2025-09-15T22:37:17.380937`

#### Content Preview



### 📄 File #124 - `HEAD`
- **Path**: `hyperlane-broadcast\.git\logs\HEAD`
- **Size**: `194 B`
- **Modified Time**: `2025-09-15T22:37:19.352062`

#### Content Preview



### 📄 File #125 - `master`
- **Path**: `hyperlane-broadcast\.git\logs\refs\heads\master`
- **Size**: `194 B`
- **Modified Time**: `2025-09-15T22:37:19.352062`

#### Content Preview



### 📄 File #126 - `HEAD`
- **Path**: `hyperlane-broadcast\.git\logs\refs\remotes\origin\HEAD`
- **Size**: `194 B`
- **Modified Time**: `2025-09-15T22:37:19.349058`

#### Content Preview



### 📄 File #127 - `pack-f1ebad11ff9bb4a4ecc5c0ba4d30487c50b9b7ff.idx`
- **Path**: `hyperlane-broadcast\.git\objects\pack\pack-f1ebad11ff9bb4a4ecc5c0ba4d30487c50b9b7ff.idx`
- **Size**: `1,772 B`
- **Modified Time**: `2025-09-15T22:37:19.306920`

#### Content Preview



### 📄 File #128 - `pack-f1ebad11ff9bb4a4ecc5c0ba4d30487c50b9b7ff.pack`
- **Path**: `hyperlane-broadcast\.git\objects\pack\pack-f1ebad11ff9bb4a4ecc5c0ba4d30487c50b9b7ff.pack`
- **Size**: `10,052 B`
- **Modified Time**: `2025-09-15T22:37:19.306920`

#### Content Preview



### 📄 File #129 - `pack-f1ebad11ff9bb4a4ecc5c0ba4d30487c50b9b7ff.rev`
- **Path**: `hyperlane-broadcast\.git\objects\pack\pack-f1ebad11ff9bb4a4ecc5c0ba4d30487c50b9b7ff.rev`
- **Size**: `152 B`
- **Modified Time**: `2025-09-15T22:37:19.307947`

#### Content Preview



### 📄 File #130 - `master`
- **Path**: `hyperlane-broadcast\.git\refs\heads\master`
- **Size**: `41 B`
- **Modified Time**: `2025-09-15T22:37:19.351059`

#### Content Preview



### 📄 File #131 - `HEAD`
- **Path**: `hyperlane-broadcast\.git\refs\remotes\origin\HEAD`
- **Size**: `32 B`
- **Modified Time**: `2025-09-15T22:37:19.348058`

#### Content Preview



### 📄 File #132 - `v0.8.0`
- **Path**: `hyperlane-broadcast\.git\refs\tags\v0.8.0`
- **Size**: `41 B`
- **Modified Time**: `2025-09-15T22:37:19.347042`

#### Content Preview



### 📄 File #133 - `rust.yml`
- **Path**: `hyperlane-broadcast\.github\workflows\rust.yml`
- **Size**: `9,636 B`
- **Modified Time**: `2025-09-15T22:37:19.370238`

#### Content Preview

```yaml
name: Rust
on:
  push:
    branches: [master]
env:
  CARGO_TERM_COLOR: always
jobs:
  setup:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.read.outputs.version }}
      tag: ${{ steps.read.outputs.tag }}
      package_name: ${{ steps.read.outputs.package_name }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Install rust-toolchain
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
          components: rustfmt, clippy
      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: |
            ~/.cargo/registry
            ~/.cargo/git
            target
          key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}
      - name: Install toml-cli
        run: cargo install toml-cli
      - name: Cache toml-cli
        uses: actions/cache@v3
        with:
          path: ~/.cargo/bin/toml
          key: toml-cli-${{ runner.os }}
      - name: Read cargo metadata
        id: read
        run: |
          VERSION=$(toml get Cargo.toml package.version --raw)
          PACKAGE_NAME=$(toml get Cargo.toml package.name --raw)
          echo "📦 Detected package: $PACKAGE_NAME v$VERSION"
          if [ -z "$VERSION" ] || [ -z "$PACKAGE_NAME" ]; then
            echo "❌ Failed to read package info from Cargo.toml"
          fi
          echo "version=$VERSION" >> $GITHUB_OUTPUT
          echo "tag=v$VERSION" >> $GITHUB_OUTPUT
          echo "package_name=$PACKAGE_NAME" >> $GITHUB_OUTPUT

  check:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup rust
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
          components: rustfmt
      - name: Format check
        run: cargo fmt -- --check

  tests:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Prepare environment
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
      - name: Run tests
        run: cargo test --all-features -- --nocapture

  clippy:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Load clippy
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
          components: clippy
      - name: Run clippy
        run: cargo clippy --all-features -- -A warnings

  build:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup build
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
      - name: Build release
        run: cargo check --release --all-features

  publish:
    needs: [setup, check, tests, clippy, build]
    if: needs.setup.outputs.tag != ''
    runs-on: ubuntu-latest
    outputs:
      published: ${{ steps.publish.outputs.published }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Restore toml-cli
        uses: actions/cache@v3
        with:
          path: ~/.cargo/bin/toml
          key: toml-cli-${{ runner.os }}
      - name: Publish to crates.io
        id: publish
        env:
          CARGO_REGISTRY_TOKEN: ${{ secrets.CARGO_REGISTRY_TOKEN }}
        run: |
          set -e
          echo "published=false" >> $GITHUB_OUTPUT
          echo "${{ secrets.CARGO_REGISTRY_TOKEN }}" | cargo login
          PACKAGE_NAME=$(toml get Cargo.toml package.name --raw)
          VERSION=${{ needs.setup.outputs.version }}
          if cargo publish --allow-dirty; then
            echo "published=true" >> $GITHUB_OUTPUT
            echo "🎉🎉🎉 PUBLISH SUCCESSFUL 🎉🎉🎉"
            echo "✅ Successfully published $PACKAGE_NAME v$VERSION to crates.io"
            echo "📦 Crates.io: [https://crates.io/crates/$PACKAGE_NAME/$VERSION](https://crates.io/crates/$PACKAGE_NAME/$VERSION)"
            echo "📚 Docs.rs: [https://docs.rs/$PACKAGE_NAME/$VERSION](https://docs.rs/$PACKAGE_NAME/$VERSION)"
          else
            echo "❌ Publish failed"
          fi

  release:
    needs: [setup, check, tests, clippy, build]
    permissions:
      contents: write
      packages: write
    if: needs.setup.outputs.tag != ''
    runs-on: ubuntu-latest
    outputs:
      released: ${{ steps.release.outputs.released }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Get package name
        id: package_info
        run: |
          echo "package_name=${{ needs.setup.outputs.package_name }}" >> $GITHUB_OUTPUT
      - name: Check tag status
        id: check_tag
        run: |
          if git tag -l | grep -q "^${{ needs.setup.outputs.tag }}$"; then
            echo "tag_exists=true" >> $GITHUB_OUTPUT
            echo "🏷️ Tag ${{ needs.setup.outputs.tag }} exists locally"
          else
            echo "tag_exists=false" >> $GITHUB_OUTPUT
            echo "🏷️ Tag ${{ needs.setup.outputs.tag }} does not exist locally"
          fi
          if git ls-remote --tags origin | grep -q "refs/tags/${{ needs.setup.outputs.tag }}$"; then
            echo "remote_tag_exists=true" >> $GITHUB_OUTPUT
            echo "🌐 Tag ${{ needs.setup.outputs.tag }} exists on remote"
          else
            echo "remote_tag_exists=false" >> $GITHUB_OUTPUT
            echo "🌐 Tag ${{ needs.setup.outputs.tag }} does not exist on remote"
          fi
      - name: Check release status
        id: check_release
        run: |
          if gh release view "${{ needs.setup.outputs.tag }}" > /dev/null 2>&1; then
            echo "release_exists=true" >> $GITHUB_OUTPUT
            echo "📦 Release ${{ needs.setup.outputs.tag }} already exists"
          else
            echo "release_exists=false" >> $GITHUB_OUTPUT
            echo "📦 Release ${{ needs.setup.outputs.tag }} does not exist"
          fi
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - name: Create or update release
        id: release
        run: |
          set -e
          echo "released=false" >> $GITHUB_OUTPUT
          PACKAGE_NAME="${{ steps.package_info.outputs.package_name }}"
          VERSION="${{ needs.setup.outputs.version }}"
          TAG="${{ needs.setup.outputs.tag }}"
          echo "📦 Building source archives..."
          git archive --format=zip --prefix="${PACKAGE_NAME}-${VERSION}/" HEAD > "${PACKAGE_NAME}-${VERSION}.zip"
          git archive --format=tar.gz --prefix="${PACKAGE_NAME}-${VERSION}/" HEAD > "${PACKAGE_NAME}-${VERSION}.tar.gz"
          if [ "${{ steps.check_release.outputs.release_exists }}" = "true" ]; then
            echo "🔄 Updating existing release: $TAG"
            gh release view "$TAG" --json assets --jq '.assets[].name' | while read asset; do
              if [ -n "$asset" ]; then
                echo "🗑️ Deleting asset: $asset"
                gh release delete-asset "$TAG" "$asset" --yes || true
              fi
            done
            if gh release edit "$TAG" \
              --title "$TAG (Updated $(date '+%Y-%m-%d %H:%M:%S'))" \
              --notes "Release $TAG - Updated at $(date '+%Y-%m-%d %H:%M:%S UTC')
            ## Changes
            - Version: $VERSION
            - Package: $PACKAGE_NAME
            ## Links
            📦 [Crate on crates.io](https://crates.io/crates/$PACKAGE_NAME/$VERSION)
            📚 [Documentation on docs.rs](https://docs.rs/$PACKAGE_NAME/$VERSION)
            📋 [Commit History](https://github.com/${{ github.repository }}/commits/$TAG)" && \
               gh release upload "$TAG" "${PACKAGE_NAME}-${VERSION}.zip" "${PACKAGE_NAME}-${VERSION}.tar.gz" --clobber; then
              echo "released=true" >> $GITHUB_OUTPUT
              echo "✅ Updated release $TAG"
              echo "🔖 Tag: $TAG"
              echo "🚀 Release: [GitHub Release](${{ github.server_url }}/${{ github.repository }}/releases/tag/$TAG)"
            else
              echo "❌ Failed to update release"
            fi
          else
            if [ "${{ steps.check_tag.outputs.remote_tag_exists }}" = "false" ]; then
              echo "🏷️ Creating and pushing tag: $TAG"
              git tag "$TAG"
              git push origin "$TAG"
            fi
            echo "🆕 Creating new release: $TAG"
            if gh release create "$TAG" \
              --title "$TAG (Created $(date '+%Y-%m-%d %H:%M:%S'))" \
              --notes "Release $TAG - Created at $(date '+%Y-%m-%d %H:%M:%S UTC')
            ## Changes
            - Version: $VERSION
            - Package: $PACKAGE_NAME
            ## Links
            📦 [Crate on crates.io](https://crates.io/crates/$PACKAGE_NAME/$VERSION)
            📚 [Documentation on docs.rs](https://docs.rs/$PACKAGE_NAME/$VERSION)
            📋 [Commit History](https://github.com/${{ github.repository }}/commits/$TAG)" \
              --latest && \
               gh release upload "$TAG" "${PACKAGE_NAME}-${VERSION}.zip" "${PACKAGE_NAME}-${VERSION}.tar.gz"; then
              echo "released=true" >> $GITHUB_OUTPUT
              echo "✅ Created release $TAG"
              echo "🔖 Tag: $TAG"
              echo "🚀 Release: [GitHub Release](${{ github.server_url }}/${{ github.repository }}/releases/tag/$TAG)"
            else
              echo "❌ Failed to create release"
            fi
          fi
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

```

### 📄 File #134 - `cfg.rs`
- **Path**: `hyperlane-broadcast\src\cfg.rs`
- **Size**: `1,073 B`
- **Modified Time**: `2025-09-15T22:37:19.373238`

#### Content Preview

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

### 📄 File #135 - `lib.rs`
- **Path**: `hyperlane-broadcast\src\lib.rs`
- **Size**: `808 B`
- **Modified Time**: `2025-09-15T22:37:19.373238`

#### Content Preview

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

### 📄 File #136 - `const.rs`
- **Path**: `hyperlane-broadcast\src\broadcast\const.rs`
- **Size**: `244 B`
- **Modified Time**: `2025-09-15T22:37:19.371238`

#### Content Preview

```rust
/// Defines the default capacity for a broadcast sender.
///
/// This constant specifies the initial buffer size for messages awaiting delivery
/// to receivers in a broadcast channel.
pub const DEFAULT_BROADCAST_SENDER_CAPACITY: usize = 1024;

```

### 📄 File #137 - `impl.rs`
- **Path**: `hyperlane-broadcast\src\broadcast\impl.rs`
- **Size**: `2,413 B`
- **Modified Time**: `2025-09-15T22:37:19.371238`

#### Content Preview

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
    fn default() -> Self {
        let sender: BroadcastSender<T> = BroadcastSender::new(DEFAULT_BROADCAST_SENDER_CAPACITY);
        Broadcast {
            capacity: 0,
            sender,
        }
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
    pub fn new(capacity: Capacity) -> Self {
        let sender: BroadcastSender<T> = BroadcastSender::new(capacity);
        let mut broadcast: Broadcast<T> = Broadcast::default();
        broadcast.sender = sender;
        broadcast.capacity = capacity;
        broadcast
    }

    /// Retrieves the current number of active receivers subscribed to this broadcast channel.
    ///
    /// # Returns
    ///
    /// - `ReceiverCount` - The total count of active receivers.
    pub fn receiver_count(&self) -> ReceiverCount {
        self.sender.receiver_count()
    }

    /// Subscribes a new receiver to the broadcast channel.
    ///
    /// # Returns
    ///
    /// - `BroadcastReceiver<T>` - A new receiver instance.
    pub fn subscribe(&self) -> BroadcastReceiver<T> {
        self.sender.subscribe()
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
    pub fn send(&self, data: T) -> BroadcastSendResult<T> {
        self.sender.send(data)
    }
}

```

### 📄 File #138 - `mod.rs`
- **Path**: `hyperlane-broadcast\src\broadcast\mod.rs`
- **Size**: `84 B`
- **Modified Time**: `2025-09-15T22:37:19.371238`

#### Content Preview

```rust
pub mod r#const;
pub mod r#impl;
pub mod r#struct;
pub mod r#trait;
pub mod r#type;

```

### 📄 File #139 - `struct.rs`
- **Path**: `hyperlane-broadcast\src\broadcast\struct.rs`
- **Size**: `612 B`
- **Modified Time**: `2025-09-15T22:37:19.371238`

#### Content Preview

```rust
use crate::*;

/// Represents a broadcast mechanism for sending messages to multiple receivers.
///
/// This struct encapsulates the core components required for broadcasting,
/// including the capacity of the broadcast channel and the sender responsible
/// for dispatching messages.
#[derive(Debug, Clone)]
pub struct Broadcast<T: BroadcastTrait> {
    /// The maximum number of messages that can be buffered in the broadcast channel.
    pub(super) capacity: Capacity,
    /// The sender component responsible for distributing messages to all connected receivers.
    pub(super) sender: BroadcastSender<T>,
}

```

### 📄 File #140 - `trait.rs`
- **Path**: `hyperlane-broadcast\src\broadcast\trait.rs`
- **Size**: `299 B`
- **Modified Time**: `2025-09-15T22:37:19.371238`

#### Content Preview

```rust
use crate::*;

/// Defines the essential traits required for types that can be broadcast.
///
/// Any type implementing `BroadcastTrait` must also implement `Clone` and `Debug`,
/// enabling efficient duplication and debugging within the broadcast system.
pub trait BroadcastTrait: Clone + Debug {}

```

### 📄 File #141 - `type.rs`
- **Path**: `hyperlane-broadcast\src\broadcast\type.rs`
- **Size**: `872 B`
- **Modified Time**: `2025-09-15T22:37:19.372237`

#### Content Preview

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

### 📄 File #142 - `impl.rs`
- **Path**: `hyperlane-broadcast\src\broadcast_map\impl.rs`
- **Size**: `4,680 B`
- **Modified Time**: `2025-09-15T22:37:19.372237`

#### Content Preview

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
    pub fn send<K: AsRef<str>>(&self, key: K, data: T) -> BroadcastMapSendResult<T>
    where
        K: AsRef<str>,
    {
        match self.get().get(key.as_ref()) {
            Some(sender) => sender.send(data).map(|result| Some(result)),
            None => Ok(None),
        }
    }
}

```

### 📄 File #143 - `mod.rs`
- **Path**: `hyperlane-broadcast\src\broadcast_map\mod.rs`
- **Size**: `67 B`
- **Modified Time**: `2025-09-15T22:37:19.372237`

#### Content Preview

```rust
pub mod r#impl;
pub mod r#struct;
pub mod r#trait;
pub mod r#type;

```

### 📄 File #144 - `struct.rs`
- **Path**: `hyperlane-broadcast\src\broadcast_map\struct.rs`
- **Size**: `399 B`
- **Modified Time**: `2025-09-15T22:37:19.372237`

#### Content Preview

```rust
use crate::*;

/// Represents a concurrent, thread-safe map of broadcast channels, keyed by string.
///
/// This struct provides a way to manage multiple broadcast channels, each identified by a unique string,
/// allowing for dynamic creation, retrieval, and management of broadcast streams.
#[derive(Debug, Clone)]
pub struct BroadcastMap<T: BroadcastTrait>(pub(super) DashMapStringBroadcast<T>);

```

### 📄 File #145 - `trait.rs`
- **Path**: `hyperlane-broadcast\src\broadcast_map\trait.rs`
- **Size**: `334 B`
- **Modified Time**: `2025-09-15T22:37:19.372237`

#### Content Preview

```rust
use crate::*;

/// Defines the essential traits required for types that can be used as values in a `BroadcastMap`.
///
/// Any type implementing `BroadcastMapTrait` must also implement `Clone` and `Debug`,
/// enabling efficient duplication and debugging within the broadcast map system.
pub trait BroadcastMapTrait: Clone + Debug {}

```

### 📄 File #146 - `type.rs`
- **Path**: `hyperlane-broadcast\src\broadcast_map\type.rs`
- **Size**: `1,414 B`
- **Modified Time**: `2025-09-15T22:37:19.372237`

#### Content Preview

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

### 📄 File #147 - `.gitignore`
- **Path**: `hyperlane-log\.gitignore`
- **Size**: `30 B`
- **Modified Time**: `2025-09-15T22:37:12.927907`

#### Content Preview



### 📄 File #148 - `Cargo.toml`
- **Path**: `hyperlane-log\Cargo.toml`
- **Size**: `1,517 B`
- **Modified Time**: `2025-09-15T22:37:12.927907`

#### Content Preview



### 📄 File #149 - `LICENSE`
- **Path**: `hyperlane-log\LICENSE`
- **Size**: `1,066 B`
- **Modified Time**: `2025-09-15T22:37:12.927907`

#### Content Preview



### 📄 File #150 - `README.md`
- **Path**: `hyperlane-log\README.md`
- **Size**: `4,066 B`
- **Modified Time**: `2025-09-15T22:37:12.928908`

#### Content Preview

```markdown
<center>

## hyperlane-log

[![](https://img.shields.io/crates/v/hyperlane-log.svg)](https://crates.io/crates/hyperlane-log)
[![](https://img.shields.io/crates/d/hyperlane-log.svg)](https://img.shields.io/crates/d/hyperlane-log.svg)
[![](https://docs.rs/hyperlane-log/badge.svg)](https://docs.rs/hyperlane-log)
[![](https://github.com/hyperlane-dev/hyperlane-log/workflows/Rust/badge.svg)](https://github.com/hyperlane-dev/hyperlane-log/actions?query=workflow:Rust)
[![](https://img.shields.io/crates/l/hyperlane-log.svg)](./LICENSE)

</center>

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

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Contact

For any inquiries, please reach out to the author at [root@ltpp.vip](mailto:root@ltpp.vip).

```

### 📄 File #151 - `config`
- **Path**: `hyperlane-log\.git\config`
- **Size**: `323 B`
- **Modified Time**: `2025-09-15T22:37:12.921397`

#### Content Preview



### 📄 File #152 - `description`
- **Path**: `hyperlane-log\.git\description`
- **Size**: `73 B`
- **Modified Time**: `2025-09-15T22:37:10.337892`

#### Content Preview



### 📄 File #153 - `FETCH_HEAD`
- **Path**: `hyperlane-log\.git\FETCH_HEAD`
- **Size**: `0 B`
- **Modified Time**: `2025-10-01T21:58:27.561776`

#### Content Preview



### 📄 File #154 - `HEAD`
- **Path**: `hyperlane-log\.git\HEAD`
- **Size**: `23 B`
- **Modified Time**: `2025-09-15T22:37:12.912397`

#### Content Preview



### 📄 File #155 - `index`
- **Path**: `hyperlane-log\.git\index`
- **Size**: `1,308 B`
- **Modified Time**: `2025-09-15T22:44:07.189926`

#### Content Preview



### 📄 File #156 - `ORIG_HEAD`
- **Path**: `hyperlane-log\.git\ORIG_HEAD`
- **Size**: `41 B`
- **Modified Time**: `2025-09-15T22:44:11.290119`

#### Content Preview



### 📄 File #157 - `packed-refs`
- **Path**: `hyperlane-log\.git\packed-refs`
- **Size**: `114 B`
- **Modified Time**: `2025-09-15T22:37:12.902397`

#### Content Preview



### 📄 File #158 - `shallow`
- **Path**: `hyperlane-log\.git\shallow`
- **Size**: `41 B`
- **Modified Time**: `2025-09-15T22:37:12.765583`

#### Content Preview



### 📄 File #159 - `applypatch-msg.sample`
- **Path**: `hyperlane-log\.git\hooks\applypatch-msg.sample`
- **Size**: `478 B`
- **Modified Time**: `2025-09-15T22:37:10.338892`

#### Content Preview



### 📄 File #160 - `commit-msg.sample`
- **Path**: `hyperlane-log\.git\hooks\commit-msg.sample`
- **Size**: `896 B`
- **Modified Time**: `2025-09-15T22:37:10.338892`

#### Content Preview



### 📄 File #161 - `fsmonitor-watchman.sample`
- **Path**: `hyperlane-log\.git\hooks\fsmonitor-watchman.sample`
- **Size**: `4,726 B`
- **Modified Time**: `2025-09-15T22:37:10.338892`

#### Content Preview



### 📄 File #162 - `post-update.sample`
- **Path**: `hyperlane-log\.git\hooks\post-update.sample`
- **Size**: `189 B`
- **Modified Time**: `2025-09-15T22:37:10.338892`

#### Content Preview



### 📄 File #163 - `pre-applypatch.sample`
- **Path**: `hyperlane-log\.git\hooks\pre-applypatch.sample`
- **Size**: `424 B`
- **Modified Time**: `2025-09-15T22:37:10.338892`

#### Content Preview



### 📄 File #164 - `pre-commit.sample`
- **Path**: `hyperlane-log\.git\hooks\pre-commit.sample`
- **Size**: `1,649 B`
- **Modified Time**: `2025-09-15T22:37:10.338892`

#### Content Preview



### 📄 File #165 - `pre-merge-commit.sample`
- **Path**: `hyperlane-log\.git\hooks\pre-merge-commit.sample`
- **Size**: `416 B`
- **Modified Time**: `2025-09-15T22:37:10.339891`

#### Content Preview



### 📄 File #166 - `pre-push.sample`
- **Path**: `hyperlane-log\.git\hooks\pre-push.sample`
- **Size**: `1,374 B`
- **Modified Time**: `2025-09-15T22:37:10.339891`

#### Content Preview



### 📄 File #167 - `pre-rebase.sample`
- **Path**: `hyperlane-log\.git\hooks\pre-rebase.sample`
- **Size**: `4,898 B`
- **Modified Time**: `2025-09-15T22:37:10.339891`

#### Content Preview



### 📄 File #168 - `pre-receive.sample`
- **Path**: `hyperlane-log\.git\hooks\pre-receive.sample`
- **Size**: `544 B`
- **Modified Time**: `2025-09-15T22:37:10.339891`

#### Content Preview



### 📄 File #169 - `prepare-commit-msg.sample`
- **Path**: `hyperlane-log\.git\hooks\prepare-commit-msg.sample`
- **Size**: `1,492 B`
- **Modified Time**: `2025-09-15T22:37:10.339891`

#### Content Preview



### 📄 File #170 - `push-to-checkout.sample`
- **Path**: `hyperlane-log\.git\hooks\push-to-checkout.sample`
- **Size**: `2,783 B`
- **Modified Time**: `2025-09-15T22:37:10.339891`

#### Content Preview



### 📄 File #171 - `sendemail-validate.sample`
- **Path**: `hyperlane-log\.git\hooks\sendemail-validate.sample`
- **Size**: `2,308 B`
- **Modified Time**: `2025-09-15T22:37:10.340891`

#### Content Preview



### 📄 File #172 - `update.sample`
- **Path**: `hyperlane-log\.git\hooks\update.sample`
- **Size**: `3,650 B`
- **Modified Time**: `2025-09-15T22:37:10.340891`

#### Content Preview



### 📄 File #173 - `exclude`
- **Path**: `hyperlane-log\.git\info\exclude`
- **Size**: `240 B`
- **Modified Time**: `2025-09-15T22:37:10.340891`

#### Content Preview



### 📄 File #174 - `HEAD`
- **Path**: `hyperlane-log\.git\logs\HEAD`
- **Size**: `188 B`
- **Modified Time**: `2025-09-15T22:37:12.914397`

#### Content Preview



### 📄 File #175 - `master`
- **Path**: `hyperlane-log\.git\logs\refs\heads\master`
- **Size**: `188 B`
- **Modified Time**: `2025-09-15T22:37:12.914397`

#### Content Preview



### 📄 File #176 - `HEAD`
- **Path**: `hyperlane-log\.git\logs\refs\remotes\origin\HEAD`
- **Size**: `188 B`
- **Modified Time**: `2025-09-15T22:37:12.912397`

#### Content Preview



### 📄 File #177 - `pack-8288281cadf0897a7078f431aa6915caf1801a01.idx`
- **Path**: `hyperlane-log\.git\objects\pack\pack-8288281cadf0897a7078f431aa6915caf1801a01.idx`
- **Size**: `1,632 B`
- **Modified Time**: `2025-09-15T22:37:12.868651`

#### Content Preview



### 📄 File #178 - `pack-8288281cadf0897a7078f431aa6915caf1801a01.pack`
- **Path**: `hyperlane-log\.git\objects\pack\pack-8288281cadf0897a7078f431aa6915caf1801a01.pack`
- **Size**: `10,203 B`
- **Modified Time**: `2025-09-15T22:37:12.868651`

#### Content Preview



### 📄 File #179 - `pack-8288281cadf0897a7078f431aa6915caf1801a01.rev`
- **Path**: `hyperlane-log\.git\objects\pack\pack-8288281cadf0897a7078f431aa6915caf1801a01.rev`
- **Size**: `132 B`
- **Modified Time**: `2025-09-15T22:37:12.869652`

#### Content Preview



### 📄 File #180 - `master`
- **Path**: `hyperlane-log\.git\refs\heads\master`
- **Size**: `41 B`
- **Modified Time**: `2025-09-15T22:37:12.914397`

#### Content Preview



### 📄 File #181 - `HEAD`
- **Path**: `hyperlane-log\.git\refs\remotes\origin\HEAD`
- **Size**: `32 B`
- **Modified Time**: `2025-09-15T22:37:12.911397`

#### Content Preview



### 📄 File #182 - `v1.19.0`
- **Path**: `hyperlane-log\.git\refs\tags\v1.19.0`
- **Size**: `41 B`
- **Modified Time**: `2025-09-15T22:37:12.909397`

#### Content Preview



### 📄 File #183 - `rust.yml`
- **Path**: `hyperlane-log\.github\workflows\rust.yml`
- **Size**: `9,636 B`
- **Modified Time**: `2025-09-15T22:37:12.927907`

#### Content Preview

```yaml
name: Rust
on:
  push:
    branches: [master]
env:
  CARGO_TERM_COLOR: always
jobs:
  setup:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.read.outputs.version }}
      tag: ${{ steps.read.outputs.tag }}
      package_name: ${{ steps.read.outputs.package_name }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Install rust-toolchain
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
          components: rustfmt, clippy
      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: |
            ~/.cargo/registry
            ~/.cargo/git
            target
          key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}
      - name: Install toml-cli
        run: cargo install toml-cli
      - name: Cache toml-cli
        uses: actions/cache@v3
        with:
          path: ~/.cargo/bin/toml
          key: toml-cli-${{ runner.os }}
      - name: Read cargo metadata
        id: read
        run: |
          VERSION=$(toml get Cargo.toml package.version --raw)
          PACKAGE_NAME=$(toml get Cargo.toml package.name --raw)
          echo "📦 Detected package: $PACKAGE_NAME v$VERSION"
          if [ -z "$VERSION" ] || [ -z "$PACKAGE_NAME" ]; then
            echo "❌ Failed to read package info from Cargo.toml"
          fi
          echo "version=$VERSION" >> $GITHUB_OUTPUT
          echo "tag=v$VERSION" >> $GITHUB_OUTPUT
          echo "package_name=$PACKAGE_NAME" >> $GITHUB_OUTPUT

  check:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup rust
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
          components: rustfmt
      - name: Format check
        run: cargo fmt -- --check

  tests:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Prepare environment
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
      - name: Run tests
        run: cargo test --all-features -- --nocapture

  clippy:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Load clippy
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
          components: clippy
      - name: Run clippy
        run: cargo clippy --all-features -- -A warnings

  build:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup build
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
      - name: Build release
        run: cargo check --release --all-features

  publish:
    needs: [setup, check, tests, clippy, build]
    if: needs.setup.outputs.tag != ''
    runs-on: ubuntu-latest
    outputs:
      published: ${{ steps.publish.outputs.published }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Restore toml-cli
        uses: actions/cache@v3
        with:
          path: ~/.cargo/bin/toml
          key: toml-cli-${{ runner.os }}
      - name: Publish to crates.io
        id: publish
        env:
          CARGO_REGISTRY_TOKEN: ${{ secrets.CARGO_REGISTRY_TOKEN }}
        run: |
          set -e
          echo "published=false" >> $GITHUB_OUTPUT
          echo "${{ secrets.CARGO_REGISTRY_TOKEN }}" | cargo login
          PACKAGE_NAME=$(toml get Cargo.toml package.name --raw)
          VERSION=${{ needs.setup.outputs.version }}
          if cargo publish --allow-dirty; then
            echo "published=true" >> $GITHUB_OUTPUT
            echo "🎉🎉🎉 PUBLISH SUCCESSFUL 🎉🎉🎉"
            echo "✅ Successfully published $PACKAGE_NAME v$VERSION to crates.io"
            echo "📦 Crates.io: [https://crates.io/crates/$PACKAGE_NAME/$VERSION](https://crates.io/crates/$PACKAGE_NAME/$VERSION)"
            echo "📚 Docs.rs: [https://docs.rs/$PACKAGE_NAME/$VERSION](https://docs.rs/$PACKAGE_NAME/$VERSION)"
          else
            echo "❌ Publish failed"
          fi

  release:
    needs: [setup, check, tests, clippy, build]
    permissions:
      contents: write
      packages: write
    if: needs.setup.outputs.tag != ''
    runs-on: ubuntu-latest
    outputs:
      released: ${{ steps.release.outputs.released }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Get package name
        id: package_info
        run: |
          echo "package_name=${{ needs.setup.outputs.package_name }}" >> $GITHUB_OUTPUT
      - name: Check tag status
        id: check_tag
        run: |
          if git tag -l | grep -q "^${{ needs.setup.outputs.tag }}$"; then
            echo "tag_exists=true" >> $GITHUB_OUTPUT
            echo "🏷️ Tag ${{ needs.setup.outputs.tag }} exists locally"
          else
            echo "tag_exists=false" >> $GITHUB_OUTPUT
            echo "🏷️ Tag ${{ needs.setup.outputs.tag }} does not exist locally"
          fi
          if git ls-remote --tags origin | grep -q "refs/tags/${{ needs.setup.outputs.tag }}$"; then
            echo "remote_tag_exists=true" >> $GITHUB_OUTPUT
            echo "🌐 Tag ${{ needs.setup.outputs.tag }} exists on remote"
          else
            echo "remote_tag_exists=false" >> $GITHUB_OUTPUT
            echo "🌐 Tag ${{ needs.setup.outputs.tag }} does not exist on remote"
          fi
      - name: Check release status
        id: check_release
        run: |
          if gh release view "${{ needs.setup.outputs.tag }}" > /dev/null 2>&1; then
            echo "release_exists=true" >> $GITHUB_OUTPUT
            echo "📦 Release ${{ needs.setup.outputs.tag }} already exists"
          else
            echo "release_exists=false" >> $GITHUB_OUTPUT
            echo "📦 Release ${{ needs.setup.outputs.tag }} does not exist"
          fi
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - name: Create or update release
        id: release
        run: |
          set -e
          echo "released=false" >> $GITHUB_OUTPUT
          PACKAGE_NAME="${{ steps.package_info.outputs.package_name }}"
          VERSION="${{ needs.setup.outputs.version }}"
          TAG="${{ needs.setup.outputs.tag }}"
          echo "📦 Building source archives..."
          git archive --format=zip --prefix="${PACKAGE_NAME}-${VERSION}/" HEAD > "${PACKAGE_NAME}-${VERSION}.zip"
          git archive --format=tar.gz --prefix="${PACKAGE_NAME}-${VERSION}/" HEAD > "${PACKAGE_NAME}-${VERSION}.tar.gz"
          if [ "${{ steps.check_release.outputs.release_exists }}" = "true" ]; then
            echo "🔄 Updating existing release: $TAG"
            gh release view "$TAG" --json assets --jq '.assets[].name' | while read asset; do
              if [ -n "$asset" ]; then
                echo "🗑️ Deleting asset: $asset"
                gh release delete-asset "$TAG" "$asset" --yes || true
              fi
            done
            if gh release edit "$TAG" \
              --title "$TAG (Updated $(date '+%Y-%m-%d %H:%M:%S'))" \
              --notes "Release $TAG - Updated at $(date '+%Y-%m-%d %H:%M:%S UTC')
            ## Changes
            - Version: $VERSION
            - Package: $PACKAGE_NAME
            ## Links
            📦 [Crate on crates.io](https://crates.io/crates/$PACKAGE_NAME/$VERSION)
            📚 [Documentation on docs.rs](https://docs.rs/$PACKAGE_NAME/$VERSION)
            📋 [Commit History](https://github.com/${{ github.repository }}/commits/$TAG)" && \
               gh release upload "$TAG" "${PACKAGE_NAME}-${VERSION}.zip" "${PACKAGE_NAME}-${VERSION}.tar.gz" --clobber; then
              echo "released=true" >> $GITHUB_OUTPUT
              echo "✅ Updated release $TAG"
              echo "🔖 Tag: $TAG"
              echo "🚀 Release: [GitHub Release](${{ github.server_url }}/${{ github.repository }}/releases/tag/$TAG)"
            else
              echo "❌ Failed to update release"
            fi
          else
            if [ "${{ steps.check_tag.outputs.remote_tag_exists }}" = "false" ]; then
              echo "🏷️ Creating and pushing tag: $TAG"
              git tag "$TAG"
              git push origin "$TAG"
            fi
            echo "🆕 Creating new release: $TAG"
            if gh release create "$TAG" \
              --title "$TAG (Created $(date '+%Y-%m-%d %H:%M:%S'))" \
              --notes "Release $TAG - Created at $(date '+%Y-%m-%d %H:%M:%S UTC')
            ## Changes
            - Version: $VERSION
            - Package: $PACKAGE_NAME
            ## Links
            📦 [Crate on crates.io](https://crates.io/crates/$PACKAGE_NAME/$VERSION)
            📚 [Documentation on docs.rs](https://docs.rs/$PACKAGE_NAME/$VERSION)
            📋 [Commit History](https://github.com/${{ github.repository }}/commits/$TAG)" \
              --latest && \
               gh release upload "$TAG" "${PACKAGE_NAME}-${VERSION}.zip" "${PACKAGE_NAME}-${VERSION}.tar.gz"; then
              echo "released=true" >> $GITHUB_OUTPUT
              echo "✅ Created release $TAG"
              echo "🔖 Tag: $TAG"
              echo "🚀 Release: [GitHub Release](${{ github.server_url }}/${{ github.repository }}/releases/tag/$TAG)"
            else
              echo "❌ Failed to create release"
            fi
          fi
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

```

### 📄 File #184 - `cfg.rs`
- **Path**: `hyperlane-log\src\cfg.rs`
- **Size**: `2,808 B`
- **Modified Time**: `2025-09-15T22:37:12.928908`

#### Content Preview

```rust
#[cfg(test)]
#[tokio::test]
async fn test() {
    use crate::*;
    let log: Log = Log::new("./logs", 1_024_000);
    let error_str: String = String::from("custom error message");
    log.error(error_str, |error| {
        let write_data: String = format!("User error func => {:?}\n", error);
        write_data
    });
    let info_str: String = String::from("custom info message");
    log.info(info_str, |info| {
        let write_data: String = format!("User info func => {:?}\n", info);
        write_data
    });
    let debug_str: String = String::from("custom debug message");
    log.debug(debug_str, |debug| {
        let write_data: String = format!("User debug func => {:#?}\n", debug);
        write_data
    });
    let async_error_str: String = String::from("custom async error message");
    log.async_error(async_error_str, |error| {
        let write_data: String = format!("User error func => {:?}\n", error);
        write_data
    })
    .await;
    let async_info_str: String = String::from("custom async info message");
    log.async_info(async_info_str, |info| {
        let write_data: String = format!("User info func => {:?}\n", info);
        write_data
    })
    .await;
    let async_debug_str: String = String::from("custom async debug message");
    log.async_debug(async_debug_str, |debug| {
        let write_data: String = format!("User debug func => {:#?}\n", debug);
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
        let write_data: String = format!("User error func => {:?}\n", error);
        write_data
    });
    log.info("info data => ", |info| {
        let write_data: String = format!("User info func => {:?}\n", info);
        write_data
    });
    log.debug("debug data => ", |debug| {
        let write_data: String = format!("User debug func => {:#?}\n", debug);
        write_data
    });
    log.async_error("async error data => ", |error| {
        let write_data: String = format!("User error func => {:?}\n", error);
        write_data
    })
    .await;
    log.async_info("async info data => ", |info| {
        let write_data: String = format!("User info func => {:?}\n", info);
        write_data
    })
    .await;
    log.async_debug("async debug data => ", |debug| {
        let write_data: String = format!("User debug func => {:#?}\n", debug);
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

### 📄 File #185 - `lib.rs`
- **Path**: `hyperlane-log\src\lib.rs`
- **Size**: `918 B`
- **Modified Time**: `2025-09-15T22:37:12.928908`

#### Content Preview

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

### 📄 File #186 - `const.rs`
- **Path**: `hyperlane-log\src\log\const.rs`
- **Size**: `871 B`
- **Modified Time**: `2025-09-15T22:37:12.928908`

#### Content Preview

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

### 📄 File #187 - `fn.rs`
- **Path**: `hyperlane-log\src\log\fn.rs`
- **Size**: `3,601 B`
- **Modified Time**: `2025-09-15T22:37:12.929908`

#### Content Preview

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
            if parts.len() > 1 {
                if let Ok(second_element) = parts[1].parse::<usize>() {
                    res_idx = second_element.max(res_idx);
                }
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
pub fn log_handler<T: AsRef<str>>(log_data: T) -> String {
    common_log(log_data)
}

```

### 📄 File #188 - `impl.rs`
- **Path**: `hyperlane-log\src\log\impl.rs`
- **Size**: `6,965 B`
- **Modified Time**: `2025-09-15T22:37:12.929908`

#### Content Preview

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
    pub fn limit_file_size(&mut self, limit_file_size: usize) -> &mut Self {
        self.limit_file_size = limit_file_size;
        self
    }

    /// Checks if logging is enabled.
    ///
    /// # Returns
    ///
    /// - `bool` - True if logging is enabled.
    pub fn is_enable(&self) -> bool {
        self.limit_file_size != DISABLE_LOG_FILE_SIZE
    }

    /// Checks if logging is disabled.
    ///
    /// # Returns
    ///
    /// - `bool` - True if logging is disabled.
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
        let _ = append_to_file(&path, &out.as_bytes());
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
        let _ = async_append_to_file(&path, &out.as_bytes()).await;
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

### 📄 File #189 - `mod.rs`
- **Path**: `hyperlane-log\src\log\mod.rs`
- **Size**: `238 B`
- **Modified Time**: `2025-09-15T22:37:12.929908`

#### Content Preview

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

### 📄 File #190 - `struct.rs`
- **Path**: `hyperlane-log\src\log\struct.rs`
- **Size**: `457 B`
- **Modified Time**: `2025-09-15T22:37:12.929908`

#### Content Preview

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

### 📄 File #191 - `trait.rs`
- **Path**: `hyperlane-log\src\log\trait.rs`
- **Size**: `373 B`
- **Modified Time**: `2025-09-15T22:37:12.929908`

#### Content Preview

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

### 📄 File #192 - `type.rs`
- **Path**: `hyperlane-log\src\log\type.rs`
- **Size**: `636 B`
- **Modified Time**: `2025-09-15T22:37:12.930907`

#### Content Preview

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

### 📄 File #193 - `.gitignore`
- **Path**: `hyperlane-macros\.gitignore`
- **Size**: `32 B`
- **Modified Time**: `2025-09-15T22:37:29.398513`

#### Content Preview



### 📄 File #194 - `Cargo.toml`
- **Path**: `hyperlane-macros\Cargo.toml`
- **Size**: `1,230 B`
- **Modified Time**: `2025-10-01T21:58:50.909285`

#### Content Preview



### 📄 File #195 - `LICENSE`
- **Path**: `hyperlane-macros\LICENSE`
- **Size**: `1,066 B`
- **Modified Time**: `2025-09-15T22:37:29.399022`

#### Content Preview



### 📄 File #196 - `README.md`
- **Path**: `hyperlane-macros\README.md`
- **Size**: `22,567 B`
- **Modified Time**: `2025-10-01T21:58:50.914121`

#### Content Preview

```markdown
<center>

## hyperlane-macros

[![](https://img.shields.io/crates/v/hyperlane-macros.svg)](https://crates.io/crates/hyperlane-macros)
[![](https://img.shields.io/crates/d/hyperlane-macros.svg)](https://img.shields.io/crates/d/hyperlane-macros.svg)
[![](https://docs.rs/hyperlane-macros/badge.svg)](https://docs.rs/hyperlane-macros)
[![](https://github.com/hyperlane-dev/hyperlane-macros/workflows/Rust/badge.svg)](https://github.com/hyperlane-dev/hyperlane-macros/actions?query=workflow:Rust)
[![](https://img.shields.io/crates/l/hyperlane-macros.svg)](./LICENSE)

</center>

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
- `#[send_once]` - Send complete response exactly once after function execution
- `#[send_body_once]` - Send response body exactly once after function execution
- `#[send_with_data("data")]` - Send complete response with specified data after function execution
- `#[send_once_with_data("data")]` - Send complete response exactly once with specified data after function execution
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
- `#[request_body_json(variable_name: type)]` - Parse request body as JSON into specified variable and type

### Attribute Macros

- `#[attribute(key => variable_name: type)]` - Extract a specific attribute by key into a typed variable

### Attributes Macros

- `#[attributes(variable_name)]` - Get all attributes as a HashMap for comprehensive attribute access

### Route Param Macros

- `#[route_param(key => variable_name)]` - Extract a specific route parameter by key into a variable

### Route Params Macros

- `#[route_params(variable_name)]` - Get all route parameters as a collection

### Request Query Macros

- `#[request_query(key => variable_name)]` - Extract a specific query parameter by key from the URL query string

### Request Querys Macros

- `#[request_querys(variable_name)]` - Get all query parameters as a collection

### Request Header Macros

- `#[request_header(key => variable_name)]` - Extract a specific HTTP header by name from the request

### Request Headers Macros

- `#[request_headers(variable_name)]` - Get all HTTP headers as a collection

### Request Cookie Macros

- `#[request_cookie(key => variable_name)]` - Extract a specific cookie value by key from the request cookie header

### Request Cookies Macros

- `#[request_cookies(variable_name)]` - Get all cookies as a raw string from the cookie header

### Request Version Macros

- `#[request_version(variable_name)]` - Extract the HTTP request version into a variable

### Request Path Macros

- `#[request_path(variable_name)]` - Extract the HTTP request path into a variable

### Host Macros

- `#[host("hostname")]` - Restrict function execution to requests with a specific host header value
- `#[reject_host("hostname")]` - Reject requests that match a specific host header value

### Referer Macros

- `#[referer("url")]` - Restrict function execution to requests with a specific referer header value
- `#[reject_referer("url")]` - Reject requests that match a specific referer header value

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

- `#[http_from_stream]` - Wraps function body with HTTP stream processing, using default buffer size. The function body only executes if data is successfully read from the HTTP stream.
- `#[http_from_stream(buffer_size)]` - Wraps function body with HTTP stream processing using specified buffer size.
- `#[http_from_stream(variable_name)]` - Wraps function body with HTTP stream processing, storing data in specified variable name.
- `#[http_from_stream(buffer_size, variable_name)]` - Wraps function body with HTTP stream processing using specified buffer size and variable name.
- `#[http_from_stream(variable_name, buffer_size)]` - Wraps function body with HTTP stream processing using specified variable name and buffer size (reversed order).
- `#[ws_from_stream]` - Wraps function body with WebSocket stream processing, using default buffer size. The function body only executes if data is successfully read from the WebSocket stream.
- `#[ws_from_stream(buffer_size)]` - Wraps function body with WebSocket stream processing using specified buffer size.
- `#[ws_from_stream(variable_name)]` - Wraps function body with WebSocket stream processing, storing data in specified variable name.
- `#[ws_from_stream(buffer_size, variable_name)]` - Wraps function body with WebSocket stream processing using specified buffer size and variable name.
- `#[ws_from_stream(variable_name, buffer_size)]` - Wraps function body with WebSocket stream processing using specified variable name and buffer size (reversed order).

### Response Header Macros

### Response Body Macros

### Route Macros

- `#[route("path")]` - Register a route handler for the given path using the default server (Prerequisite: requires the #[hyperlane(server: Server)] macro)

### Helper Tips

- **Request related macros** (data extraction) use **`get`** operations - they retrieve/query data from the request
- **Response related macros** (data setting) use **`set`** operations - they assign/configure response data
- **Hook macros** For hook-related macros that support an `order` parameter, if `order` is not specified, the hook will have higher priority than hooks with a specified `order` (applies only to macros like `#[request_middleware]`, `#[response_middleware]`, `#[panic_hook]`)

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
#[epilogue_macros(response_body("panic_hook"), send)]
async fn panic_hook(ctx: Context) {}

#[request_middleware]
#[epilogue_macros(
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
#[epilogue_macros(
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
#[prologue_macros(
    reject(ctx.get_request().await.is_ws()),
    response_header(STEP => "response_middleware_2")
)]
#[epilogue_macros(send, flush)]
async fn response_middleware_2(ctx: Context) {}

#[response_middleware("3")]
#[prologue_macros(
    ws,
    response_header(STEP => "response_middleware_3")
)]
#[epilogue_macros(send_body, flush)]
async fn response_middleware_3(ctx: Context) {}

#[get]
#[http]
async fn prologue_hooks(ctx: Context) {}

#[response_status_code(200)]
async fn epilogue_hooks(ctx: Context) {}

#[route("/response")]
#[response_body(&RESPONSE_DATA)]
#[response_reason_phrase(CUSTOM_REASON)]
#[response_status_code(CUSTOM_STATUS_CODE)]
#[response_header(CUSTOM_HEADER_NAME => CUSTOM_HEADER_VALUE)]
async fn response(ctx: Context) {}

#[route("/connect")]
#[prologue_macros(connect, response_body("connect"))]
async fn connect(ctx: Context) {}

#[route("/delete")]
#[prologue_macros(delete, response_body("delete"))]
async fn delete(ctx: Context) {}

#[route("/head")]
#[prologue_macros(head, response_body("head"))]
async fn head(ctx: Context) {}

#[route("/options")]
#[prologue_macros(options, response_body("options"))]
async fn options(ctx: Context) {}

#[route("/patch")]
#[prologue_macros(patch, response_body("patch"))]
async fn patch(ctx: Context) {}

#[route("/put")]
#[prologue_macros(put, response_body("put"))]
async fn put(ctx: Context) {}

#[route("/trace")]
#[prologue_macros(trace, response_body("trace"))]
async fn trace(ctx: Context) {}

#[route("/h2c")]
#[prologue_macros(h2c, response_body("h2c"))]
async fn h2c(ctx: Context) {}

#[route("/http")]
#[prologue_macros(http, response_body("http"))]
async fn http_only(ctx: Context) {}

#[route("/http0_9")]
#[prologue_macros(http0_9, response_body("http0_9"))]
async fn http0_9(ctx: Context) {}

#[route("/http1_0")]
#[prologue_macros(http1_0, response_body("http1_0"))]
async fn http1_0(ctx: Context) {}

#[route("/http1_1")]
#[prologue_macros(http1_1, response_body("http1_1"))]
async fn http1_1(ctx: Context) {}

#[route("/http2")]
#[prologue_macros(http2, response_body("http2"))]
async fn http2(ctx: Context) {}

#[route("/http3")]
#[prologue_macros(http3, response_body("http3"))]
async fn http3(ctx: Context) {}

#[route("/tls")]
#[prologue_macros(tls, response_body("tls"))]
async fn tls(ctx: Context) {}

#[route("/http1_1_or_higher")]
#[prologue_macros(http1_1_or_higher, response_body("http1_1_or_higher"))]
async fn http1_1_or_higher(ctx: Context) {}

#[route("/unknown_method")]
#[prologue_macros(
    clear_response_headers,
    filter(ctx.get_request().await.is_unknown_method()),
    response_body("unknown_method")
)]
async fn unknown_method(ctx: Context) {}

#[route("/get")]
#[send_body_once]
#[prologue_macros(ws, get, response_body("get"))]
async fn get(ctx: Context) {}

#[send_once]
#[route("/post")]
#[prologue_macros(post, response_body("post"))]
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
#[prologue_hooks(prologue_hooks)]
#[epilogue_hooks(epilogue_hooks)]
#[response_body("Testing hook macro")]
async fn hook(ctx: Context) {}

#[closed]
#[route("/get_post")]
#[prologue_macros(
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
#[epilogue_macros(
    response_body("host string literal: localhost"),
    send,
    http_from_stream
)]
#[prologue_macros(response_body("host string literal: localhost"), send)]
async fn host(ctx: Context) {}

#[route("/request_query")]
#[epilogue_macros(
    request_query("test" => request_query_option),
    response_body(&format!("request query: {request_query_option:?}")),
    send,
    http_from_stream(1024)
)]
#[prologue_macros(
    request_query("test" => request_query_option),
    response_body(&format!("request query: {request_query_option:?}")),
    send
)]
async fn request_query(ctx: Context) {}

#[route("/request_header")]
#[epilogue_macros(
    request_header(HOST => request_header_option),
    response_body(&format!("request header: {request_header_option:?}")),
    send,
    http_from_stream(_request)
)]
#[prologue_macros(
    request_header(HOST => request_header_option),
    response_body(&format!("request header: {request_header_option:?}")),
    send
)]
async fn request_header(ctx: Context) {}

#[route("/request_querys")]
#[epilogue_macros(
    request_querys(request_querys),
    response_body(&format!("request querys: {request_querys:?}")),
    send,
    http_from_stream(1024, _request)
)]
#[prologue_macros(
    request_querys(request_querys),
    response_body(&format!("request querys: {request_querys:?}")),
    send
)]
async fn request_querys(ctx: Context) {}

#[route("/request_headers")]
#[epilogue_macros(
    request_headers(request_headers),
    response_body(&format!("request headers: {request_headers:?}")),
    send,
    http_from_stream(_request, 1024)
)]
#[prologue_macros(
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
#[prologue_macros(
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
#[prologue_macros(
    referer("http://localhost"),
    response_body("referer string literal: http://localhost")
)]
async fn referer(ctx: Context) {}

#[route("/reject_referer")]
#[prologue_macros(
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

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Contact

For any inquiries, please reach out to the author at [root@ltpp.vip](mailto:root@ltpp.vip).

```

### 📄 File #197 - `config`
- **Path**: `hyperlane-macros\.git\config`
- **Size**: `326 B`
- **Modified Time**: `2025-09-15T22:37:29.390902`

#### Content Preview



### 📄 File #198 - `description`
- **Path**: `hyperlane-macros\.git\description`
- **Size**: `73 B`
- **Modified Time**: `2025-09-15T22:37:27.027664`

#### Content Preview



### 📄 File #199 - `FETCH_HEAD`
- **Path**: `hyperlane-macros\.git\FETCH_HEAD`
- **Size**: `716 B`
- **Modified Time**: `2025-10-01T21:58:50.856348`

#### Content Preview



### 📄 File #200 - `HEAD`
- **Path**: `hyperlane-macros\.git\HEAD`
- **Size**: `23 B`
- **Modified Time**: `2025-09-15T22:37:29.384877`

#### Content Preview



### 📄 File #201 - `index`
- **Path**: `hyperlane-macros\.git\index`
- **Size**: `6,789 B`
- **Modified Time**: `2025-10-01T21:58:50.938057`

#### Content Preview



### 📄 File #202 - `ORIG_HEAD`
- **Path**: `hyperlane-macros\.git\ORIG_HEAD`
- **Size**: `41 B`
- **Modified Time**: `2025-09-15T22:44:23.276438`

#### Content Preview



### 📄 File #203 - `packed-refs`
- **Path**: `hyperlane-macros\.git\packed-refs`
- **Size**: `114 B`
- **Modified Time**: `2025-09-15T22:37:29.374722`

#### Content Preview



### 📄 File #204 - `shallow`
- **Path**: `hyperlane-macros\.git\shallow`
- **Size**: `41 B`
- **Modified Time**: `2025-09-15T22:37:29.168042`

#### Content Preview



### 📄 File #205 - `applypatch-msg.sample`
- **Path**: `hyperlane-macros\.git\hooks\applypatch-msg.sample`
- **Size**: `478 B`
- **Modified Time**: `2025-09-15T22:37:27.028180`

#### Content Preview



### 📄 File #206 - `commit-msg.sample`
- **Path**: `hyperlane-macros\.git\hooks\commit-msg.sample`
- **Size**: `896 B`
- **Modified Time**: `2025-09-15T22:37:27.028180`

#### Content Preview



### 📄 File #207 - `fsmonitor-watchman.sample`
- **Path**: `hyperlane-macros\.git\hooks\fsmonitor-watchman.sample`
- **Size**: `4,726 B`
- **Modified Time**: `2025-09-15T22:37:27.028696`

#### Content Preview



### 📄 File #208 - `post-update.sample`
- **Path**: `hyperlane-macros\.git\hooks\post-update.sample`
- **Size**: `189 B`
- **Modified Time**: `2025-09-15T22:37:27.028696`

#### Content Preview



### 📄 File #209 - `pre-applypatch.sample`
- **Path**: `hyperlane-macros\.git\hooks\pre-applypatch.sample`
- **Size**: `424 B`
- **Modified Time**: `2025-09-15T22:37:27.028696`

#### Content Preview



### 📄 File #210 - `pre-commit.sample`
- **Path**: `hyperlane-macros\.git\hooks\pre-commit.sample`
- **Size**: `1,649 B`
- **Modified Time**: `2025-09-15T22:37:27.029209`

#### Content Preview



### 📄 File #211 - `pre-merge-commit.sample`
- **Path**: `hyperlane-macros\.git\hooks\pre-merge-commit.sample`
- **Size**: `416 B`
- **Modified Time**: `2025-09-15T22:37:27.029209`

#### Content Preview



### 📄 File #212 - `pre-push.sample`
- **Path**: `hyperlane-macros\.git\hooks\pre-push.sample`
- **Size**: `1,374 B`
- **Modified Time**: `2025-09-15T22:37:27.029729`

#### Content Preview



### 📄 File #213 - `pre-rebase.sample`
- **Path**: `hyperlane-macros\.git\hooks\pre-rebase.sample`
- **Size**: `4,898 B`
- **Modified Time**: `2025-09-15T22:37:27.029729`

#### Content Preview



### 📄 File #214 - `pre-receive.sample`
- **Path**: `hyperlane-macros\.git\hooks\pre-receive.sample`
- **Size**: `544 B`
- **Modified Time**: `2025-09-15T22:37:27.029729`

#### Content Preview



### 📄 File #215 - `prepare-commit-msg.sample`
- **Path**: `hyperlane-macros\.git\hooks\prepare-commit-msg.sample`
- **Size**: `1,492 B`
- **Modified Time**: `2025-09-15T22:37:27.030243`

#### Content Preview



### 📄 File #216 - `push-to-checkout.sample`
- **Path**: `hyperlane-macros\.git\hooks\push-to-checkout.sample`
- **Size**: `2,783 B`
- **Modified Time**: `2025-09-15T22:37:27.030243`

#### Content Preview



### 📄 File #217 - `sendemail-validate.sample`
- **Path**: `hyperlane-macros\.git\hooks\sendemail-validate.sample`
- **Size**: `2,308 B`
- **Modified Time**: `2025-09-15T22:37:27.030243`

#### Content Preview



### 📄 File #218 - `update.sample`
- **Path**: `hyperlane-macros\.git\hooks\update.sample`
- **Size**: `3,650 B`
- **Modified Time**: `2025-09-15T22:37:27.030243`

#### Content Preview



### 📄 File #219 - `exclude`
- **Path**: `hyperlane-macros\.git\info\exclude`
- **Size**: `240 B`
- **Modified Time**: `2025-09-15T22:37:27.030755`

#### Content Preview



### 📄 File #220 - `HEAD`
- **Path**: `hyperlane-macros\.git\logs\HEAD`
- **Size**: `344 B`
- **Modified Time**: `2025-10-01T21:58:50.938057`

#### Content Preview



### 📄 File #221 - `master`
- **Path**: `hyperlane-macros\.git\logs\refs\heads\master`
- **Size**: `344 B`
- **Modified Time**: `2025-10-01T21:58:50.938057`

#### Content Preview



### 📄 File #222 - `HEAD`
- **Path**: `hyperlane-macros\.git\logs\refs\remotes\origin\HEAD`
- **Size**: `191 B`
- **Modified Time**: `2025-09-15T22:37:29.383875`

#### Content Preview



### 📄 File #223 - `master`
- **Path**: `hyperlane-macros\.git\logs\refs\remotes\origin\master`
- **Size**: `153 B`
- **Modified Time**: `2025-10-01T21:58:50.797657`

#### Content Preview



### 📄 File #224 - `b5f77eadd85aa84cf2e268828327e9f76e1247`
- **Path**: `hyperlane-macros\.git\objects\03\b5f77eadd85aa84cf2e268828327e9f76e1247`
- **Size**: `240 B`
- **Modified Time**: `2025-10-01T21:58:50.648070`

#### Content Preview



### 📄 File #225 - `1f19bb026d1404c5d3ee497e2be33c3ac8669b`
- **Path**: `hyperlane-macros\.git\objects\07\1f19bb026d1404c5d3ee497e2be33c3ac8669b`
- **Size**: `652 B`
- **Modified Time**: `2025-10-01T21:58:50.665325`

#### Content Preview



### 📄 File #226 - `cd87addf49bff29c2acfd4a88a443a608f0c5b`
- **Path**: `hyperlane-macros\.git\objects\09\cd87addf49bff29c2acfd4a88a443a608f0c5b`
- **Size**: `935 B`
- **Modified Time**: `2025-10-01T21:58:50.723491`

#### Content Preview



### 📄 File #227 - `edbe696a8767d5ce0b9359fe818ccd9ec83868`
- **Path**: `hyperlane-macros\.git\objects\10\edbe696a8767d5ce0b9359fe818ccd9ec83868`
- **Size**: `240 B`
- **Modified Time**: `2025-10-01T21:58:50.648070`

#### Content Preview



### 📄 File #228 - `f3d0e5b5f7eec3defafa50d224a0931c8e4ac8`
- **Path**: `hyperlane-macros\.git\objects\18\f3d0e5b5f7eec3defafa50d224a0931c8e4ac8`
- **Size**: `78 B`
- **Modified Time**: `2025-10-01T21:58:50.640031`

#### Content Preview



### 📄 File #229 - `b03a62f482c5ebc492fc0fe2b0b032e469e215`
- **Path**: `hyperlane-macros\.git\objects\1b\b03a62f482c5ebc492fc0fe2b0b032e469e215`
- **Size**: `241 B`
- **Modified Time**: `2025-10-01T21:58:50.648070`

#### Content Preview



### 📄 File #230 - `921370bedec8251ecbd269f6e6dcd8ecd7c23e`
- **Path**: `hyperlane-macros\.git\objects\21\921370bedec8251ecbd269f6e6dcd8ecd7c23e`
- **Size**: `165 B`
- **Modified Time**: `2025-10-01T21:58:50.631999`

#### Content Preview



### 📄 File #231 - `f5e482d4a2c0a30ca7784feec69b28c583264a`
- **Path**: `hyperlane-macros\.git\objects\29\f5e482d4a2c0a30ca7784feec69b28c583264a`
- **Size**: `9,197 B`
- **Modified Time**: `2025-10-01T21:58:50.713219`

#### Content Preview



### 📄 File #232 - `2c4d1bcb33767c0fab1945fc7712035729b4dc`
- **Path**: `hyperlane-macros\.git\objects\2c\2c4d1bcb33767c0fab1945fc7712035729b4dc`
- **Size**: `165 B`
- **Modified Time**: `2025-10-01T21:58:50.634139`

#### Content Preview



### 📄 File #233 - `aa6599719692a84fc0e9b368b4c5d660171b2f`
- **Path**: `hyperlane-macros\.git\objects\36\aa6599719692a84fc0e9b368b4c5d660171b2f`
- **Size**: `164 B`
- **Modified Time**: `2025-10-01T21:58:50.633581`

#### Content Preview



### 📄 File #234 - `eafb18021b3be9da8af7a8716fa6a3ef967753`
- **Path**: `hyperlane-macros\.git\objects\39\eafb18021b3be9da8af7a8716fa6a3ef967753`
- **Size**: `164 B`
- **Modified Time**: `2025-10-01T21:58:50.629580`

#### Content Preview



### 📄 File #235 - `73f38085eaf893de92fe7b912fe358460c0a8a`
- **Path**: `hyperlane-macros\.git\objects\3b\73f38085eaf893de92fe7b912fe358460c0a8a`
- **Size**: `52 B`
- **Modified Time**: `2025-10-01T21:58:50.639031`

#### Content Preview



### 📄 File #236 - `0c4adc2741703c7daf0f260a79ac37e42a49b5`
- **Path**: `hyperlane-macros\.git\objects\53\0c4adc2741703c7daf0f260a79ac37e42a49b5`
- **Size**: `240 B`
- **Modified Time**: `2025-10-01T21:58:50.640031`

#### Content Preview



### 📄 File #237 - `46113a141074b64683eea473d19264927d1728`
- **Path**: `hyperlane-macros\.git\objects\59\46113a141074b64683eea473d19264927d1728`
- **Size**: `240 B`
- **Modified Time**: `2025-10-01T21:58:50.663557`

#### Content Preview



### 📄 File #238 - `a3e973a0f8b0386d8f73aea5d7077574da58e7`
- **Path**: `hyperlane-macros\.git\objects\61\a3e973a0f8b0386d8f73aea5d7077574da58e7`
- **Size**: `84 B`
- **Modified Time**: `2025-10-01T21:58:50.637031`

#### Content Preview



### 📄 File #239 - `d95fa87a4b9f0bca0d3425e4e4946b96bc3f24`
- **Path**: `hyperlane-macros\.git\objects\81\d95fa87a4b9f0bca0d3425e4e4946b96bc3f24`
- **Size**: `169 B`
- **Modified Time**: `2025-10-01T21:58:50.721878`

#### Content Preview



### 📄 File #240 - `a545160eebc7030a425b7f892bbe1c8f0e0a0b`
- **Path**: `hyperlane-macros\.git\objects\86\a545160eebc7030a425b7f892bbe1c8f0e0a0b`
- **Size**: `9,286 B`
- **Modified Time**: `2025-10-01T21:58:50.720877`

#### Content Preview



### 📄 File #241 - `59203278d954190af3d8785828c4c0fad563f9`
- **Path**: `hyperlane-macros\.git\objects\87\59203278d954190af3d8785828c4c0fad563f9`
- **Size**: `652 B`
- **Modified Time**: `2025-10-01T21:58:50.679620`

#### Content Preview



### 📄 File #242 - `596ced0ba477141d3cbf507d77d96a47fefcef`
- **Path**: `hyperlane-macros\.git\objects\89\596ced0ba477141d3cbf507d77d96a47fefcef`
- **Size**: `85 B`
- **Modified Time**: `2025-10-01T21:58:50.648070`

#### Content Preview



### 📄 File #243 - `59e48abcd2da539b8048d0dab8ab83d3a93e69`
- **Path**: `hyperlane-macros\.git\objects\af\59e48abcd2da539b8048d0dab8ab83d3a93e69`
- **Size**: `5,858 B`
- **Modified Time**: `2025-10-01T21:58:50.688590`

#### Content Preview



### 📄 File #244 - `de0e812c30e48502e53e193d37456192e41f0f`
- **Path**: `hyperlane-macros\.git\objects\b9\de0e812c30e48502e53e193d37456192e41f0f`
- **Size**: `1,159 B`
- **Modified Time**: `2025-10-01T21:58:50.711388`

#### Content Preview



### 📄 File #245 - `8ca0467a9101bc1a7d9929a95cbc90753b3a76`
- **Path**: `hyperlane-macros\.git\objects\ba\8ca0467a9101bc1a7d9929a95cbc90753b3a76`
- **Size**: `673 B`
- **Modified Time**: `2025-10-01T21:58:50.701754`

#### Content Preview



### 📄 File #246 - `708b9ecf7e2856724e025562ef18a0b10b74c0`
- **Path**: `hyperlane-macros\.git\objects\be\708b9ecf7e2856724e025562ef18a0b10b74c0`
- **Size**: `672 B`
- **Modified Time**: `2025-10-01T21:58:50.708737`

#### Content Preview



### 📄 File #247 - `d600272541aecf0a3b35192d352b610a7236e4`
- **Path**: `hyperlane-macros\.git\objects\be\d600272541aecf0a3b35192d352b610a7236e4`
- **Size**: `653 B`
- **Modified Time**: `2025-10-01T21:58:50.685593`

#### Content Preview



### 📄 File #248 - `1928f80f8f9e7e137c946b2f1ce773fffb2bb3`
- **Path**: `hyperlane-macros\.git\objects\c0\1928f80f8f9e7e137c946b2f1ce773fffb2bb3`
- **Size**: `1,012 B`
- **Modified Time**: `2025-10-01T21:58:50.710354`

#### Content Preview



### 📄 File #249 - `fe4a1c1ab395643db1432a76ea9c15f766e65a`
- **Path**: `hyperlane-macros\.git\objects\da\fe4a1c1ab395643db1432a76ea9c15f766e65a`
- **Size**: `78 B`
- **Modified Time**: `2025-10-01T21:58:50.640031`

#### Content Preview



### 📄 File #250 - `b6e37ce0d3909d8e04c03f38587ae4020134c0`
- **Path**: `hyperlane-macros\.git\objects\df\b6e37ce0d3909d8e04c03f38587ae4020134c0`
- **Size**: `654 B`
- **Modified Time**: `2025-10-01T21:58:50.673338`

#### Content Preview



### 📄 File #251 - `83d9e8e3f412adb0beb13607b7e9172cb09387`
- **Path**: `hyperlane-macros\.git\objects\e8\83d9e8e3f412adb0beb13607b7e9172cb09387`
- **Size**: `2,780 B`
- **Modified Time**: `2025-10-01T21:58:50.700755`

#### Content Preview



### 📄 File #252 - `c86834726d2f001acb20e22a76067896933f58`
- **Path**: `hyperlane-macros\.git\objects\ec\c86834726d2f001acb20e22a76067896933f58`
- **Size**: `5,860 B`
- **Modified Time**: `2025-10-01T21:58:50.693561`

#### Content Preview



### 📄 File #253 - `0dcc2478ff1684900eaca445c5b84c72582fb6`
- **Path**: `hyperlane-macros\.git\objects\f0\0dcc2478ff1684900eaca445c5b84c72582fb6`
- **Size**: `5,850 B`
- **Modified Time**: `2025-10-01T21:58:50.686723`

#### Content Preview



### 📄 File #254 - `6d7ad261e43967cb8edbb94a6c05dfe1fcb87e`
- **Path**: `hyperlane-macros\.git\objects\f3\6d7ad261e43967cb8edbb94a6c05dfe1fcb87e`
- **Size**: `51 B`
- **Modified Time**: `2025-10-01T21:58:50.648070`

#### Content Preview



### 📄 File #255 - `3c9c447920075172c4e5f145be556eefffb554`
- **Path**: `hyperlane-macros\.git\objects\f6\3c9c447920075172c4e5f145be556eefffb554`
- **Size**: `165 B`
- **Modified Time**: `2025-10-01T21:58:50.635959`

#### Content Preview



### 📄 File #256 - `5d49636fc74acc2b8100ec67c286265217860b`
- **Path**: `hyperlane-macros\.git\objects\f7\5d49636fc74acc2b8100ec67c286265217860b`
- **Size**: `2,777 B`
- **Modified Time**: `2025-10-01T21:58:50.693561`

#### Content Preview



### 📄 File #257 - `201926e2f06b1acf69ed89e064b063ecf8cba8`
- **Path**: `hyperlane-macros\.git\objects\fc\201926e2f06b1acf69ed89e064b063ecf8cba8`
- **Size**: `654 B`
- **Modified Time**: `2025-10-01T21:58:50.667299`

#### Content Preview



### 📄 File #258 - `pack-19c30813ea463b0ec192e86c37e4408eaa01bdba.idx`
- **Path**: `hyperlane-macros\.git\objects\pack\pack-19c30813ea463b0ec192e86c37e4408eaa01bdba.idx`
- **Size**: `3,424 B`
- **Modified Time**: `2025-09-15T22:37:29.336083`

#### Content Preview



### 📄 File #259 - `pack-19c30813ea463b0ec192e86c37e4408eaa01bdba.pack`
- **Path**: `hyperlane-macros\.git\objects\pack\pack-19c30813ea463b0ec192e86c37e4408eaa01bdba.pack`
- **Size**: `42,771 B`
- **Modified Time**: `2025-09-15T22:37:29.336083`

#### Content Preview



### 📄 File #260 - `pack-19c30813ea463b0ec192e86c37e4408eaa01bdba.rev`
- **Path**: `hyperlane-macros\.git\objects\pack\pack-19c30813ea463b0ec192e86c37e4408eaa01bdba.rev`
- **Size**: `388 B`
- **Modified Time**: `2025-09-15T22:37:29.337910`

#### Content Preview



### 📄 File #261 - `master`
- **Path**: `hyperlane-macros\.git\refs\heads\master`
- **Size**: `41 B`
- **Modified Time**: `2025-10-01T21:58:50.938057`

#### Content Preview



### 📄 File #262 - `HEAD`
- **Path**: `hyperlane-macros\.git\refs\remotes\origin\HEAD`
- **Size**: `32 B`
- **Modified Time**: `2025-09-15T22:37:29.383373`

#### Content Preview



### 📄 File #263 - `master`
- **Path**: `hyperlane-macros\.git\refs\remotes\origin\master`
- **Size**: `41 B`
- **Modified Time**: `2025-10-01T21:58:50.797657`

#### Content Preview



### 📄 File #264 - `v7.1.11`
- **Path**: `hyperlane-macros\.git\refs\tags\v7.1.11`
- **Size**: `41 B`
- **Modified Time**: `2025-09-15T22:37:29.382016`

#### Content Preview



### 📄 File #265 - `v8.0.0`
- **Path**: `hyperlane-macros\.git\refs\tags\v8.0.0`
- **Size**: `41 B`
- **Modified Time**: `2025-10-01T21:58:50.849577`

#### Content Preview



### 📄 File #266 - `v9.0.0`
- **Path**: `hyperlane-macros\.git\refs\tags\v9.0.0`
- **Size**: `41 B`
- **Modified Time**: `2025-10-01T21:58:50.849577`

#### Content Preview



### 📄 File #267 - `v9.0.1`
- **Path**: `hyperlane-macros\.git\refs\tags\v9.0.1`
- **Size**: `41 B`
- **Modified Time**: `2025-10-01T21:58:50.856348`

#### Content Preview



### 📄 File #268 - `v9.0.2`
- **Path**: `hyperlane-macros\.git\refs\tags\v9.0.2`
- **Size**: `41 B`
- **Modified Time**: `2025-10-01T21:58:50.856348`

#### Content Preview



### 📄 File #269 - `v9.0.3`
- **Path**: `hyperlane-macros\.git\refs\tags\v9.0.3`
- **Size**: `41 B`
- **Modified Time**: `2025-10-01T21:58:50.797657`

#### Content Preview



### 📄 File #270 - `rust.yml`
- **Path**: `hyperlane-macros\.github\workflows\rust.yml`
- **Size**: `9,636 B`
- **Modified Time**: `2025-09-15T22:37:29.398513`

#### Content Preview

```yaml
name: Rust
on:
  push:
    branches: [master]
env:
  CARGO_TERM_COLOR: always
jobs:
  setup:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.read.outputs.version }}
      tag: ${{ steps.read.outputs.tag }}
      package_name: ${{ steps.read.outputs.package_name }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Install rust-toolchain
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
          components: rustfmt, clippy
      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: |
            ~/.cargo/registry
            ~/.cargo/git
            target
          key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}
      - name: Install toml-cli
        run: cargo install toml-cli
      - name: Cache toml-cli
        uses: actions/cache@v3
        with:
          path: ~/.cargo/bin/toml
          key: toml-cli-${{ runner.os }}
      - name: Read cargo metadata
        id: read
        run: |
          VERSION=$(toml get Cargo.toml package.version --raw)
          PACKAGE_NAME=$(toml get Cargo.toml package.name --raw)
          echo "📦 Detected package: $PACKAGE_NAME v$VERSION"
          if [ -z "$VERSION" ] || [ -z "$PACKAGE_NAME" ]; then
            echo "❌ Failed to read package info from Cargo.toml"
          fi
          echo "version=$VERSION" >> $GITHUB_OUTPUT
          echo "tag=v$VERSION" >> $GITHUB_OUTPUT
          echo "package_name=$PACKAGE_NAME" >> $GITHUB_OUTPUT

  check:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup rust
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
          components: rustfmt
      - name: Format check
        run: cargo fmt -- --check

  tests:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Prepare environment
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
      - name: Run tests
        run: cargo test --all-features -- --nocapture

  clippy:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Load clippy
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
          components: clippy
      - name: Run clippy
        run: cargo clippy --all-features -- -A warnings

  build:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup build
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
      - name: Build release
        run: cargo check --release --all-features

  publish:
    needs: [setup, check, tests, clippy, build]
    if: needs.setup.outputs.tag != ''
    runs-on: ubuntu-latest
    outputs:
      published: ${{ steps.publish.outputs.published }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Restore toml-cli
        uses: actions/cache@v3
        with:
          path: ~/.cargo/bin/toml
          key: toml-cli-${{ runner.os }}
      - name: Publish to crates.io
        id: publish
        env:
          CARGO_REGISTRY_TOKEN: ${{ secrets.CARGO_REGISTRY_TOKEN }}
        run: |
          set -e
          echo "published=false" >> $GITHUB_OUTPUT
          echo "${{ secrets.CARGO_REGISTRY_TOKEN }}" | cargo login
          PACKAGE_NAME=$(toml get Cargo.toml package.name --raw)
          VERSION=${{ needs.setup.outputs.version }}
          if cargo publish --allow-dirty; then
            echo "published=true" >> $GITHUB_OUTPUT
            echo "🎉🎉🎉 PUBLISH SUCCESSFUL 🎉🎉🎉"
            echo "✅ Successfully published $PACKAGE_NAME v$VERSION to crates.io"
            echo "📦 Crates.io: [https://crates.io/crates/$PACKAGE_NAME/$VERSION](https://crates.io/crates/$PACKAGE_NAME/$VERSION)"
            echo "📚 Docs.rs: [https://docs.rs/$PACKAGE_NAME/$VERSION](https://docs.rs/$PACKAGE_NAME/$VERSION)"
          else
            echo "❌ Publish failed"
          fi

  release:
    needs: [setup, check, tests, clippy, build]
    permissions:
      contents: write
      packages: write
    if: needs.setup.outputs.tag != ''
    runs-on: ubuntu-latest
    outputs:
      released: ${{ steps.release.outputs.released }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Get package name
        id: package_info
        run: |
          echo "package_name=${{ needs.setup.outputs.package_name }}" >> $GITHUB_OUTPUT
      - name: Check tag status
        id: check_tag
        run: |
          if git tag -l | grep -q "^${{ needs.setup.outputs.tag }}$"; then
            echo "tag_exists=true" >> $GITHUB_OUTPUT
            echo "🏷️ Tag ${{ needs.setup.outputs.tag }} exists locally"
          else
            echo "tag_exists=false" >> $GITHUB_OUTPUT
            echo "🏷️ Tag ${{ needs.setup.outputs.tag }} does not exist locally"
          fi
          if git ls-remote --tags origin | grep -q "refs/tags/${{ needs.setup.outputs.tag }}$"; then
            echo "remote_tag_exists=true" >> $GITHUB_OUTPUT
            echo "🌐 Tag ${{ needs.setup.outputs.tag }} exists on remote"
          else
            echo "remote_tag_exists=false" >> $GITHUB_OUTPUT
            echo "🌐 Tag ${{ needs.setup.outputs.tag }} does not exist on remote"
          fi
      - name: Check release status
        id: check_release
        run: |
          if gh release view "${{ needs.setup.outputs.tag }}" > /dev/null 2>&1; then
            echo "release_exists=true" >> $GITHUB_OUTPUT
            echo "📦 Release ${{ needs.setup.outputs.tag }} already exists"
          else
            echo "release_exists=false" >> $GITHUB_OUTPUT
            echo "📦 Release ${{ needs.setup.outputs.tag }} does not exist"
          fi
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - name: Create or update release
        id: release
        run: |
          set -e
          echo "released=false" >> $GITHUB_OUTPUT
          PACKAGE_NAME="${{ steps.package_info.outputs.package_name }}"
          VERSION="${{ needs.setup.outputs.version }}"
          TAG="${{ needs.setup.outputs.tag }}"
          echo "📦 Building source archives..."
          git archive --format=zip --prefix="${PACKAGE_NAME}-${VERSION}/" HEAD > "${PACKAGE_NAME}-${VERSION}.zip"
          git archive --format=tar.gz --prefix="${PACKAGE_NAME}-${VERSION}/" HEAD > "${PACKAGE_NAME}-${VERSION}.tar.gz"
          if [ "${{ steps.check_release.outputs.release_exists }}" = "true" ]; then
            echo "🔄 Updating existing release: $TAG"
            gh release view "$TAG" --json assets --jq '.assets[].name' | while read asset; do
              if [ -n "$asset" ]; then
                echo "🗑️ Deleting asset: $asset"
                gh release delete-asset "$TAG" "$asset" --yes || true
              fi
            done
            if gh release edit "$TAG" \
              --title "$TAG (Updated $(date '+%Y-%m-%d %H:%M:%S'))" \
              --notes "Release $TAG - Updated at $(date '+%Y-%m-%d %H:%M:%S UTC')
            ## Changes
            - Version: $VERSION
            - Package: $PACKAGE_NAME
            ## Links
            📦 [Crate on crates.io](https://crates.io/crates/$PACKAGE_NAME/$VERSION)
            📚 [Documentation on docs.rs](https://docs.rs/$PACKAGE_NAME/$VERSION)
            📋 [Commit History](https://github.com/${{ github.repository }}/commits/$TAG)" && \
               gh release upload "$TAG" "${PACKAGE_NAME}-${VERSION}.zip" "${PACKAGE_NAME}-${VERSION}.tar.gz" --clobber; then
              echo "released=true" >> $GITHUB_OUTPUT
              echo "✅ Updated release $TAG"
              echo "🔖 Tag: $TAG"
              echo "🚀 Release: [GitHub Release](${{ github.server_url }}/${{ github.repository }}/releases/tag/$TAG)"
            else
              echo "❌ Failed to update release"
            fi
          else
            if [ "${{ steps.check_tag.outputs.remote_tag_exists }}" = "false" ]; then
              echo "🏷️ Creating and pushing tag: $TAG"
              git tag "$TAG"
              git push origin "$TAG"
            fi
            echo "🆕 Creating new release: $TAG"
            if gh release create "$TAG" \
              --title "$TAG (Created $(date '+%Y-%m-%d %H:%M:%S'))" \
              --notes "Release $TAG - Created at $(date '+%Y-%m-%d %H:%M:%S UTC')
            ## Changes
            - Version: $VERSION
            - Package: $PACKAGE_NAME
            ## Links
            📦 [Crate on crates.io](https://crates.io/crates/$PACKAGE_NAME/$VERSION)
            📚 [Documentation on docs.rs](https://docs.rs/$PACKAGE_NAME/$VERSION)
            📋 [Commit History](https://github.com/${{ github.repository }}/commits/$TAG)" \
              --latest && \
               gh release upload "$TAG" "${PACKAGE_NAME}-${VERSION}.zip" "${PACKAGE_NAME}-${VERSION}.tar.gz"; then
              echo "released=true" >> $GITHUB_OUTPUT
              echo "✅ Created release $TAG"
              echo "🔖 Tag: $TAG"
              echo "🚀 Release: [GitHub Release](${{ github.server_url }}/${{ github.repository }}/releases/tag/$TAG)"
            else
              echo "❌ Failed to create release"
            fi
          fi
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

```

### 📄 File #271 - `Cargo.toml`
- **Path**: `hyperlane-macros\debug\Cargo.toml`
- **Size**: `240 B`
- **Modified Time**: `2025-09-15T22:37:29.399529`

#### Content Preview



### 📄 File #272 - `main.rs`
- **Path**: `hyperlane-macros\debug\src\main.rs`
- **Size**: `11,742 B`
- **Modified Time**: `2025-10-01T21:58:50.920332`

#### Content Preview

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
#[epilogue_macros(response_body("panic_hook"), send)]
async fn panic_hook(ctx: Context) {}

#[request_middleware]
#[epilogue_macros(
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
#[epilogue_macros(
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
#[prologue_macros(
    reject(ctx.get_request().await.is_ws()),
    response_header(STEP => "response_middleware_2")
)]
#[epilogue_macros(send, flush)]
async fn response_middleware_2(ctx: Context) {}

#[response_middleware("3")]
#[prologue_macros(
    ws,
    response_header(STEP => "response_middleware_3")
)]
#[epilogue_macros(send_body, flush)]
async fn response_middleware_3(ctx: Context) {}

#[get]
#[http]
async fn prologue_hooks(ctx: Context) {}

#[response_status_code(200)]
async fn epilogue_hooks(ctx: Context) {}

#[route("/response")]
#[response_body(&RESPONSE_DATA)]
#[response_reason_phrase(CUSTOM_REASON)]
#[response_status_code(CUSTOM_STATUS_CODE)]
#[response_header(CUSTOM_HEADER_NAME => CUSTOM_HEADER_VALUE)]
async fn response(ctx: Context) {}

#[route("/connect")]
#[prologue_macros(connect, response_body("connect"))]
async fn connect(ctx: Context) {}

#[route("/delete")]
#[prologue_macros(delete, response_body("delete"))]
async fn delete(ctx: Context) {}

#[route("/head")]
#[prologue_macros(head, response_body("head"))]
async fn head(ctx: Context) {}

#[route("/options")]
#[prologue_macros(options, response_body("options"))]
async fn options(ctx: Context) {}

#[route("/patch")]
#[prologue_macros(patch, response_body("patch"))]
async fn patch(ctx: Context) {}

#[route("/put")]
#[prologue_macros(put, response_body("put"))]
async fn put(ctx: Context) {}

#[route("/trace")]
#[prologue_macros(trace, response_body("trace"))]
async fn trace(ctx: Context) {}

#[route("/h2c")]
#[prologue_macros(h2c, response_body("h2c"))]
async fn h2c(ctx: Context) {}

#[route("/http")]
#[prologue_macros(http, response_body("http"))]
async fn http_only(ctx: Context) {}

#[route("/http0_9")]
#[prologue_macros(http0_9, response_body("http0_9"))]
async fn http0_9(ctx: Context) {}

#[route("/http1_0")]
#[prologue_macros(http1_0, response_body("http1_0"))]
async fn http1_0(ctx: Context) {}

#[route("/http1_1")]
#[prologue_macros(http1_1, response_body("http1_1"))]
async fn http1_1(ctx: Context) {}

#[route("/http2")]
#[prologue_macros(http2, response_body("http2"))]
async fn http2(ctx: Context) {}

#[route("/http3")]
#[prologue_macros(http3, response_body("http3"))]
async fn http3(ctx: Context) {}

#[route("/tls")]
#[prologue_macros(tls, response_body("tls"))]
async fn tls(ctx: Context) {}

#[route("/http1_1_or_higher")]
#[prologue_macros(http1_1_or_higher, response_body("http1_1_or_higher"))]
async fn http1_1_or_higher(ctx: Context) {}

#[route("/unknown_method")]
#[prologue_macros(
    clear_response_headers,
    filter(ctx.get_request().await.is_unknown_method()),
    response_body("unknown_method")
)]
async fn unknown_method(ctx: Context) {}

#[route("/get")]
#[send_body_once]
#[prologue_macros(ws, get, response_body("get"))]
async fn get(ctx: Context) {}

#[send_once]
#[route("/post")]
#[prologue_macros(post, response_body("post"))]
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
#[prologue_hooks(prologue_hooks)]
#[epilogue_hooks(epilogue_hooks)]
#[response_body("Testing hook macro")]
async fn hook(ctx: Context) {}

#[closed]
#[route("/get_post")]
#[prologue_macros(
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
#[epilogue_macros(
    response_body("host string literal: localhost"),
    send,
    http_from_stream
)]
#[prologue_macros(response_body("host string literal: localhost"), send)]
async fn host(ctx: Context) {}

#[route("/request_query")]
#[epilogue_macros(
    request_query("test" => request_query_option),
    response_body(&format!("request query: {request_query_option:?}")),
    send,
    http_from_stream(1024)
)]
#[prologue_macros(
    request_query("test" => request_query_option),
    response_body(&format!("request query: {request_query_option:?}")),
    send
)]
async fn request_query(ctx: Context) {}

#[route("/request_header")]
#[epilogue_macros(
    request_header(HOST => request_header_option),
    response_body(&format!("request header: {request_header_option:?}")),
    send,
    http_from_stream(_request)
)]
#[prologue_macros(
    request_header(HOST => request_header_option),
    response_body(&format!("request header: {request_header_option:?}")),
    send
)]
async fn request_header(ctx: Context) {}

#[route("/request_querys")]
#[epilogue_macros(
    request_querys(request_querys),
    response_body(&format!("request querys: {request_querys:?}")),
    send,
    http_from_stream(1024, _request)
)]
#[prologue_macros(
    request_querys(request_querys),
    response_body(&format!("request querys: {request_querys:?}")),
    send
)]
async fn request_querys(ctx: Context) {}

#[route("/request_headers")]
#[epilogue_macros(
    request_headers(request_headers),
    response_body(&format!("request headers: {request_headers:?}")),
    send,
    http_from_stream(_request, 1024)
)]
#[prologue_macros(
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
#[prologue_macros(
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
#[prologue_macros(
    referer("http://localhost"),
    response_body("referer string literal: http://localhost")
)]
async fn referer(ctx: Context) {}

#[route("/reject_referer")]
#[prologue_macros(
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
    let server_hook_clone: ServerHook = server_hook.clone();
    tokio::spawn(async move {
        tokio::time::sleep(std::time::Duration::from_secs(60)).await;
        server_hook.shutdown().await;
    });
    server_hook_clone.wait().await;
}

```

### 📄 File #273 - `lib.rs`
- **Path**: `hyperlane-macros\src\lib.rs`
- **Size**: `59,282 B`
- **Modified Time**: `2025-10-01T21:58:50.933329`

#### Content Preview

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
/// #[get]
/// async fn handle_get(ctx: Context) {
///     // Function body
/// }
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `Context` parameter.
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
/// #[post]
/// async fn handle_post(ctx: Context) {
///     // Function body
/// }
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `Context` parameter.
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
/// #[put]
/// async fn handle_put(ctx: Context) {
///     // Function body
/// }
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `Context` parameter.
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
/// #[delete]
/// async fn handle_delete(ctx: Context) {
///     // Function body
/// }
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `Context` parameter.
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
/// #[patch]
/// async fn handle_patch(ctx: Context) {
///     // Function body
/// }
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `Context` parameter.
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
/// #[head]
/// async fn handle_head(ctx: Context) {
///     // Function body
/// }
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `Context` parameter.
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
/// #[options]
/// async fn handle_options(ctx: Context) {
///     // Function body
/// }
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `Context` parameter.
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
/// #[connect]
/// async fn handle_connect(ctx: Context) {
///     // Function body
/// }
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `Context` parameter.
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
/// #[trace]
/// async fn handle_trace(ctx: Context) {
///     // Function body
/// }
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `Context` parameter.
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
/// #[methods(get, post)]
/// async fn handle_get_post(ctx: Context) {
///     // Function body
/// }
///
/// #[methods(put, patch, delete)]
/// async fn handle_modifications(ctx: Context) {
///     // Function body
/// }
/// ```
///
/// The macro accepts a comma-separated list of HTTP method names (lowercase) and should be
/// applied to async functions that accept a `Context` parameter.
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
/// #[ws]
/// async fn handle_websocket(ctx: Context) {
///     // WebSocket handling logic
/// }
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `Context` parameter.
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
/// #[http]
/// async fn handle_http(ctx: Context) {
///     // HTTP request handling logic
/// }
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `Context` parameter.
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
/// const CUSTOM_STATUS: i32 = 418;
///
/// #[response_status_code(200)]
/// async fn success_handler(ctx: Context) {
///     // Response will have status code 200
/// }
///
/// #[response_status_code(404)]
/// async fn not_found_handler(ctx: Context) {
///     // Response will have status code 404
/// }
///
/// #[response_status_code(CUSTOM_STATUS)]
/// async fn custom_handler(ctx: Context) {
///     // Response will have status code from global constant
/// }
/// ```
///
/// The macro accepts a numeric HTTP status code or a global constant
/// and should be applied to async functions that accept a `Context` parameter.
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
/// const CUSTOM_REASON: &str = "I'm a teapot";
///
/// #[response_reason_phrase("OK")]
/// async fn success_handler(ctx: Context) {
///     // Response will have reason phrase "OK"
/// }
///
/// #[response_reason_phrase("Not Found")]
/// async fn not_found_handler(ctx: Context) {
///     // Response will have reason phrase "Not Found"
/// }
///
/// #[response_reason_phrase(CUSTOM_REASON)]
/// async fn custom_handler(ctx: Context) {
///     // Response will have reason phrase from global constant
/// }
/// ```
///
/// The macro accepts a string literal or global constant for the reason phrase and should be
/// applied to async functions that accept a `Context` parameter.
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
/// const HEADER_NAME: &str = "X-Custom-Header";
/// const HEADER_VALUE: &str = "custom-value";
///
/// #[response_header("Content-Type", "application/json")]
/// async fn json_handler(ctx: Context) {
///     // Response will have Content-Type header set to application/json
/// }
///
/// #[response_header("X-Static-Header" => "static-value")]
/// async fn set_header_handler(ctx: Context) {
///     // Response will have static header replaced (overwrite existing)
/// }
///
/// #[response_header(HEADER_NAME, HEADER_VALUE)]
/// async fn dynamic_header_handler(ctx: Context) {
///     // Response will have header from global constants
/// }
///
/// #[response_header("Cache-Control" => "no-cache")]
/// async fn set_cache_handler(ctx: Context) {
///     // Response will have Cache-Control header replaced
/// }
///
/// #[response_header("X-Add-Header", "add-value")]
/// #[response_header("X-Set-Header" => "set-value")]
/// async fn header_operations_handler(ctx: Context) {
///     // Response will have X-Add-Header set and X-Set-Header replaced
/// }
/// ```
///
/// The macro accepts header name and header value, both can be string literals or global constants.
/// Use `"key", "value"` for setting headers and `"key" => "value"` for replacing headers.
/// Should be applied to async functions that accept a `Context` parameter.
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
/// const RESPONSE_DATA: &str = "Dynamic content from constant";
///
/// #[response_body("Hello, World!")]
/// async fn hello_handler(ctx: Context) {
///     // Response will have body "Hello, World!"
/// }
///
/// #[response_body("{\"message\": \"success\"}")]
/// async fn json_response_handler(ctx: Context) {
///     // Response will have JSON body
/// }
///
/// #[response_body(RESPONSE_DATA)]
/// async fn dynamic_body_handler(ctx: Context) {
///     // Response will have body from global constant
/// }
/// ```
///
/// The macro accepts a string literal or global constant for the response body and should be
/// applied to async functions that accept a `Context` parameter.
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
/// #[clear_response_headers]
/// async fn clear_headers(ctx: Context) {
///     // Clear all response headers
/// }
/// ```
///
/// The macro should be applied to async functions that accept a `Context` parameter.   
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
/// #[response_version(HttpVersion::HTTP1_1)]
/// async fn version_from_constant(ctx: Context) {
///     // Response will have version from global constant
/// }
/// ```
///
/// The macro accepts a variable or code block for the response version and should be
/// applied to async functions that accept a `Context` parameter.
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
/// #[send]
/// async fn auto_send_handler(ctx: Context) {
///     let _ = ctx.set_response_body("Hello World").await;
///     // Response is automatically sent after function returns
/// }
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `Context` parameter.
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
/// #[send_body]
/// async fn auto_send_body_handler(ctx: Context) {
///     let _ = ctx.set_response_body("Response body content").await;
///     // Only response body is automatically sent after function returns
/// }
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `Context` parameter.
#[proc_macro_attribute]
pub fn send_body(_attr: TokenStream, item: TokenStream) -> TokenStream {
    send_body_macro(item, Position::Epilogue)
}

/// Sends the complete response with data after function execution.
///
/// This attribute macro ensures that the response (request headers and body) is automatically sent
/// to the client after the function completes execution, with the specified data.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[send_with_data("Hello, World!")]
/// async fn auto_send_with_data_handler(ctx: Context) {
///     // Response is automatically sent with the specified data after function returns
/// }
/// ```
///
/// The macro accepts data to send and should be applied to async functions
/// that accept a `Context` parameter.
#[proc_macro_attribute]
pub fn send_with_data(attr: TokenStream, item: TokenStream) -> TokenStream {
    send_with_data_macro(attr, item, Position::Epilogue)
}

/// Sends the complete response exactly once after function execution.
///
/// This attribute macro ensures that the response is sent exactly once to the client,
/// preventing multiple response transmissions for single-use scenarios.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[send_once]
/// async fn send_once_handler(ctx: Context) {
///     let _ = ctx.set_response_body("One-time response").await;
///     // Response is sent exactly once after function returns
/// }
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `Context` parameter.
#[proc_macro_attribute]
pub fn send_once(_attr: TokenStream, item: TokenStream) -> TokenStream {
    send_once_macro(item, Position::Epilogue)
}

/// Sends only the response body exactly once after function execution.
///
/// This attribute macro ensures that the response body is sent exactly once to the client,
/// preventing multiple body transmissions for single-use scenarios.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[send_body_once]
/// async fn send_body_once_handler(ctx: Context) {
///     let _ = ctx.set_response_body("One-time body content").await;
///     // Response body is sent exactly once after function returns
/// }
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `Context` parameter.
#[proc_macro_attribute]
pub fn send_body_once(_attr: TokenStream, item: TokenStream) -> TokenStream {
    send_body_once_macro(item, Position::Epilogue)
}

/// Sends the complete response exactly once with data after function execution.
///
/// This attribute macro ensures that the response is sent exactly once to the client,
/// preventing multiple response transmissions for single-use scenarios, with the specified data.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[send_once_with_data("One-time response")]
/// async fn send_once_with_data_handler(ctx: Context) {
///     // Response is sent exactly once with the specified data after function returns
/// }
/// ```
///
/// The macro accepts data to send and should be applied to async functions
/// that accept a `Context` parameter.
#[proc_macro_attribute]
pub fn send_once_with_data(attr: TokenStream, item: TokenStream) -> TokenStream {
    send_once_with_data_macro(attr, item, Position::Epilogue)
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
/// #[flush]
/// async fn flush_handler(ctx: Context) {
///     let _ = ctx.set_response_body("Immediate response").await;
///     // Response stream is flushed after function returns
/// }
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `Context` parameter.
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
/// #[aborted]
/// async fn handle_aborted(ctx: Context) {
///     // Handle aborted request logic
/// }
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `Context` parameter.
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
/// #[closed]
/// async fn handle_closed(ctx: Context) {
///     // Handle closed connection logic
/// }
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `Context` parameter.
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
/// #[h2c]
/// async fn handle_h2c(ctx: Context) {
///     // Handle HTTP/2 cleartext requests
/// }
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `Context` parameter.
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
/// #[http0_9]
/// async fn handle_http09(ctx: Context) {
///     // Handle HTTP/0.9 requests
/// }
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `Context` parameter.
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
/// #[http1_0]
/// async fn handle_http10(ctx: Context) {
///     // Handle HTTP/1.0 requests
/// }
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `Context` parameter.
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
/// #[http1_1]
/// async fn handle_http11(ctx: Context) {
///     // Handle HTTP/1.1 requests
/// }
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `Context` parameter.
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
/// #[http1_1_or_higher]
/// async fn handle_modern_http(ctx: Context) {
///     // Handle HTTP/1.1, HTTP/2, HTTP/3, etc.
/// }
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `Context` parameter.
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
/// #[http2]
/// async fn handle_http2(ctx: Context) {
///     // Handle HTTP/2 requests
/// }
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `Context` parameter.
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
/// #[http3]
/// async fn handle_http3(ctx: Context) {
///     // Handle HTTP/3 requests
/// }
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `Context` parameter.
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
/// #[tls]
/// async fn handle_secure(ctx: Context) {
///     // Handle TLS-encrypted requests only
/// }
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `Context` parameter.
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
/// #[filter(ctx.get_request().await.is_ws())]
/// async fn handle_ws(ctx: Context) {
///     // This code will only run for WebSocket requests.
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
/// #[reject(ctx.get_request().await.is_http())]
/// async fn handle_non_http(ctx: Context) {
///     // This code will not run for HTTP requests.
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
/// #[host("localhost")]
/// async fn handle_example_com(ctx: Context) {
///     // Function body for localhost requests
/// }
///
/// #[host("api.localhost")]
/// async fn handle_api_subdomain(ctx: Context) {
///     // Function body for api.localhost requests
/// }
/// ```
///
/// The macro accepts a string literal specifying the expected host value and should be
/// applied to async functions that accept a `Context` parameter.
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
/// #[reject_host("localhost")]
/// async fn handle_with_host(ctx: Context) {
///     // Function body for requests with host header
/// }
/// ```
///
/// The macro takes no parameters and should be applied directly to async functions
/// that accept a `Context` parameter.
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
/// #[referer("http://localhost")]
/// async fn handle_example_referer(ctx: Context) {
///     // Function body for requests from localhost
/// }
///
/// #[referer("https://api.localhost")]
/// async fn handle_api_referer(ctx: Context) {
///     // Function body for requests from api.localhost
/// }
/// ```
///
/// The macro accepts a string literal specifying the expected referer value and should be
/// applied to async functions that accept a `Context` parameter.
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
/// #[reject_referer("http://localhost")]
/// async fn handle_without_spam_referer(ctx: Context) {
///     // Function body for requests not from localhost
/// }
/// ```
///
/// The macro accepts a string literal specifying the referer value to filter out and should be
/// applied to async functions that accept a `Context` parameter.
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
/// #[get]
/// async fn prologue_handler1(ctx: Context) {
///     // First pre-execution logic
/// }
///
/// #[http]
/// async fn prologue_handler2(ctx: Context) {
///     // Second pre-execution logic
/// }
///
/// #[prologue_hooks(prologue_handler1, prologue_handler2)]
/// async fn main_handler(ctx: Context) {
///     // Main function logic (runs after prologue_handler1 and prologue_handler2)
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
/// #[send]
/// async fn epilogue_handler1(ctx: Context) {
///     // First post-execution logic
/// }
///
/// #[flush]
/// async fn epilogue_handler2(ctx: Context) {
///     // Second post-execution logic
/// }
///
/// #[epilogue_hooks(epilogue_handler1, epilogue_handler2)]
/// async fn main_handler(ctx: Context) {
///     // Main function logic (runs before epilogue_handler1 and epilogue_handler2)
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
/// #[request_body(raw_body)]
/// async fn handle_raw_body(ctx: Context) {
///     // Use the raw request body
///     let body_content = raw_body;
/// }
/// ```
///
/// The macro accepts only a variable name. The variable will be available
/// in the function scope as a `RequestBody` type.
#[proc_macro_attribute]
pub fn request_body(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_body_macro(attr, item, Position::Prologue)
}

/// Parses the request body as JSON into a specified variable and type.
///
/// This attribute macro extracts and deserializes the request body content as JSON into a variable
/// with the specified type. The body content is parsed as JSON using serde.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
/// use serde::Deserialize;
///
/// #[derive(Deserialize, Clone)]
/// struct UserData {
///     name: String,
///     age: u32,
/// }
///
/// #[request_body_json(user_data: UserData)]
/// async fn handle_user(ctx: Context) {
///     if let Ok(data) = user_data {
///         // Use the parsed user data
///     }
/// }
/// ```
///
/// The macro accepts a variable name and type in the format `variable_name: Type`.
/// The variable will be available in the function scope as a `Result<Type, JsonError>`.
#[proc_macro_attribute]
pub fn request_body_json(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_body_json_macro(attr, item, Position::Prologue)
}

/// Extracts a specific attribute value into a variable.
///
/// This attribute macro retrieves a specific attribute by key and makes it available
/// as a typed variable from the request context.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
/// use serde::Deserialize;
///
/// const USER_KEY: &str = "user_data";
///
/// #[derive(Deserialize, Clone)]
/// struct User {
///     id: u64,
///     name: String,
/// }
///
/// #[attribute(USER_KEY => user: User)]
/// async fn handle_with_attribute(ctx: Context) {
///     if let Some(user_data) = user {
///         // Use the extracted attribute
///     }
/// }
/// ```
///
/// The macro accepts a key-to-variable mapping in the format `key => variable_name: Type`.
/// The variable will be available as an `Option<Type>` in the function scope.
#[proc_macro_attribute]
pub fn attribute(attr: TokenStream, item: TokenStream) -> TokenStream {
    attribute_macro(attr, item, Position::Prologue)
}

/// Extracts all attributes into a HashMap variable.
///
/// This attribute macro retrieves all available attributes from the request context
/// and makes them available as a HashMap for comprehensive attribute access.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[attributes(all_attrs)]
/// async fn handle_with_all_attributes(ctx: Context) {
///     for (key, value) in all_attrs {
///         // Process each attribute
///     }
/// }
/// ```
///
/// The macro accepts a variable name that will contain a HashMap of all attributes.
/// The variable will be available as a HashMap in the function scope.
#[proc_macro_attribute]
pub fn attributes(attr: TokenStream, item: TokenStream) -> TokenStream {
    attributes_macro(attr, item, Position::Prologue)
}

/// Extracts a specific route parameter into a variable.
///
/// This attribute macro retrieves a specific route parameter by key and makes it
/// available as a variable. Route parameters are extracted from the URL path segments.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// // For route like "/users/{id}"
/// #[route_param("id" => user_id)]
/// async fn get_user(ctx: Context) {
///     if let Some(id) = user_id {
///         // Use the route parameter
///     }
/// }
/// ```
///
/// The macro accepts a key-to-variable mapping in the format `"key" => variable_name`.
/// The variable will be available as an `Option<String>` in the function scope.
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
/// // For route like "/users/{id}/posts/{epilogue_id}"
/// #[route_params(params)]
/// async fn handle_nested_route(ctx: Context) {
///     for (key, value) in params {
///         // Process each route parameter
///     }
/// }
/// ```
///
/// The macro accepts a variable name that will contain all route parameters.
/// The variable will be available as a collection in the function scope.
#[proc_macro_attribute]
pub fn route_params(attr: TokenStream, item: TokenStream) -> TokenStream {
    route_params_macro(attr, item, Position::Prologue)
}

/// Extracts a specific request query parameter into a variable.
///
/// This attribute macro retrieves a specific request query parameter by key and makes it
/// available as a variable. Query parameters are extracted from the URL request query string.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// // For URL like "/search?q=rust&limit=10"
/// #[request_query("q" => search_term)]
/// async fn search(ctx: Context) {
///     if let Some(term) = search_term {
///         // Use the request query parameter
///     }
/// }
/// ```
///
/// The macro accepts a key-to-variable mapping in the format `"key" => variable_name`.
/// The variable will be available as an `Option<String>` in the function scope.
#[proc_macro_attribute]
pub fn request_query(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_query_macro(attr, item, Position::Prologue)
}

/// Extracts all request query parameters into a collection variable.
///
/// This attribute macro retrieves all available request query parameters from the URL request query string
/// and makes them available as a collection for comprehensive request query parameter access.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// // For URL like "/search?q=rust&limit=10&sort=date"
/// #[request_querys(all_params)]
/// async fn search_with_params(ctx: Context) {
///     for (key, value) in all_params {
///         // Process each request query parameter
///     }
/// }
/// ```
///
/// The macro accepts a variable name that will contain all request query parameters.
/// The variable will be available as a collection in the function scope.
#[proc_macro_attribute]
pub fn request_querys(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_querys_macro(attr, item, Position::Prologue)
}

/// Extracts a specific HTTP request header into a variable.
///
/// This attribute macro retrieves a specific HTTP request header by name and makes it
/// available as a variable. Header values are extracted from the request request headers collection.
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[request_header(HOST => host_request_header)]
/// async fn handle_with_host(ctx: Context) {
///     if let Some(host) = host_request_header {
///         // Use the host request_header value
///     }
/// }
///
/// #[request_header("Content-Type" => content_type)]
/// async fn handle_with_content_type(ctx: Context) {
///     if let Some(ct) = content_type {
///         // Use the content type request_header
///     }
/// }
/// ```
///
/// The macro accepts a request header name-to-variable mapping in the format `HEADER_NAME => variable_name`
/// or `"Header-Name" => variable_name`. The variable will be available as an `Option<String>`.
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
/// #[request_headers(all_request_headers)]
/// async fn handle_with_all_request_headers(ctx: Context) {
///     for (name, value) in all_request_headers {
///         // Process each request_header
///     }
/// }
/// ```
///
/// The macro accepts a variable name that will contain all HTTP request headers.
/// The variable will be available as a collection in the function scope.
#[proc_macro_attribute]
pub fn request_headers(attr: TokenStream, item: TokenStream) -> TokenStream {
    request_headers_macro(attr, item, Position::Prologue)
}

/// Extracts a specific cookie value or all cookies into a variable.
///
/// This attribute macro supports two syntaxes:
/// 1. `cookie(key => variable_name)` - Extract a specific cookie value by key
/// 2. `cookie(variable_name)` - Extract all cookies as a raw string
///
/// # Usage
///
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[request_cookie("session_id" => session_cookie_opt)]
/// async fn handle_with_session(ctx: Context) {
///     if let Some(session) = session_cookie_opt {
///         // Use the session cookie value
///     }
/// }
/// ```
///
/// For specific cookie extraction, the variable will be available as `Option<String>`.
/// For all cookies extraction, the variable will be available as `String`.
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
/// #[request_cookies(cookie_value)]
/// async fn handle_with_cookies(ctx: Context) {
///     // Use the cookie value
///     if !cookie_value.is_empty() {
///         // Process cookie data
///     }
/// }
/// ```
///
/// The macro accepts a variable name that will contain the Cookie header value.
/// The variable will be available as a String in the function scope.
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
/// #[request_version(http_version)]
/// async fn handle_with_version(ctx: Context) {
///     // Use the HTTP version
/// }
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
/// #[request_path(request_path)]
/// async fn handle_with_path(ctx: Context) {
///     // Use the request path
///     if request_path.starts_with("/api/") {
///         // Handle API requests
///     }
/// }
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
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[hyperlane(server: Server)]
/// #[tokio::main]
/// async fn main() {
///     // `server` is now available as: `let server: Server = Server::new().await;`
///     // The function body can now use `server`.
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
/// #[route("/")]
/// async fn route(ctx: Context) {
///     // function body
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
/// #[request_middleware(1)]
/// #[request_middleware("2")]
/// async fn log_request(ctx: Context) {
///     // Middleware logic
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
/// #[response_middleware(1)]
/// #[response_middleware("2")]
/// async fn add_custom_header(ctx: Context) {
///     // Middleware logic
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
/// async fn handle_panic(ctx: Context) {
///     // Panic handling logic
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
/// #[prologue_macros(post, send)]
/// async fn handler(ctx: Context) {
///     // ...
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
/// #[epilogue_macros(post, send)]
/// async fn handler(ctx: Context) {
///     // ...
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
/// #[send_body_with_data("Response body content")]
/// async fn send_body_with_data_handler(ctx: Context) {
///     // Response body is automatically sent with the specified data after function returns
/// }
/// ```
///
/// The macro accepts data to send and should be applied to async functions
/// that accept a `Context` parameter.
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
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[http_from_stream]
/// async fn handle_data(ctx: Context) {
///     // Process data from HTTP stream with default buffer size
/// }
/// ```
///
/// Basic usage with buffer size:
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[ws_from_stream(1024)]
/// async fn handle_data(ctx: Context) {
///     // Process data from stream with 1024 byte buffer
/// }
/// ```
///
/// Using a variable name for the data:
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[ws_from_stream(data)]
/// async fn handle_data(ctx: Context) {
///     // Data will be available in the `data` variable
/// }
/// ```
///
/// Using both buffer size and variable name:
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[ws_from_stream(1024, payload)]
/// async fn handle_large_data(ctx: Context) {
///     // Process large data with 1024 byte buffer, available in `payload` variable
/// }
/// ```
///
/// Reversing buffer size and variable name:
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[ws_from_stream(payload, 1024)]
/// async fn handle_reversed_data(ctx: Context) {
///     // Process data with 1024 byte buffer, available in `payload` variable
/// }
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
/// Using no parameters (default buffer size):
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[http_from_stream]
/// async fn handle_data(ctx: Context) {
///     // Process data from HTTP stream with default buffer size
/// }
/// ```
///
/// Basic usage with buffer size:
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[http_from_stream(1024)]
/// async fn handle_data(ctx: Context) {
///     // Process data from stream with 1024 byte buffer
/// }
/// ```
///
/// Using a variable name for the data:
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[http_from_stream(data)]
/// async fn handle_data(ctx: Context) {
///     // Data will be available in the `data` variable
/// }
/// ```
///
/// Using both buffer size and variable name:
/// ```rust
/// use hyperlane::*;
/// use hyperlane_macros::*;
///
/// #[http_from_stream(1024, payload)]
/// async fn handle_large_data(ctx: Context) {
///     // Process large data with 1024 byte buffer, available in `payload` variable
/// }
/// ```
#[proc_macro_attribute]
pub fn http_from_stream(attr: TokenStream, item: TokenStream) -> TokenStream {
    http_from_stream_macro(attr, item)
}

```

### 📄 File #274 - `fn.rs`
- **Path**: `hyperlane-macros\src\aborted\fn.rs`
- **Size**: `908 B`
- **Modified Time**: `2025-09-15T22:37:29.400036`

#### Content Preview

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

### 📄 File #275 - `mod.rs`
- **Path**: `hyperlane-macros\src\aborted\mod.rs`
- **Size**: `35 B`
- **Modified Time**: `2025-09-15T22:37:29.400036`

#### Content Preview

```rust
mod r#fn;

pub(crate) use r#fn::*;

```

### 📄 File #276 - `fn.rs`
- **Path**: `hyperlane-macros\src\closed\fn.rs`
- **Size**: `900 B`
- **Modified Time**: `2025-09-15T22:37:29.400036`

#### Content Preview

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

### 📄 File #277 - `mod.rs`
- **Path**: `hyperlane-macros\src\closed\mod.rs`
- **Size**: `35 B`
- **Modified Time**: `2025-09-15T22:37:29.400036`

#### Content Preview

```rust
mod r#fn;

pub(crate) use r#fn::*;

```

### 📄 File #278 - `enum.rs`
- **Path**: `hyperlane-macros\src\common\enum.rs`
- **Size**: `1,838 B`
- **Modified Time**: `2025-09-15T22:37:29.400036`

#### Content Preview

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

### 📄 File #279 - `fn.rs`
- **Path**: `hyperlane-macros\src\common\fn.rs`
- **Size**: `5,783 B`
- **Modified Time**: `2025-09-15T22:37:29.400831`

#### Content Preview

```rust
use crate::*;

/// Expands macro with code inserted before function body.
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
    match parse_context_from_fn(sig) {
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

/// Expands macro with code inserted after function body.
///
/// # Arguments
///
/// - `TokenStream` - The input `TokenStream` to process.
/// - `impl FnOnce(&Ident) -> TokenStream2` - A closure that takes a context identifier and returns a `TokenStream` to be inserted at the end of the function.
fn inject_at_end(input: TokenStream, after_fn: impl FnOnce(&Ident) -> TokenStream2) -> TokenStream {
    let input_fn: ItemFn = parse_macro_input!(input as ItemFn);
    let vis: &Visibility = &input_fn.vis;
    let sig: &Signature = &input_fn.sig;
    let block: &Block = &input_fn.block;
    let attrs: &Vec<Attribute> = &input_fn.attrs;
    match parse_context_from_fn(sig) {
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

/// Injects code into a function at a specified position.
///
/// # Arguments
///
/// - `Position` - The position at which to inject the code (`Prologue` or `Epilogue`).
/// - `TokenStream` - The input `TokenStream` of the function to modify.
/// - `impl FnOnce(&Ident) -> TokenStream2` - A closure that generates the code to be injected, based on the function's context identifier.
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

/// Checks if an expression is an integer literal.
///
/// # Arguments
///
/// - `expr` - The expression to check.
///
/// # Returns
///
/// - `bool` - Returns `true` if the expression is an integer literal, `false` otherwise.
pub(crate) fn is_integer_literal(expr: &Expr) -> bool {
    matches!(
        expr,
        Expr::Lit(ExprLit {
            lit: Lit::Int(_),
            ..
        })
    )
}

```

### 📄 File #280 - `impl.rs`
- **Path**: `hyperlane-macros\src\common\impl.rs`
- **Size**: `751 B`
- **Modified Time**: `2025-09-15T22:37:29.400831`

#### Content Preview

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

### 📄 File #281 - `mod.rs`
- **Path**: `hyperlane-macros\src\common\mod.rs`
- **Size**: `165 B`
- **Modified Time**: `2025-09-15T22:37:29.400831`

#### Content Preview

```rust
mod r#enum;
mod r#fn;
mod r#impl;
mod r#struct;
mod r#type;

pub(crate) use r#enum::*;
pub(crate) use r#fn::*;
pub(crate) use r#struct::*;
pub(crate) use r#type::*;

```

### 📄 File #282 - `struct.rs`
- **Path**: `hyperlane-macros\src\common\struct.rs`
- **Size**: `722 B`
- **Modified Time**: `2025-09-15T22:37:29.400831`

#### Content Preview

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

### 📄 File #283 - `type.rs`
- **Path**: `hyperlane-macros\src\common\type.rs`
- **Size**: `860 B`
- **Modified Time**: `2025-09-15T22:37:29.401339`

#### Content Preview

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

### 📄 File #284 - `fn.rs`
- **Path**: `hyperlane-macros\src\filter\fn.rs`
- **Size**: `1,060 B`
- **Modified Time**: `2025-09-15T22:37:29.401339`

#### Content Preview

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

### 📄 File #285 - `mod.rs`
- **Path**: `hyperlane-macros\src\filter\mod.rs`
- **Size**: `35 B`
- **Modified Time**: `2025-09-15T22:37:29.401339`

#### Content Preview

```rust
mod r#fn;

pub(crate) use r#fn::*;

```

### 📄 File #286 - `fn.rs`
- **Path**: `hyperlane-macros\src\flush\fn.rs`
- **Size**: `614 B`
- **Modified Time**: `2025-09-15T22:37:29.401339`

#### Content Preview

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

### 📄 File #287 - `mod.rs`
- **Path**: `hyperlane-macros\src\flush\mod.rs`
- **Size**: `35 B`
- **Modified Time**: `2025-09-15T22:37:29.401845`

#### Content Preview

```rust
mod r#fn;

pub(crate) use r#fn::*;

```

### 📄 File #288 - `impl.rs`
- **Path**: `hyperlane-macros\src\from_stream\impl.rs`
- **Size**: `4,623 B`
- **Modified Time**: `2025-09-15T22:37:29.401845`

#### Content Preview

```rust
use crate::*;

/// Implementation of Parse trait for FromStreamData.
///
/// This implementation handles parsing of macro attributes that specify stream processing parameters.
/// It supports various parameter combinations including buffer size, variable name, or both.
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
/// - Two buffer size parameters are provided
/// - Two variable name parameters are provided
/// - Additional unexpected tokens are present after valid parameters
/// - A comma is present without a second parameter following it
impl Parse for FromStreamData {
    /// Parses the input token stream into a FromStreamData structure.
    ///
    /// This method implements the core parsing logic for the FromStream macro attribute.
    /// It handles three possible parameter configurations:
    /// 1. Single parameter: interpreted as buffer size if integer literal, otherwise as variable name
    /// 2. Two parameters: first as buffer size, second as variable name (order independent)
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
    /// - Ok(FromStreamData) contains the successfully parsed data with buffer and variable name
    /// - Err(syn::Error) contains an appropriate error message for invalid input
    ///
    /// # Errors
    /// The function returns errors in the following cases:
    /// - Empty input: when no parameters are provided
    /// - Two integer literals: when both parameters are buffer sizes
    /// - Two non-integer expressions: when both parameters are variable names
    /// - Malformed syntax: when comma is present without a second parameter
    /// - Extra tokens: when additional tokens are present after valid parameters
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let mut buffer: Option<Expr> = None;
        let mut variable_name: Option<Expr> = None;
        if input.is_empty() {
            return Ok(FromStreamData {
                buffer,
                variable_name,
            });
        }
        let first_expr: Expr = input.parse()?;
        if input.is_empty() {
            if is_integer_literal(&first_expr) {
                buffer = Some(first_expr);
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
                        "cannot have two buffer size parameters",
                    ));
                }
                (false, false) => {
                    return Err(syn::Error::new_spanned(
                        &second_expr,
                        "cannot have two variable name parameters",
                    ));
                }
                (true, false) => {
                    buffer = Some(first_expr);
                    variable_name = Some(second_expr);
                }
                (false, true) => {
                    variable_name = Some(first_expr);
                    buffer = Some(second_expr);
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
            buffer,
            variable_name,
        })
    }
}

```

### 📄 File #289 - `mod.rs`
- **Path**: `hyperlane-macros\src\from_stream\mod.rs`
- **Size**: `55 B`
- **Modified Time**: `2025-09-15T22:37:29.401845`

#### Content Preview

```rust
mod r#impl;
mod r#struct;

pub(crate) use r#struct::*;

```

### 📄 File #290 - `struct.rs`
- **Path**: `hyperlane-macros\src\from_stream\struct.rs`
- **Size**: `348 B`
- **Modified Time**: `2025-09-15T22:37:29.401845`

#### Content Preview

```rust
use crate::*;

/// Represents data for stream processing.
///
/// This struct holds the buffer and variable name for stream processing.
pub(crate) struct FromStreamData {
    /// The buffer to read from the stream.
    pub(crate) buffer: Option<Expr>,
    /// The variable name to store the read data.
    pub(crate) variable_name: Option<Expr>,
}

```

### 📄 File #291 - `fn.rs`
- **Path**: `hyperlane-macros\src\hook\fn.rs`
- **Size**: `3,522 B`
- **Modified Time**: `2025-10-01T21:58:50.927240`

#### Content Preview

```rust
use crate::*;

/// Registers a panic hook.
///
/// This macro takes a function as input and registers it as a panic hook.
/// The registered function will be called when a panic occurs within the application.
///
/// # Arguments
///
/// - `TokenStream` - The attribute `TokenStream`, which can optionally specify an `order`.
/// - `TokenStream` - The input `TokenStream` representing the function to be registered as a hook.
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
    let input_fn: ItemFn = parse_macro_input!(item as ItemFn);
    let fn_name: &Ident = &input_fn.sig.ident;
    let gen_code: TokenStream2 = quote! {
        #input_fn
        inventory::submit! {
            ::hyperlane::HookMacro {
                hook_type: ::hyperlane::HookType::PanicHook(#order),
                handler: |ctx: ::hyperlane::Context| Box::pin(#fn_name(ctx)),
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

### 📄 File #292 - `mod.rs`
- **Path**: `hyperlane-macros\src\hook\mod.rs`
- **Size**: `35 B`
- **Modified Time**: `2025-09-15T22:37:29.402351`

#### Content Preview

```rust
mod r#fn;

pub(crate) use r#fn::*;

```

### 📄 File #293 - `fn.rs`
- **Path**: `hyperlane-macros\src\host\fn.rs`
- **Size**: `1,923 B`
- **Modified Time**: `2025-09-15T22:37:29.402351`

#### Content Preview

```rust
use crate::*;

/// Filters requests matching the specified host.
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
    let host_data: HostData = parse_macro_input!(attr as HostData);
    let host_value: Expr = host_data.host_value;
    inject(position, item, |context| {
        quote! {
            let request_host: ::hyperlane::RequestHost = #context.get_request_host().await;
            if request_host != #host_value.to_string() {
                return;
            }
        }
    })
}

inventory::submit! {
    InjectableMacro {
        name: "host",
        handler: Handler::WithAttrPosition(host_macro),
    }
}

/// Reject requests not matching the specified host.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with inverse host filter.
pub(crate) fn reject_host_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let host_data: HostData = parse_macro_input!(attr as HostData);
    let host_value: Expr = host_data.host_value;
    inject(position, item, |context| {
        quote! {
            let request_host: ::hyperlane::RequestHost = #context.get_request_host().await;
            if request_host == #host_value.to_string() {
                return;
            }
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

### 📄 File #294 - `impl.rs`
- **Path**: `hyperlane-macros\src\host\impl.rs`
- **Size**: `442 B`
- **Modified Time**: `2025-09-15T22:37:29.402858`

#### Content Preview

```rust
use crate::*;

/// Implementation of Parse trait for HostData.
///
/// Parses host value expression from input stream.
///
/// # Arguments
///
/// - `ParseStream` - The input parse stream.
///
/// # Returns
///
/// - `syn::Result<HostData>` - Parsed HostData or error.
impl Parse for HostData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let host_value: Expr = input.parse()?;
        Ok(HostData { host_value })
    }
}

```

### 📄 File #295 - `mod.rs`
- **Path**: `hyperlane-macros\src\host\mod.rs`
- **Size**: `122 B`
- **Modified Time**: `2025-09-15T22:37:29.402858`

#### Content Preview

```rust
pub(crate) mod r#fn;
pub(crate) mod r#impl;
pub(crate) mod r#struct;

pub(crate) use r#fn::*;
pub(crate) use r#struct::*;

```

### 📄 File #296 - `struct.rs`
- **Path**: `hyperlane-macros\src\host\struct.rs`
- **Size**: `240 B`
- **Modified Time**: `2025-09-15T22:37:29.402858`

#### Content Preview

```rust
use crate::*;

/// Host data container storing host value expression.
///
/// Used for host matching in request processing.
pub(crate) struct HostData {
    /// The host value expression to match against.
    pub(crate) host_value: Expr,
}

```

### 📄 File #297 - `fn.rs`
- **Path**: `hyperlane-macros\src\http\fn.rs`
- **Size**: `4,380 B`
- **Modified Time**: `2025-09-15T22:37:29.402858`

#### Content Preview

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

// Generates a handler that checks if the HTTP method is GET.
impl_http_method_macro!(get_handler, "get");

// Generates a handler that checks if the HTTP method is POST.
impl_http_method_macro!(epilogue_handler, "post");

// Generates a handler that checks if the HTTP method is PUT.
impl_http_method_macro!(put_handler, "put");

// Generates a handler that checks if the HTTP method is DELETE.
impl_http_method_macro!(delete_handler, "delete");

// Generates a handler that checks if the HTTP method is PATCH.
impl_http_method_macro!(patch_handler, "patch");

// Generates a handler that checks if the HTTP method is HEAD.
impl_http_method_macro!(head_handler, "head");

// Generates a handler that checks if the HTTP method is OPTIONS.
impl_http_method_macro!(options_handler, "options");

// Generates a handler that checks if the HTTP method is CONNECT.
impl_http_method_macro!(connect_handler, "connect");

// Generates a handler that checks if the HTTP method is TRACE.
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
    let check_method: Ident = Ident::new(&format!("is_{}", method_name), span);
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
    match parse_context_from_fn(sig) {
        Ok(context) => {
            let method_checks = methods.methods.iter().map(|method| {
                let check_fn: Ident = Ident::new(&format!("is_{}", method), method.span());
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

### 📄 File #298 - `mod.rs`
- **Path**: `hyperlane-macros\src\http\mod.rs`
- **Size**: `35 B`
- **Modified Time**: `2025-09-15T22:37:29.402858`

#### Content Preview

```rust
mod r#fn;

pub(crate) use r#fn::*;

```

### 📄 File #299 - `fn.rs`
- **Path**: `hyperlane-macros\src\hyperlane\fn.rs`
- **Size**: `2,078 B`
- **Modified Time**: `2025-09-15T22:37:29.403364`

#### Content Preview

```rust
use crate::*;

/// Main macro for creating and configuring a Hyperlane server instance.
///
/// This macro expects an attribute in the format `#[hyperlane(variable_name: TypeName)]`.
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
    let hyperlane_attr: HyperlaneAttr = parse_macro_input!(attr as HyperlaneAttr);
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
    let var_name: &Ident = &hyperlane_attr.var_name;
    let type_name: &Ident = &hyperlane_attr.type_name;
    init_statements.push(quote! {
        let #var_name: #type_name = #type_name::new().await;
    });
    if type_name == "Server" {
        init_statements.push(quote! {
            let mut hooks: Vec<::hyperlane::HookMacro> = inventory::iter().cloned().collect();
            assert_hook_unique_order(hooks.clone());
            hooks.sort_by_key(|hook| hook.hook_type.try_get());
            for hook in hooks {
                #var_name.handle_hook(hook.clone()).await;
            }
        });
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

### 📄 File #300 - `impl.rs`
- **Path**: `hyperlane-macros\src\hyperlane\impl.rs`
- **Size**: `623 B`
- **Modified Time**: `2025-09-15T22:37:29.403364`

#### Content Preview

```rust
use crate::*;

/// Implementation of the `Parse` trait for `HyperlaneAttr`.
///
/// This implementation allows parsing a `HyperlaneAttr` from a token stream,
/// expecting the format `variable_name: TypeName`.
///
/// # Arguments
///
/// - `ParseStream` - The `ParseStream` to parse from.
///
/// # Returns
///
/// A `syn::Result` containing the parsed `HyperlaneAttr` or an error.
impl Parse for HyperlaneAttr {
    fn parse(input: ParseStream) -> Result<Self> {
        Ok(HyperlaneAttr {
            var_name: input.parse()?,
            _colon: input.parse()?,
            type_name: input.parse()?,
        })
    }
}

```

### 📄 File #301 - `mod.rs`
- **Path**: `hyperlane-macros\src\hyperlane\mod.rs`
- **Size**: `122 B`
- **Modified Time**: `2025-09-15T22:37:29.403871`

#### Content Preview

```rust
pub(crate) mod r#fn;
pub(crate) mod r#impl;
pub(crate) mod r#struct;

pub(crate) use r#fn::*;
pub(crate) use r#struct::*;

```

### 📄 File #302 - `struct.rs`
- **Path**: `hyperlane-macros\src\hyperlane\struct.rs`
- **Size**: `466 B`
- **Modified Time**: `2025-09-15T22:37:29.403871`

#### Content Preview

```rust
use crate::*;

/// Represents the attribute for the Hyperlane macro.
///
/// It consists of a variable name and a type name, separated by `:`.
pub(crate) struct HyperlaneAttr {
    /// The variable name to assign the initialized component to.
    pub(crate) var_name: Ident,
    /// The colon token `:` separating the variable and type names.
    pub(crate) _colon: Token![:],
    /// The type name of the component to initialize.
    pub(crate) type_name: Ident,
}

```

### 📄 File #303 - `fn.rs`
- **Path**: `hyperlane-macros\src\inject\fn.rs`
- **Size**: `3,828 B`
- **Modified Time**: `2025-10-01T21:58:50.931329`

#### Content Preview

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
                        panic!("Macro {} does not take attributes", macro_name);
                    }
                    handler(item_stream, position)
                }
                Handler::WithAttrPosition(handler) => handler(macro_attr, item_stream, position),
            };
        }
    }
    panic!("Unsupported macro: {}", macro_name);
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
        .parse(attr.into())
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
        .parse(attr.into())
        .expect("Failed to parse macro attributes");
    let mut current_stream: TokenStream = item;
    for meta in metas.iter() {
        current_stream = apply_macro(meta, current_stream, Position::Epilogue);
    }
    current_stream
}

```

### 📄 File #304 - `mod.rs`
- **Path**: `hyperlane-macros\src\inject\mod.rs`
- **Size**: `46 B`
- **Modified Time**: `2025-09-15T22:37:29.404385`

#### Content Preview

```rust
pub(crate) mod r#fn;

pub(crate) use r#fn::*;

```

### 📄 File #305 - `fn.rs`
- **Path**: `hyperlane-macros\src\protocol\fn.rs`
- **Size**: `3,699 B`
- **Modified Time**: `2025-09-15T22:37:29.404385`

#### Content Preview

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

// Checks if the request is H2C protocol.
impl_protocol_check_macro!(h2c_macro, is_h2c, "h2c");

// Checks if the request is HTTP/0.9 protocol.
impl_protocol_check_macro!(http0_9_macro, is_http0_9, "http0_9");

// Checks if the request is HTTP/1.0 protocol.
impl_protocol_check_macro!(http1_0_macro, is_http1_0, "http1_0");

// Checks if the request is HTTP/1.1 protocol.
impl_protocol_check_macro!(http1_1_macro, is_http1_1, "http1_1");

// Checks if the request is HTTP/1.1 or higher protocol.
impl_protocol_check_macro!(
    http1_1_or_higher_macro,
    is_http1_1_or_higher,
    "http1_1_or_higher"
);

// Checks if the request is HTTP/2 protocol.
impl_protocol_check_macro!(http2_macro, is_http2, "http2");

// Checks if the request is HTTP/3 protocol.
impl_protocol_check_macro!(http3_macro, is_http3, "http3");

// Checks if the request is TLS protocol.
impl_protocol_check_macro!(tls_macro, is_tls, "tls");

```

### 📄 File #306 - `mod.rs`
- **Path**: `hyperlane-macros\src\protocol\mod.rs`
- **Size**: `35 B`
- **Modified Time**: `2025-09-15T22:37:29.404896`

#### Content Preview

```rust
mod r#fn;

pub(crate) use r#fn::*;

```

### 📄 File #307 - `fn.rs`
- **Path**: `hyperlane-macros\src\referer\fn.rs`
- **Size**: `2,267 B`
- **Modified Time**: `2025-09-15T22:37:29.404896`

#### Content Preview

```rust
use crate::*;

/// Filters requests matching the specified Referer header.
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
    let referer_data: RefererData = parse_macro_input!(attr as RefererData);
    let referer_value: Expr = referer_data.referer_value;
    inject(position, item, |context| {
        quote! {
            let referer: ::hyperlane::OptionRequestHeadersValueItem = #context.try_get_request_header_back(REFERER).await;
            if let Some(referer_header) = referer {
                if referer_header != #referer_value {
                    return;
                }
            } else {
                return;
            }
        }
    })
}

inventory::submit! {
    InjectableMacro {
        name: "referer",
        handler: Handler::WithAttrPosition(referer_macro),
    }
}

/// Reject requests not matching the specified Referer header.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream.
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with inverse Referer filter.
pub(crate) fn reject_referer_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let referer_data: RefererData = parse_macro_input!(attr as RefererData);
    let referer_value: Expr = referer_data.referer_value;
    inject(position, item, |context| {
        quote! {
            let referer: ::hyperlane::OptionRequestHeadersValueItem = #context.try_get_request_header_back(REFERER).await;
            if let Some(referer_header) = referer {
                if referer_header == #referer_value {
                    return;
                }
            }
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

### 📄 File #308 - `impl.rs`
- **Path**: `hyperlane-macros\src\referer\impl.rs`
- **Size**: `466 B`
- **Modified Time**: `2025-09-15T22:37:29.404896`

#### Content Preview

```rust
use crate::*;

/// Implementation of Parse trait for RefererData.
///
/// Parses referer value expression from input stream.
///
/// # Arguments
///
/// - `ParseStream` - The input parse stream.
///
/// # Returns
///
/// - `syn::Result<RefererData>` - Parsed RefererData or error.
impl Parse for RefererData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let referer_value: Expr = input.parse()?;
        Ok(RefererData { referer_value })
    }
}

```

### 📄 File #309 - `mod.rs`
- **Path**: `hyperlane-macros\src\referer\mod.rs`
- **Size**: `89 B`
- **Modified Time**: `2025-09-15T22:37:29.404896`

#### Content Preview

```rust
mod r#fn;
mod r#impl;
mod r#struct;

pub(crate) use r#fn::*;
pub(crate) use r#struct::*;

```

### 📄 File #310 - `struct.rs`
- **Path**: `hyperlane-macros\src\referer\struct.rs`
- **Size**: `265 B`
- **Modified Time**: `2025-09-15T22:37:29.405406`

#### Content Preview

```rust
use crate::*;

/// Referer data container storing referer value expression.
///
/// Used for Referer header matching in request processing.
pub(crate) struct RefererData {
    /// The referer value expression to match against.
    pub(crate) referer_value: Expr,
}

```

### 📄 File #311 - `fn.rs`
- **Path**: `hyperlane-macros\src\reject\fn.rs`
- **Size**: `1,041 B`
- **Modified Time**: `2025-09-15T22:37:29.405406`

#### Content Preview

```rust
use crate::*;

/// Rejects requests based on a boolean condition.
///
/// The function continues execution only if the provided code block returns `false`.
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

### 📄 File #312 - `mod.rs`
- **Path**: `hyperlane-macros\src\reject\mod.rs`
- **Size**: `35 B`
- **Modified Time**: `2025-09-15T22:37:29.405406`

#### Content Preview

```rust
mod r#fn;

pub(crate) use r#fn::*;

```

### 📄 File #313 - `fn.rs`
- **Path**: `hyperlane-macros\src\request\fn.rs`
- **Size**: `13,253 B`
- **Modified Time**: `2025-09-15T22:37:29.405406`

#### Content Preview

```rust
use crate::*;

/// Gets raw request body and assigns to specified variable.
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
    let body_param: RequestBodyData = parse_macro_input!(attr as RequestBodyData);
    let variable: Ident = body_param.variable;
    inject(position, item, |context| {
        quote! {
            let #variable: ::hyperlane::RequestBody = #context.get_request_body().await;
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
    let body_param: RequestBodyJsonData = parse_macro_input!(attr as RequestBodyJsonData);
    let variable: Ident = body_param.variable;
    let type_name: Type = body_param.type_name;
    inject(position, item, |context| {
        quote! {
            let #variable: ::hyperlane::ResultJsonError<#type_name> = #context.get_request_body_json::<#type_name>().await;
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
    let attribute: AttributeData = parse_macro_input!(attr as AttributeData);
    let variable: Ident = attribute.variable;
    let type_name: Type = attribute.type_name;
    let key_name: Expr = attribute.key_name;
    inject(position, item, |context| {
        quote! {
            let #variable: Option<#type_name> = #context.try_get_attribute(&#key_name).await;
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
    let attributes: AttributesData = parse_macro_input!(attr as AttributesData);
    let variable: Ident = attributes.variable;
    inject(position, item, |context| {
        quote! {
            let #variable: ::hyperlane::HashMapArcAnySendSync = #context.get_attributes().await;
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
    let route_param: RouteParamData = parse_macro_input!(attr as RouteParamData);
    let variable: Ident = route_param.variable;
    let key_name: Expr = route_param.key_name;
    inject(position, item, |context| {
        quote! {
            let #variable: ::hyperlane::OptionString = #context.try_get_route_param(#key_name).await;
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
    let route_params: RouteParamsData = parse_macro_input!(attr as RouteParamsData);
    let variable: Ident = route_params.variable;
    inject(position, item, |context| {
        quote! {
            let #variable: ::hyperlane::RouteParams = #context.get_route_params().await;
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
    let request_query: QueryData = parse_macro_input!(attr as QueryData);
    let variable: Ident = request_query.variable;
    let key_name: Expr = request_query.key_name;
    inject(position, item, |context| {
        quote! {
            let #variable: ::hyperlane::OptionRequestQuerysValue = #context.try_get_request_query(#key_name).await;
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
    let request_query: QuerysData = parse_macro_input!(attr as QuerysData);
    let variable: Ident = request_query.variable;
    inject(position, item, |context| {
        quote! {
            let #variable: ::hyperlane::RequestQuerys = #context.get_request_querys().await;
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
    let request_header: HeaderData = parse_macro_input!(attr as HeaderData);
    let variable: Ident = request_header.variable;
    let key_name: Expr = request_header.key_name;
    inject(position, item, |context| {
        quote! {
            let #variable: ::hyperlane::OptionRequestHeadersValueItem = #context.try_get_request_header_back(#key_name).await;
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
    let request_headers: HeadersData = parse_macro_input!(attr as HeadersData);
    let variable: Ident = request_headers.variable;
    inject(position, item, |context| {
        quote! {
            let #variable: ::hyperlane::RequestHeaders = #context.get_request_headers().await;
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
    let cookie_data: CookieData = parse_macro_input!(attr as CookieData);
    let variable: Ident = cookie_data.variable;
    let key: Expr = cookie_data.key_name;
    inject(position, item, |context| {
        quote! {
            let #variable: ::hyperlane::OptionCookiesValue = #context.try_get_request_cookie(#key).await;
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
    let cookies_data: CookiesData = parse_macro_input!(attr as CookiesData);
    let variable: Ident = cookies_data.variable;
    inject(position, item, |context| {
        quote! {
            let #variable: ::hyperlane::Cookies = #context.get_request_cookies().await;
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
    let version_data: RequestVersionData = parse_macro_input!(attr as RequestVersionData);
    let variable: Ident = version_data.variable;
    inject(position, item, |context| {
        quote! {
            let #variable: ::hyperlane::RequestVersion = #context.get_request_version().await;
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
    let path_data: RequestPathData = parse_macro_input!(attr as RequestPathData);
    let variable: Ident = path_data.variable;
    inject(position, item, |context| {
        quote! {
            let #variable: ::hyperlane::RequestPath = #context.get_request_path().await;
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

### 📄 File #314 - `impl.rs`
- **Path**: `hyperlane-macros\src\request\impl.rs`
- **Size**: `7,571 B`
- **Modified Time**: `2025-09-15T22:37:29.405922`

#### Content Preview

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

/// Implementation of Parse trait for RequestBodyData.
///
/// Parses request body variable from input stream.
///
/// # Arguments
///
/// - `ParseStream` - The input parse stream.
///
/// # Returns
///
/// - `syn::Result<RequestBodyData>` - Parsed RequestBodyData or error.
impl Parse for RequestBodyData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let variable: Ident = input.parse()?;
        Ok(RequestBodyData { variable })
    }
}

/// Implementation of Parse trait for RequestBodyJsonData.
///
/// Parses request body JSON variable and type from input stream.
///
/// # Arguments
///
/// - `ParseStream` - The input parse stream.
///
/// # Returns
///
/// - `syn::Result<RequestBodyJsonData>` - Parsed RequestBodyJsonData or error.
impl Parse for RequestBodyJsonData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let variable: Ident = input.parse()?;
        input.parse::<Token![:]>()?;
        let type_name: Type = input.parse()?;
        Ok(RequestBodyJsonData {
            variable,
            type_name,
        })
    }
}

/// Implementation of Parse trait for AttributeData.
///
/// Parses attribute key, variable and type from input stream.
///
/// # Arguments
///
/// - `ParseStream` - The input parse stream.
///
/// # Returns
///
/// - `syn::Result<AttributeData>` - Parsed AttributeData or error.
impl Parse for AttributeData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let key_name: Expr = input.parse()?;
        input.parse::<Token![=>]>()?;
        let variable: Ident = input.parse()?;
        input.parse::<Token![:]>()?;
        let type_name: Type = input.parse()?;
        Ok(AttributeData {
            variable,
            key_name,
            type_name,
        })
    }
}

/// Implementation of Parse trait for AttributesData.
///
/// Parses attributes variable from input stream.
///
/// # Arguments
///
/// - `ParseStream` - The input parse stream.
///
/// # Returns
///
/// - `syn::Result<AttributesData>` - Parsed AttributesData or error.
impl Parse for AttributesData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let variable: Ident = input.parse()?;
        Ok(AttributesData { variable })
    }
}

/// Implementation of Parse trait for RouteParamData.
///
/// Parses route parameter key and variable from input stream.
///
/// # Arguments
///
/// - `ParseStream` - The input parse stream.
///
/// # Returns
///
/// - `syn::Result<RouteParamData>` - Parsed RouteParamData or error.
impl Parse for RouteParamData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let key_name: Expr = input.parse()?;
        input.parse::<Token![=>]>()?;
        let variable: Ident = input.parse()?;
        Ok(RouteParamData { key_name, variable })
    }
}

/// Implementation of Parse trait for RouteParamsData.
///
/// Parses route parameters variable from input stream.
///
/// # Arguments
///
/// - `ParseStream` - The input parse stream.
///
/// # Returns
///
/// - `syn::Result<RouteParamsData>` - Parsed RouteParamsData or error.
impl Parse for RouteParamsData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let variable: Ident = input.parse()?;
        Ok(RouteParamsData { variable })
    }
}

/// Implementation of Parse trait for QueryData.
///
/// Parses query parameter key and variable from input stream.
///
/// # Arguments
///
/// - `ParseStream` - The input parse stream.
///
/// # Returns
///
/// - `syn::Result<QueryData>` - Parsed QueryData or error.
impl Parse for QueryData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let key_name: Expr = input.parse()?;
        input.parse::<Token![=>]>()?;
        let variable: Ident = input.parse()?;
        Ok(QueryData { key_name, variable })
    }
}

/// Implementation of Parse trait for QuerysData.
///
/// Parses query parameters variable from input stream.
///
/// # Arguments
///
/// - `ParseStream` - The input parse stream.
///
/// # Returns
///
/// - `syn::Result<QuerysData>` - Parsed QuerysData or error.
impl Parse for QuerysData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let variable: Ident = input.parse()?;
        Ok(QuerysData { variable })
    }
}

/// Implementation of Parse trait for HeaderData.
///
/// Parses header key and variable from input stream.
///
/// # Arguments
///
/// - `ParseStream` - The input parse stream.
///
/// # Returns
///
/// - `syn::Result<HeaderData>` - Parsed HeaderData or error.
impl Parse for HeaderData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let key_name: Expr = input.parse()?;
        input.parse::<Token![=>]>()?;
        let variable: Ident = input.parse()?;
        Ok(HeaderData { key_name, variable })
    }
}

/// Implementation of Parse trait for HeadersData.
///
/// Parses headers variable from input stream.
///
/// # Arguments
///
/// - `ParseStream` - The input parse stream.
///
/// # Returns
///
/// - `syn::Result<HeadersData>` - Parsed HeadersData or error.
impl Parse for HeadersData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let variable: Ident = input.parse()?;
        Ok(HeadersData { variable })
    }
}

/// Implementation of Parse trait for CookieData.
///
/// Parses cookie key and variable from input stream.
///
/// # Arguments
///
/// - `ParseStream` - The input parse stream.
///
/// # Returns
///
/// - `syn::Result<CookieData>` - Parsed CookieData or error.
impl Parse for CookieData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let key_name: Expr = input.parse()?;
        input.parse::<Token![=>]>()?;
        let variable: Ident = input.parse()?;
        Ok(CookieData { variable, key_name })
    }
}

/// Implementation of Parse trait for CookiesData.
///
/// Parses cookies variable from input stream.
///
/// # Arguments
///
/// - `ParseStream` - The input parse stream.
///
/// # Returns
///
/// - `syn::Result<CookiesData>` - Parsed CookiesData or error.
impl Parse for CookiesData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let variable: Ident = input.parse()?;
        Ok(CookiesData { variable })
    }
}

/// Implementation of Parse trait for RequestVersionData.
///
/// Parses request version variable from input stream.
///
/// # Arguments
///
/// - `ParseStream` - The input parse stream.
///
/// # Returns
///
/// - `syn::Result<RequestVersionData>` - Parsed RequestVersionData or error.
impl Parse for RequestVersionData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let variable: Ident = input.parse()?;
        Ok(RequestVersionData { variable })
    }
}

/// Implementation of Parse trait for RequestPathData.
///
/// Parses request path variable from input stream.
///
/// # Arguments
///
/// - `ParseStream` - The input parse stream.
///
/// # Returns
///
/// - `syn::Result<RequestPathData>` - Parsed RequestPathData or error.
impl Parse for RequestPathData {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let variable: Ident = input.parse()?;
        Ok(RequestPathData { variable })
    }
}

```

### 📄 File #315 - `mod.rs`
- **Path**: `hyperlane-macros\src\request\mod.rs`
- **Size**: `89 B`
- **Modified Time**: `2025-09-15T22:37:29.405922`

#### Content Preview

```rust
mod r#fn;
mod r#impl;
mod r#struct;

pub(crate) use r#fn::*;
pub(crate) use r#struct::*;

```

### 📄 File #316 - `struct.rs`
- **Path**: `hyperlane-macros\src\request\struct.rs`
- **Size**: `4,044 B`
- **Modified Time**: `2025-09-15T22:37:29.405922`

#### Content Preview

```rust
use crate::*;

/// Container for HTTP methods data.
///
/// Used to store parsed HTTP methods from macro input.
pub(crate) struct RequestMethods {
    /// The parsed HTTP methods as punctuated identifiers.
    pub(crate) methods: Punctuated<Ident, Token![,]>,
}

/// Container for raw request body data.
///
/// Used to store parsed request body variable from macro input.
pub(crate) struct RequestBodyData {
    /// The variable name to store the request body.
    pub(crate) variable: Ident,
}

/// Container for JSON request body data.
///
/// Used to store parsed JSON request body variable and type from macro input.
pub(crate) struct RequestBodyJsonData {
    /// The variable name to store the parsed JSON.
    pub(crate) variable: Ident,
    /// The type to parse the JSON into.
    pub(crate) type_name: Type,
}

/// Container for request attribute data.
///
/// Used to store parsed attribute key, variable and type from macro input.
pub(crate) struct AttributeData {
    /// The variable name to store the attribute value.
    pub(crate) variable: Ident,
    /// The type to parse the attribute into.
    pub(crate) type_name: Type,
    /// The attribute key name.
    pub(crate) key_name: Expr,
}

/// Container for request attributes data.
///
/// Used to store parsed attributes variable from macro input.
pub(crate) struct AttributesData {
    /// The variable name to store all attributes.
    pub(crate) variable: Ident,
}

/// Container for route parameter data.
///
/// Used to store parsed route parameter key and variable from macro input.
pub(crate) struct RouteParamData {
    /// The variable name to store the route parameter value.
    pub(crate) variable: Ident,
    /// The route parameter key name.
    pub(crate) key_name: Expr,
}

/// Container for route parameters data.
///
/// Used to store parsed route parameters variable from macro input.
pub(crate) struct RouteParamsData {
    /// The variable name to store all route parameters.
    pub(crate) variable: Ident,
}

/// Container for query parameter data.
///
/// Used to store parsed query parameter key and variable from macro input.
pub(crate) struct QueryData {
    /// The variable name to store the query parameter value.
    pub(crate) variable: Ident,
    /// The query parameter key name.
    pub(crate) key_name: Expr,
}

/// Container for query parameters data.
///
/// Used to store parsed query parameters variable from macro input.
pub(crate) struct QuerysData {
    /// The variable name to store all query parameters.
    pub(crate) variable: Ident,
}

/// Container for request header data.
///
/// Used to store parsed header key and variable from macro input.
pub(crate) struct HeaderData {
    /// The variable name to store the header value.
    pub(crate) variable: Ident,
    /// The header key name.
    pub(crate) key_name: Expr,
}

/// Container for request headers data.
///
/// Used to store parsed headers variable from macro input.
pub(crate) struct HeadersData {
    /// The variable name to store all headers.
    pub(crate) variable: Ident,
}

/// Container for request cookie data.
///
/// Used to store parsed cookie key and variable from macro input.
pub(crate) struct CookieData {
    /// The variable name to store the cookie value.
    pub(crate) variable: Ident,
    /// The cookie key name.
    pub(crate) key_name: Expr,
}

/// Container for request cookies data.
///
/// Used to store parsed cookies variable from macro input.
pub(crate) struct CookiesData {
    /// The variable name to store all cookies.
    pub(crate) variable: Ident,
}

/// Container for request version data.
///
/// Used to store parsed request version variable from macro input.
pub(crate) struct RequestVersionData {
    /// The variable name to store the request version.
    pub(crate) variable: Ident,
}

/// Container for request path data.
///
/// Used to store parsed request path variable from macro input.
pub(crate) struct RequestPathData {
    /// The variable name to store the request path.
    pub(crate) variable: Ident,
}

```

### 📄 File #317 - `fn.rs`
- **Path**: `hyperlane-macros\src\request_middleware\fn.rs`
- **Size**: `1,495 B`
- **Modified Time**: `2025-09-15T22:37:29.405922`

#### Content Preview

```rust
use crate::*;

/// Registers a request middleware.
///
/// This macro takes a function as input and registers it as a request middleware.
/// The registered function will be called before the main request handler.
///
/// # Arguments
///
/// - `TokenStream` - The attribute `TokenStream`, which can optionally specify an `order`.
/// - `TokenStream` - The input token stream representing the function to be registered as a middleware.
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
    let input_fn: ItemFn = parse_macro_input!(item as ItemFn);
    let fn_name: &Ident = &input_fn.sig.ident;
    let gen_code: TokenStream2 = quote! {
        #input_fn
        inventory::submit! {
            ::hyperlane::HookMacro {
                hook_type: ::hyperlane::HookType::RequestMiddleware(#order),
                handler: |ctx: ::hyperlane::Context| Box::pin(#fn_name(ctx)),
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

### 📄 File #318 - `mod.rs`
- **Path**: `hyperlane-macros\src\request_middleware\mod.rs`
- **Size**: `46 B`
- **Modified Time**: `2025-09-15T22:37:29.406432`

#### Content Preview

```rust
pub(crate) mod r#fn;

pub(crate) use r#fn::*;

```

### 📄 File #319 - `enum.rs`
- **Path**: `hyperlane-macros\src\response\enum.rs`
- **Size**: `260 B`
- **Modified Time**: `2025-09-15T22:37:29.406432`

#### Content Preview

```rust
/// Defines operations that can be performed on response headers.
pub(crate) enum HeaderOperation {
    /// Sets an existing header value, keeping the original if not present.
    Set,
    /// Add a new header value, overwriting any existing value.
    Add,
}

```

### 📄 File #320 - `fn.rs`
- **Path**: `hyperlane-macros\src\response\fn.rs`
- **Size**: `5,453 B`
- **Modified Time**: `2025-10-01T21:58:50.938057`

#### Content Preview

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

### 📄 File #321 - `impl.rs`
- **Path**: `hyperlane-macros\src\response\impl.rs`
- **Size**: `1,173 B`
- **Modified Time**: `2025-09-15T22:37:29.406432`

#### Content Preview

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

### 📄 File #322 - `mod.rs`
- **Path**: `hyperlane-macros\src\response\mod.rs`
- **Size**: `127 B`
- **Modified Time**: `2025-09-15T22:37:29.406944`

#### Content Preview

```rust
mod r#enum;
mod r#fn;
mod r#impl;
mod r#struct;

pub(crate) use r#enum::*;
pub(crate) use r#fn::*;
pub(crate) use r#struct::*;

```

### 📄 File #323 - `struct.rs`
- **Path**: `hyperlane-macros\src\response\struct.rs`
- **Size**: `185 B`
- **Modified Time**: `2025-09-15T22:37:29.406944`

#### Content Preview

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

### 📄 File #324 - `fn.rs`
- **Path**: `hyperlane-macros\src\response_middleware\fn.rs`
- **Size**: `1,532 B`
- **Modified Time**: `2025-09-15T22:37:29.406944`

#### Content Preview

```rust
use crate::*;

/// Registers a response middleware.
///
/// This macro takes a function as input and registers it as a response middleware.
/// The registered function will be called after the main request handler but before the response is sent.
///
/// # Arguments
///
/// - `TokenStream` - The attribute `TokenStream`, which can optionally specify an `order`.
/// - `TokenStream` - The input token stream representing the function to be registered as a middleware.
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
    let input_fn: ItemFn = parse_macro_input!(item as ItemFn);
    let fn_name: &Ident = &input_fn.sig.ident;
    let gen_code: TokenStream2 = quote! {
        #input_fn
        inventory::submit! {
            ::hyperlane::HookMacro {
                hook_type: ::hyperlane::HookType::ResponseMiddleware(#order),
                handler: |ctx: ::hyperlane::Context| Box::pin(#fn_name(ctx)),
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

### 📄 File #325 - `mod.rs`
- **Path**: `hyperlane-macros\src\response_middleware\mod.rs`
- **Size**: `46 B`
- **Modified Time**: `2025-09-15T22:37:29.406944`

#### Content Preview

```rust
pub(crate) mod r#fn;

pub(crate) use r#fn::*;

```

### 📄 File #326 - `fn.rs`
- **Path**: `hyperlane-macros\src\route\fn.rs`
- **Size**: `1,524 B`
- **Modified Time**: `2025-09-15T22:37:29.407503`

#### Content Preview

```rust
use crate::*;

/// Internal implementation for the `route` attribute macro.
///
/// This function processes the route attribute and generates code to register
/// the decorated function as a route handler in the inventory system.
///
/// # Arguments
///
/// - `TokenStream` - The attribute token stream containing route parameters (path and optional server)
/// - `TokenStream` - The function token stream being decorated
///
/// # Returns
///
/// A `TokenStream` containing the original function and inventory registration code
///
/// # Generated Code
///
/// The macro generates:
/// - The original function unchanged
/// - An `inventory::submit!` block that registers a `HookMacro` instance
/// - A handler closure that wraps the function in `Box::pin` for async execution
pub(crate) fn route_macro(attr: TokenStream, item: TokenStream) -> TokenStream {
    let route_attr: RouteAttr = parse_macro_input!(attr as RouteAttr);
    let path: &Expr = &route_attr.path;
    let input_fn: ItemFn = parse_macro_input!(item as ItemFn);
    let fn_name: &Ident = &input_fn.sig.ident;
    let gen_code: TokenStream2 = quote! {
        #input_fn
        inventory::submit! {
            ::hyperlane::HookMacro {
                hook_type: ::hyperlane::HookType::Route(#path),
                handler: |ctx: ::hyperlane::Context| Box::pin(#fn_name(ctx)),
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

### 📄 File #327 - `impl.rs`
- **Path**: `hyperlane-macros\src\route\impl.rs`
- **Size**: `384 B`
- **Modified Time**: `2025-09-15T22:37:29.407503`

#### Content Preview

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

### 📄 File #328 - `mod.rs`
- **Path**: `hyperlane-macros\src\route\mod.rs`
- **Size**: `122 B`
- **Modified Time**: `2025-09-15T22:37:29.407503`

#### Content Preview

```rust
pub(crate) mod r#fn;
pub(crate) mod r#impl;
pub(crate) mod r#struct;

pub(crate) use r#fn::*;
pub(crate) use r#struct::*;

```

### 📄 File #329 - `struct.rs`
- **Path**: `hyperlane-macros\src\route\struct.rs`
- **Size**: `293 B`
- **Modified Time**: `2025-09-15T22:37:29.407503`

#### Content Preview

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

### 📄 File #330 - `fn.rs`
- **Path**: `hyperlane-macros\src\send\fn.rs`
- **Size**: `5,213 B`
- **Modified Time**: `2025-09-15T22:37:29.407503`

#### Content Preview

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

/// Sends the response once with both headers and body (no keep-alive).
///
/// # Arguments
///
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with single send operation.
pub(crate) fn send_once_macro(item: TokenStream, position: Position) -> TokenStream {
    inject(position, item, |context| {
        quote! {
            let _ = #context.send_once().await;
        }
    })
}

inventory::submit! {
    InjectableMacro {
        name: "send_once",
        handler: Handler::NoAttrPosition(send_once_macro),
    }
}

/// Sends only the response body once (no keep-alive).
///
/// # Arguments
///
/// - `TokenStream` - The input token stream to process.
/// - `Position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with single body send operation.
pub(crate) fn send_body_once_macro(item: TokenStream, position: Position) -> TokenStream {
    inject(position, item, |context| {
        quote! {
            let _ = #context.send_body_once().await;
        }
    })
}

inventory::submit! {
    InjectableMacro {
        name: "send_body_once",
        handler: Handler::NoAttrPosition(send_body_once_macro),
    }
}

/// Sends the response with both headers and body with specified data.
///
/// # Arguments
///
/// - `attr` - The attribute token stream containing the data to send.
/// - `item` - The input token stream to process.
/// - `position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with send operation.
pub(crate) fn send_with_data_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let send_data: SendData = parse_macro_input!(attr as SendData);
    let data: Expr = send_data.data;
    inject(position, item, |context| {
        quote! {
            let _ = #context.send_with_data(#data).await;
        }
    })
}

inventory::submit! {
    InjectableMacro {
        name: "send_with_data",
        handler: Handler::WithAttrPosition(send_with_data_macro),
    }
}

/// Sends the response once with both headers and body with specified data (no keep-alive).
///
/// # Arguments
///
/// - `attr` - The attribute token stream containing the data to send.
/// - `item` - The input token stream to process.
/// - `position` - The position to inject the code.
///
/// # Returns
///
/// - `TokenStream` - The expanded token stream with single send operation.
pub(crate) fn send_once_with_data_macro(
    attr: TokenStream,
    item: TokenStream,
    position: Position,
) -> TokenStream {
    let send_data: SendData = parse_macro_input!(attr as SendData);
    let data: Expr = send_data.data;
    inject(position, item, |context| {
        quote! {
            let _ = #context.send_once_with_data(#data).await;
        }
    })
}

inventory::submit! {
    InjectableMacro {
        name: "send_once_with_data",
        handler: Handler::WithAttrPosition(send_once_with_data_macro),
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

### 📄 File #331 - `impl.rs`
- **Path**: `hyperlane-macros\src\send\impl.rs`
- **Size**: `276 B`
- **Modified Time**: `2025-09-15T22:37:29.407503`

#### Content Preview

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

### 📄 File #332 - `mod.rs`
- **Path**: `hyperlane-macros\src\send\mod.rs`
- **Size**: `89 B`
- **Modified Time**: `2025-09-15T22:37:29.407503`

#### Content Preview

```rust
mod r#fn;
mod r#impl;
mod r#struct;

pub(crate) use r#fn::*;
pub(crate) use r#struct::*;

```

### 📄 File #333 - `struct.rs`
- **Path**: `hyperlane-macros\src\send\struct.rs`
- **Size**: `596 B`
- **Modified Time**: `2025-09-15T22:37:29.407503`

#### Content Preview

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

### 📄 File #334 - `fn.rs`
- **Path**: `hyperlane-macros\src\stream\fn.rs`
- **Size**: `4,988 B`
- **Modified Time**: `2025-09-15T22:37:29.407503`

#### Content Preview

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
/// - `&FromStreamData` - The FromStreamData containing buffer size and variable name
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
    match (data.buffer.clone(), data.variable_name.clone()) {
        (Some(buffer), Some(variable_name)) => {
            quote! {
                while let Ok(#variable_name) = #context.#method_ident(#buffer).await {
                    #(#stmts)*
                }
            }
        }
        (Some(buffer), None) => {
            quote! {
                while #context.#method_ident(#buffer).await.is_ok() {
                    #(#stmts)*
                }
            }
        }
        (None, Some(variable_name)) => {
            quote! {
                while let Ok(#variable_name) = #context.#method_ident(::hyperlane::DEFAULT_BUFFER_SIZE).await {
                    #(#stmts)*
                }
            }
        }
        (None, None) => {
            quote! {
                while #context.#method_ident(::hyperlane::DEFAULT_BUFFER_SIZE).await.is_ok() {
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
/// - `TokenStream` - The attribute containing the buffer and variable name.
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
    match parse_context_from_fn(sig) {
        Ok(context) => {
            let stmts: &Vec<Stmt> = &block.stmts;
            let loop_stream: TokenStream2 =
                generate_stream(&context, "http_from_stream", &data, stmts);
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
/// - `attr` - The attribute containing the buffer and variable name.
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
    match parse_context_from_fn(sig) {
        Ok(context) => {
            let stmts: &Vec<Stmt> = &block.stmts;
            let loop_stream: TokenStream2 =
                generate_stream(&context, "ws_from_stream", &data, stmts);
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

### 📄 File #335 - `mod.rs`
- **Path**: `hyperlane-macros\src\stream\mod.rs`
- **Size**: `35 B`
- **Modified Time**: `2025-09-15T22:37:29.408506`

#### Content Preview

```rust
mod r#fn;

pub(crate) use r#fn::*;

```

### 📄 File #336 - `.gitignore`
- **Path**: `hyperlane-plugin-websocket\.gitignore`
- **Size**: `30 B`
- **Modified Time**: `2025-09-15T22:37:26.967372`

#### Content Preview



### 📄 File #337 - `Cargo.toml`
- **Path**: `hyperlane-plugin-websocket\Cargo.toml`
- **Size**: `865 B`
- **Modified Time**: `2025-10-01T21:58:44.941996`

#### Content Preview



### 📄 File #338 - `LICENSE`
- **Path**: `hyperlane-plugin-websocket\LICENSE`
- **Size**: `1,066 B`
- **Modified Time**: `2025-09-15T22:37:26.968377`

#### Content Preview



### 📄 File #339 - `README.md`
- **Path**: `hyperlane-plugin-websocket\README.md`
- **Size**: `9,289 B`
- **Modified Time**: `2025-09-15T22:37:26.968377`

#### Content Preview

```markdown
<center>

## hyperlane-plugin-websocket

[![](https://img.shields.io/crates/v/hyperlane-plugin-websocket.svg)](https://crates.io/crates/hyperlane-plugin-websocket)
[![](https://img.shields.io/crates/d/hyperlane-plugin-websocket.svg)](https://img.shields.io/crates/d/hyperlane-plugin-websocket.svg)
[![](https://docs.rs/hyperlane-plugin-websocket/badge.svg)](https://docs.rs/hyperlane-plugin-websocket)
[![](https://github.com/hyperlane-dev/hyperlane-plugin-websocket/workflows/Rust/badge.svg)](https://github.com/hyperlane-dev/hyperlane-plugin-websocket/actions?query=workflow:Rust)
[![](https://img.shields.io/crates/l/hyperlane-plugin-websocket.svg)](./LICENSE)

</center>

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

static BROADCAST_MAP: OnceLock<WebSocket> = OnceLock::new();

fn get_broadcast_map() -> &'static WebSocket {
    BROADCAST_MAP.get_or_init(|| WebSocket::new())
}

async fn request_middleware(ctx: Context) {
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

async fn connected_hook(ctx: Context) {
    let group_name: String = ctx
        .try_get_route_param("group_name")
        .await
        .unwrap_or_default();
    let group_broadcast_type: BroadcastType<String> = BroadcastType::PointToGroup(group_name);
    let receiver_count: ReceiverCount =
        get_broadcast_map().receiver_count_after_increment(group_broadcast_type.clone());
    let my_name: String = ctx.try_get_route_param("my_name").await.unwrap_or_default();
    let your_name: String = ctx
        .try_get_route_param("your_name")
        .await
        .unwrap_or_default();
    let private_broadcast_type: BroadcastType<String> =
        BroadcastType::PointToPoint(my_name, your_name);
    let data: String = format!("receiver_count => {:?}", receiver_count).into();
    tokio::spawn(async move {
        tokio::task::yield_now().await;
        get_broadcast_map()
            .send(group_broadcast_type, data.clone())
            .unwrap_or_else(|err| {
                println!("[connected_hook]send group error => {:?}", err.to_string());
                None
            });
        get_broadcast_map()
            .send(private_broadcast_type, data)
            .unwrap_or_else(|err| {
                println!(
                    "[connected_hook]send private error => {:?}",
                    err.to_string()
                );
                None
            });
    });
    println!("[connected_hook]receiver_count => {:?}", receiver_count);
    let _ = std::io::Write::flush(&mut std::io::stdout());
}

async fn group_chat_hook(ws_ctx: Context) {
    let group_name: String = ws_ctx.try_get_route_param("group_name").await.unwrap();
    let key: BroadcastType<String> = BroadcastType::PointToGroup(group_name);
    let mut receiver_count: ReceiverCount = get_broadcast_map().receiver_count(key.clone());
    let mut body: RequestBody = ws_ctx.get_request_body().await;
    if body.is_empty() {
        receiver_count = get_broadcast_map().receiver_count_after_decrement(key);
        body = format!("receiver_count => {:?}", receiver_count).into();
    }
    ws_ctx.set_response_body(&body).await;
    println!("[group_chat]receiver_count => {:?}", receiver_count);
    let _ = std::io::Write::flush(&mut std::io::stdout());
}

async fn group_closed(ctx: Context) {
    let group_name: String = ctx.try_get_route_param("group_name").await.unwrap();
    let key: BroadcastType<String> = BroadcastType::PointToGroup(group_name);
    let receiver_count: ReceiverCount =
        get_broadcast_map().receiver_count_after_decrement(key.clone());
    let body: String = format!("receiver_count => {:?}", receiver_count);
    ctx.set_response_body(&body).await;
    println!("[group_closed]receiver_count => {:?}", receiver_count);
    let _ = std::io::Write::flush(&mut std::io::stdout());
}

async fn private_chat_hook(ctx: Context) {
    let my_name: String = ctx.try_get_route_param("my_name").await.unwrap();
    let your_name: String = ctx.try_get_route_param("your_name").await.unwrap();
    let key: BroadcastType<String> = BroadcastType::PointToPoint(my_name, your_name);
    let mut receiver_count: ReceiverCount = get_broadcast_map().receiver_count(key.clone());
    let mut body: RequestBody = ctx.get_request_body().await;
    if body.is_empty() {
        receiver_count = get_broadcast_map().receiver_count_after_decrement(key);
        body = format!("receiver_count => {:?}", receiver_count).into();
    }
    ctx.set_response_body(&body).await;
    println!("[private_chat]receiver_count => {:?}", receiver_count);
    let _ = std::io::Write::flush(&mut std::io::stdout());
}

async fn private_closed(ctx: Context) {
    let my_name: String = ctx.try_get_route_param("my_name").await.unwrap();
    let your_name: String = ctx.try_get_route_param("your_name").await.unwrap();
    let key: BroadcastType<String> = BroadcastType::PointToPoint(my_name, your_name);
    let receiver_count: ReceiverCount = get_broadcast_map().receiver_count_after_decrement(key);
    let body: String = format!("receiver_count => {:?}", receiver_count);
    ctx.set_response_body(&body).await;
    println!("[private_closed]receiver_count => {:?}", receiver_count);
    let _ = std::io::Write::flush(&mut std::io::stdout());
}

async fn sended(ctx: Context) {
    let msg: String = ctx.get_response_body_string().await;
    println!("[sended_hook]msg => {}", msg);
    let _ = std::io::Write::flush(&mut std::io::stdout());
}

async fn private_chat(ctx: Context) {
    let my_name: String = ctx.try_get_route_param("my_name").await.unwrap();
    let your_name: String = ctx.try_get_route_param("your_name").await.unwrap();
    let key: BroadcastType<String> = BroadcastType::PointToPoint(my_name, your_name);
    let config: WebSocketConfig<String> = WebSocketConfig::new()
        .set_context(ctx.clone())
        .set_broadcast_type(key)
        .set_buffer_size(4096)
        .set_capacity(1024)
        .set_request_hook(private_chat_hook)
        .set_sended_hook(sended)
        .set_closed_hook(private_closed);
    get_broadcast_map().run(config).await;
}

async fn group_chat(ctx: Context) {
    let group_name: String = ctx.try_get_route_param("group_name").await.unwrap();
    let key: BroadcastType<String> = BroadcastType::PointToGroup(group_name);
    let config: WebSocketConfig<String> = WebSocketConfig::new()
        .set_context(ctx.clone())
        .set_broadcast_type(key)
        .set_buffer_size(4096)
        .set_capacity(1024)
        .set_request_hook(group_chat_hook)
        .set_sended_hook(sended)
        .set_closed_hook(group_closed);
    get_broadcast_map().run(config).await;
}

#[tokio::main]
async fn main() {
    let server: Server = Server::new().await;
    let config: ServerConfig = ServerConfig::new().await;
    config.host("0.0.0.0").await;
    config.port(60000).await;
    config.buffer(4096).await;
    config.disable_linger().await;
    config.disable_nodelay().await;
    server.config(config).await;
    server.route("/{group_name}", group_chat).await;
    server.route("/{my_name}/{your_name}", private_chat).await;
    server.request_middleware(request_middleware).await;
    server.request_middleware(upgrade_hook).await;
    server.request_middleware(connected_hook).await;
    let server_hook: ServerHook = server.run().await.unwrap_or_default();
    server_hook.wait().await;
}
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Contact

For any inquiries, please reach out to the author at [root@ltpp.vip](mailto:root@ltpp.vip).

```

### 📄 File #340 - `config`
- **Path**: `hyperlane-plugin-websocket\.git\config`
- **Size**: `336 B`
- **Modified Time**: `2025-09-15T22:37:26.959662`

#### Content Preview



### 📄 File #341 - `description`
- **Path**: `hyperlane-plugin-websocket\.git\description`
- **Size**: `73 B`
- **Modified Time**: `2025-09-15T22:37:22.216632`

#### Content Preview



### 📄 File #342 - `FETCH_HEAD`
- **Path**: `hyperlane-plugin-websocket\.git\FETCH_HEAD`
- **Size**: `253 B`
- **Modified Time**: `2025-10-01T21:58:44.904393`

#### Content Preview



### 📄 File #343 - `HEAD`
- **Path**: `hyperlane-plugin-websocket\.git\HEAD`
- **Size**: `23 B`
- **Modified Time**: `2025-09-15T22:37:26.951946`

#### Content Preview



### 📄 File #344 - `index`
- **Path**: `hyperlane-plugin-websocket\.git\index`
- **Size**: `1,392 B`
- **Modified Time**: `2025-10-01T21:58:44.941996`

#### Content Preview



### 📄 File #345 - `ORIG_HEAD`
- **Path**: `hyperlane-plugin-websocket\.git\ORIG_HEAD`
- **Size**: `41 B`
- **Modified Time**: `2025-09-15T22:44:20.979455`

#### Content Preview



### 📄 File #346 - `packed-refs`
- **Path**: `hyperlane-plugin-websocket\.git\packed-refs`
- **Size**: `114 B`
- **Modified Time**: `2025-09-15T22:37:26.941218`

#### Content Preview



### 📄 File #347 - `shallow`
- **Path**: `hyperlane-plugin-websocket\.git\shallow`
- **Size**: `41 B`
- **Modified Time**: `2025-09-15T22:37:26.875105`

#### Content Preview



### 📄 File #348 - `applypatch-msg.sample`
- **Path**: `hyperlane-plugin-websocket\.git\hooks\applypatch-msg.sample`
- **Size**: `478 B`
- **Modified Time**: `2025-09-15T22:37:22.217633`

#### Content Preview



### 📄 File #349 - `commit-msg.sample`
- **Path**: `hyperlane-plugin-websocket\.git\hooks\commit-msg.sample`
- **Size**: `896 B`
- **Modified Time**: `2025-09-15T22:37:22.217633`

#### Content Preview



### 📄 File #350 - `fsmonitor-watchman.sample`
- **Path**: `hyperlane-plugin-websocket\.git\hooks\fsmonitor-watchman.sample`
- **Size**: `4,726 B`
- **Modified Time**: `2025-09-15T22:37:22.217633`

#### Content Preview



### 📄 File #351 - `post-update.sample`
- **Path**: `hyperlane-plugin-websocket\.git\hooks\post-update.sample`
- **Size**: `189 B`
- **Modified Time**: `2025-09-15T22:37:22.217633`

#### Content Preview



### 📄 File #352 - `pre-applypatch.sample`
- **Path**: `hyperlane-plugin-websocket\.git\hooks\pre-applypatch.sample`
- **Size**: `424 B`
- **Modified Time**: `2025-09-15T22:37:22.218633`

#### Content Preview



### 📄 File #353 - `pre-commit.sample`
- **Path**: `hyperlane-plugin-websocket\.git\hooks\pre-commit.sample`
- **Size**: `1,649 B`
- **Modified Time**: `2025-09-15T22:37:22.218633`

#### Content Preview



### 📄 File #354 - `pre-merge-commit.sample`
- **Path**: `hyperlane-plugin-websocket\.git\hooks\pre-merge-commit.sample`
- **Size**: `416 B`
- **Modified Time**: `2025-09-15T22:37:22.218633`

#### Content Preview



### 📄 File #355 - `pre-push.sample`
- **Path**: `hyperlane-plugin-websocket\.git\hooks\pre-push.sample`
- **Size**: `1,374 B`
- **Modified Time**: `2025-09-15T22:37:22.219235`

#### Content Preview



### 📄 File #356 - `pre-rebase.sample`
- **Path**: `hyperlane-plugin-websocket\.git\hooks\pre-rebase.sample`
- **Size**: `4,898 B`
- **Modified Time**: `2025-09-15T22:37:22.219235`

#### Content Preview



### 📄 File #357 - `pre-receive.sample`
- **Path**: `hyperlane-plugin-websocket\.git\hooks\pre-receive.sample`
- **Size**: `544 B`
- **Modified Time**: `2025-09-15T22:37:22.219235`

#### Content Preview



### 📄 File #358 - `prepare-commit-msg.sample`
- **Path**: `hyperlane-plugin-websocket\.git\hooks\prepare-commit-msg.sample`
- **Size**: `1,492 B`
- **Modified Time**: `2025-09-15T22:37:22.219235`

#### Content Preview



### 📄 File #359 - `push-to-checkout.sample`
- **Path**: `hyperlane-plugin-websocket\.git\hooks\push-to-checkout.sample`
- **Size**: `2,783 B`
- **Modified Time**: `2025-09-15T22:37:22.219235`

#### Content Preview



### 📄 File #360 - `sendemail-validate.sample`
- **Path**: `hyperlane-plugin-websocket\.git\hooks\sendemail-validate.sample`
- **Size**: `2,308 B`
- **Modified Time**: `2025-09-15T22:37:22.220242`

#### Content Preview



### 📄 File #361 - `update.sample`
- **Path**: `hyperlane-plugin-websocket\.git\hooks\update.sample`
- **Size**: `3,650 B`
- **Modified Time**: `2025-09-15T22:37:22.220242`

#### Content Preview



### 📄 File #362 - `exclude`
- **Path**: `hyperlane-plugin-websocket\.git\info\exclude`
- **Size**: `240 B`
- **Modified Time**: `2025-09-15T22:37:22.220242`

#### Content Preview



### 📄 File #363 - `HEAD`
- **Path**: `hyperlane-plugin-websocket\.git\logs\HEAD`
- **Size**: `354 B`
- **Modified Time**: `2025-10-01T21:58:44.952992`

#### Content Preview



### 📄 File #364 - `master`
- **Path**: `hyperlane-plugin-websocket\.git\logs\refs\heads\master`
- **Size**: `354 B`
- **Modified Time**: `2025-10-01T21:58:44.952992`

#### Content Preview



### 📄 File #365 - `HEAD`
- **Path**: `hyperlane-plugin-websocket\.git\logs\refs\remotes\origin\HEAD`
- **Size**: `201 B`
- **Modified Time**: `2025-09-15T22:37:26.951442`

#### Content Preview



### 📄 File #366 - `master`
- **Path**: `hyperlane-plugin-websocket\.git\logs\refs\remotes\origin\master`
- **Size**: `153 B`
- **Modified Time**: `2025-10-01T21:58:44.895381`

#### Content Preview



### 📄 File #367 - `1ebda971d1d3c8b4d205161947f4443db69fc2`
- **Path**: `hyperlane-plugin-websocket\.git\objects\3b\1ebda971d1d3c8b4d205161947f4443db69fc2`
- **Size**: `483 B`
- **Modified Time**: `2025-10-01T21:58:44.861316`

#### Content Preview



### 📄 File #368 - `02374d2dd7a71741b253bd66472f5871f583c4`
- **Path**: `hyperlane-plugin-websocket\.git\objects\ac\02374d2dd7a71741b253bd66472f5871f583c4`
- **Size**: `211 B`
- **Modified Time**: `2025-10-01T21:58:44.859311`

#### Content Preview



### 📄 File #369 - `1ec4265467905506ee79fcf99353ecbfa518a7`
- **Path**: `hyperlane-plugin-websocket\.git\objects\cb\1ec4265467905506ee79fcf99353ecbfa518a7`
- **Size**: `167 B`
- **Modified Time**: `2025-10-01T21:58:44.857924`

#### Content Preview



### 📄 File #370 - `pack-b689ea47ecc3a85a58f612de92d096d3fa73fd1c.idx`
- **Path**: `hyperlane-plugin-websocket\.git\objects\pack\pack-b689ea47ecc3a85a58f612de92d096d3fa73fd1c.idx`
- **Size**: `1,660 B`
- **Modified Time**: `2025-09-15T22:37:26.906923`

#### Content Preview



### 📄 File #371 - `pack-b689ea47ecc3a85a58f612de92d096d3fa73fd1c.pack`
- **Path**: `hyperlane-plugin-websocket\.git\objects\pack\pack-b689ea47ecc3a85a58f612de92d096d3fa73fd1c.pack`
- **Size**: `12,964 B`
- **Modified Time**: `2025-09-15T22:37:26.906410`

#### Content Preview



### 📄 File #372 - `pack-b689ea47ecc3a85a58f612de92d096d3fa73fd1c.rev`
- **Path**: `hyperlane-plugin-websocket\.git\objects\pack\pack-b689ea47ecc3a85a58f612de92d096d3fa73fd1c.rev`
- **Size**: `136 B`
- **Modified Time**: `2025-09-15T22:37:26.907950`

#### Content Preview



### 📄 File #373 - `master`
- **Path**: `hyperlane-plugin-websocket\.git\refs\heads\master`
- **Size**: `41 B`
- **Modified Time**: `2025-10-01T21:58:44.952394`

#### Content Preview



### 📄 File #374 - `HEAD`
- **Path**: `hyperlane-plugin-websocket\.git\refs\remotes\origin\HEAD`
- **Size**: `32 B`
- **Modified Time**: `2025-09-15T22:37:26.950418`

#### Content Preview



### 📄 File #375 - `master`
- **Path**: `hyperlane-plugin-websocket\.git\refs\remotes\origin\master`
- **Size**: `41 B`
- **Modified Time**: `2025-10-01T21:58:44.894357`

#### Content Preview



### 📄 File #376 - `v2.2.63`
- **Path**: `hyperlane-plugin-websocket\.git\refs\tags\v2.2.63`
- **Size**: `41 B`
- **Modified Time**: `2025-09-15T22:37:26.949404`

#### Content Preview



### 📄 File #377 - `v2.2.64`
- **Path**: `hyperlane-plugin-websocket\.git\refs\tags\v2.2.64`
- **Size**: `41 B`
- **Modified Time**: `2025-10-01T21:58:44.895984`

#### Content Preview



### 📄 File #378 - `rust.yml`
- **Path**: `hyperlane-plugin-websocket\.github\workflows\rust.yml`
- **Size**: `9,636 B`
- **Modified Time**: `2025-09-15T22:37:26.967372`

#### Content Preview

```yaml
name: Rust
on:
  push:
    branches: [master]
env:
  CARGO_TERM_COLOR: always
jobs:
  setup:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.read.outputs.version }}
      tag: ${{ steps.read.outputs.tag }}
      package_name: ${{ steps.read.outputs.package_name }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Install rust-toolchain
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
          components: rustfmt, clippy
      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: |
            ~/.cargo/registry
            ~/.cargo/git
            target
          key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}
      - name: Install toml-cli
        run: cargo install toml-cli
      - name: Cache toml-cli
        uses: actions/cache@v3
        with:
          path: ~/.cargo/bin/toml
          key: toml-cli-${{ runner.os }}
      - name: Read cargo metadata
        id: read
        run: |
          VERSION=$(toml get Cargo.toml package.version --raw)
          PACKAGE_NAME=$(toml get Cargo.toml package.name --raw)
          echo "📦 Detected package: $PACKAGE_NAME v$VERSION"
          if [ -z "$VERSION" ] || [ -z "$PACKAGE_NAME" ]; then
            echo "❌ Failed to read package info from Cargo.toml"
          fi
          echo "version=$VERSION" >> $GITHUB_OUTPUT
          echo "tag=v$VERSION" >> $GITHUB_OUTPUT
          echo "package_name=$PACKAGE_NAME" >> $GITHUB_OUTPUT

  check:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup rust
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
          components: rustfmt
      - name: Format check
        run: cargo fmt -- --check

  tests:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Prepare environment
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
      - name: Run tests
        run: cargo test --all-features -- --nocapture

  clippy:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Load clippy
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
          components: clippy
      - name: Run clippy
        run: cargo clippy --all-features -- -A warnings

  build:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup build
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
      - name: Build release
        run: cargo check --release --all-features

  publish:
    needs: [setup, check, tests, clippy, build]
    if: needs.setup.outputs.tag != ''
    runs-on: ubuntu-latest
    outputs:
      published: ${{ steps.publish.outputs.published }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Restore toml-cli
        uses: actions/cache@v3
        with:
          path: ~/.cargo/bin/toml
          key: toml-cli-${{ runner.os }}
      - name: Publish to crates.io
        id: publish
        env:
          CARGO_REGISTRY_TOKEN: ${{ secrets.CARGO_REGISTRY_TOKEN }}
        run: |
          set -e
          echo "published=false" >> $GITHUB_OUTPUT
          echo "${{ secrets.CARGO_REGISTRY_TOKEN }}" | cargo login
          PACKAGE_NAME=$(toml get Cargo.toml package.name --raw)
          VERSION=${{ needs.setup.outputs.version }}
          if cargo publish --allow-dirty; then
            echo "published=true" >> $GITHUB_OUTPUT
            echo "🎉🎉🎉 PUBLISH SUCCESSFUL 🎉🎉🎉"
            echo "✅ Successfully published $PACKAGE_NAME v$VERSION to crates.io"
            echo "📦 Crates.io: [https://crates.io/crates/$PACKAGE_NAME/$VERSION](https://crates.io/crates/$PACKAGE_NAME/$VERSION)"
            echo "📚 Docs.rs: [https://docs.rs/$PACKAGE_NAME/$VERSION](https://docs.rs/$PACKAGE_NAME/$VERSION)"
          else
            echo "❌ Publish failed"
          fi

  release:
    needs: [setup, check, tests, clippy, build]
    permissions:
      contents: write
      packages: write
    if: needs.setup.outputs.tag != ''
    runs-on: ubuntu-latest
    outputs:
      released: ${{ steps.release.outputs.released }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Get package name
        id: package_info
        run: |
          echo "package_name=${{ needs.setup.outputs.package_name }}" >> $GITHUB_OUTPUT
      - name: Check tag status
        id: check_tag
        run: |
          if git tag -l | grep -q "^${{ needs.setup.outputs.tag }}$"; then
            echo "tag_exists=true" >> $GITHUB_OUTPUT
            echo "🏷️ Tag ${{ needs.setup.outputs.tag }} exists locally"
          else
            echo "tag_exists=false" >> $GITHUB_OUTPUT
            echo "🏷️ Tag ${{ needs.setup.outputs.tag }} does not exist locally"
          fi
          if git ls-remote --tags origin | grep -q "refs/tags/${{ needs.setup.outputs.tag }}$"; then
            echo "remote_tag_exists=true" >> $GITHUB_OUTPUT
            echo "🌐 Tag ${{ needs.setup.outputs.tag }} exists on remote"
          else
            echo "remote_tag_exists=false" >> $GITHUB_OUTPUT
            echo "🌐 Tag ${{ needs.setup.outputs.tag }} does not exist on remote"
          fi
      - name: Check release status
        id: check_release
        run: |
          if gh release view "${{ needs.setup.outputs.tag }}" > /dev/null 2>&1; then
            echo "release_exists=true" >> $GITHUB_OUTPUT
            echo "📦 Release ${{ needs.setup.outputs.tag }} already exists"
          else
            echo "release_exists=false" >> $GITHUB_OUTPUT
            echo "📦 Release ${{ needs.setup.outputs.tag }} does not exist"
          fi
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - name: Create or update release
        id: release
        run: |
          set -e
          echo "released=false" >> $GITHUB_OUTPUT
          PACKAGE_NAME="${{ steps.package_info.outputs.package_name }}"
          VERSION="${{ needs.setup.outputs.version }}"
          TAG="${{ needs.setup.outputs.tag }}"
          echo "📦 Building source archives..."
          git archive --format=zip --prefix="${PACKAGE_NAME}-${VERSION}/" HEAD > "${PACKAGE_NAME}-${VERSION}.zip"
          git archive --format=tar.gz --prefix="${PACKAGE_NAME}-${VERSION}/" HEAD > "${PACKAGE_NAME}-${VERSION}.tar.gz"
          if [ "${{ steps.check_release.outputs.release_exists }}" = "true" ]; then
            echo "🔄 Updating existing release: $TAG"
            gh release view "$TAG" --json assets --jq '.assets[].name' | while read asset; do
              if [ -n "$asset" ]; then
                echo "🗑️ Deleting asset: $asset"
                gh release delete-asset "$TAG" "$asset" --yes || true
              fi
            done
            if gh release edit "$TAG" \
              --title "$TAG (Updated $(date '+%Y-%m-%d %H:%M:%S'))" \
              --notes "Release $TAG - Updated at $(date '+%Y-%m-%d %H:%M:%S UTC')
            ## Changes
            - Version: $VERSION
            - Package: $PACKAGE_NAME
            ## Links
            📦 [Crate on crates.io](https://crates.io/crates/$PACKAGE_NAME/$VERSION)
            📚 [Documentation on docs.rs](https://docs.rs/$PACKAGE_NAME/$VERSION)
            📋 [Commit History](https://github.com/${{ github.repository }}/commits/$TAG)" && \
               gh release upload "$TAG" "${PACKAGE_NAME}-${VERSION}.zip" "${PACKAGE_NAME}-${VERSION}.tar.gz" --clobber; then
              echo "released=true" >> $GITHUB_OUTPUT
              echo "✅ Updated release $TAG"
              echo "🔖 Tag: $TAG"
              echo "🚀 Release: [GitHub Release](${{ github.server_url }}/${{ github.repository }}/releases/tag/$TAG)"
            else
              echo "❌ Failed to update release"
            fi
          else
            if [ "${{ steps.check_tag.outputs.remote_tag_exists }}" = "false" ]; then
              echo "🏷️ Creating and pushing tag: $TAG"
              git tag "$TAG"
              git push origin "$TAG"
            fi
            echo "🆕 Creating new release: $TAG"
            if gh release create "$TAG" \
              --title "$TAG (Created $(date '+%Y-%m-%d %H:%M:%S'))" \
              --notes "Release $TAG - Created at $(date '+%Y-%m-%d %H:%M:%S UTC')
            ## Changes
            - Version: $VERSION
            - Package: $PACKAGE_NAME
            ## Links
            📦 [Crate on crates.io](https://crates.io/crates/$PACKAGE_NAME/$VERSION)
            📚 [Documentation on docs.rs](https://docs.rs/$PACKAGE_NAME/$VERSION)
            📋 [Commit History](https://github.com/${{ github.repository }}/commits/$TAG)" \
              --latest && \
               gh release upload "$TAG" "${PACKAGE_NAME}-${VERSION}.zip" "${PACKAGE_NAME}-${VERSION}.tar.gz"; then
              echo "released=true" >> $GITHUB_OUTPUT
              echo "✅ Created release $TAG"
              echo "🔖 Tag: $TAG"
              echo "🚀 Release: [GitHub Release](${{ github.server_url }}/${{ github.repository }}/releases/tag/$TAG)"
            else
              echo "❌ Failed to create release"
            fi
          fi
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

```

### 📄 File #379 - `lib.rs`
- **Path**: `hyperlane-plugin-websocket\src\lib.rs`
- **Size**: `850 B`
- **Modified Time**: `2025-09-15T22:37:26.968880`

#### Content Preview

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

### 📄 File #380 - `cfg.rs`
- **Path**: `hyperlane-plugin-websocket\src\tests\cfg.rs`
- **Size**: `8,850 B`
- **Modified Time**: `2025-09-15T22:37:26.969414`

#### Content Preview

```rust
use crate::*;

#[tokio::test]
async fn test() {
    static BROADCAST_MAP: OnceLock<WebSocket> = OnceLock::new();

    fn get_broadcast_map() -> &'static WebSocket {
        BROADCAST_MAP.get_or_init(|| WebSocket::new())
    }

    async fn request_middleware(ctx: Context) {
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

    async fn connected_hook(ctx: Context) {
        let group_name: String = ctx
            .try_get_route_param("group_name")
            .await
            .unwrap_or_default();
        let group_broadcast_type: BroadcastType<String> = BroadcastType::PointToGroup(group_name);
        let receiver_count: ReceiverCount =
            get_broadcast_map().receiver_count_after_increment(group_broadcast_type.clone());
        let my_name: String = ctx.try_get_route_param("my_name").await.unwrap_or_default();
        let your_name: String = ctx
            .try_get_route_param("your_name")
            .await
            .unwrap_or_default();
        let private_broadcast_type: BroadcastType<String> =
            BroadcastType::PointToPoint(my_name, your_name);
        let data: String = format!("receiver_count => {:?}", receiver_count).into();
        tokio::spawn(async move {
            tokio::task::yield_now().await;
            get_broadcast_map()
                .send(group_broadcast_type, data.clone())
                .unwrap_or_else(|err| {
                    println!("[connected_hook]send group error => {:?}", err.to_string());
                    None
                });
            get_broadcast_map()
                .send(private_broadcast_type, data)
                .unwrap_or_else(|err| {
                    println!(
                        "[connected_hook]send private error => {:?}",
                        err.to_string()
                    );
                    None
                });
        });
        println!("[connected_hook]receiver_count => {:?}", receiver_count);
        let _ = std::io::Write::flush(&mut std::io::stdout());
    }

    async fn group_chat_hook(ws_ctx: Context) {
        let group_name: String = ws_ctx.try_get_route_param("group_name").await.unwrap();
        let key: BroadcastType<String> = BroadcastType::PointToGroup(group_name);
        let mut receiver_count: ReceiverCount = get_broadcast_map().receiver_count(key.clone());
        let mut body: RequestBody = ws_ctx.get_request_body().await;
        if body.is_empty() {
            receiver_count = get_broadcast_map().receiver_count_after_decrement(key);
            body = format!("receiver_count => {:?}", receiver_count).into();
        }
        ws_ctx.set_response_body(&body).await;
        println!("[group_chat]receiver_count => {:?}", receiver_count);
        let _ = std::io::Write::flush(&mut std::io::stdout());
    }

    async fn group_closed(ctx: Context) {
        let group_name: String = ctx.try_get_route_param("group_name").await.unwrap();
        let key: BroadcastType<String> = BroadcastType::PointToGroup(group_name);
        let receiver_count: ReceiverCount =
            get_broadcast_map().receiver_count_after_decrement(key.clone());
        let body: String = format!("receiver_count => {:?}", receiver_count);
        ctx.set_response_body(&body).await;
        println!("[group_closed]receiver_count => {:?}", receiver_count);
        let _ = std::io::Write::flush(&mut std::io::stdout());
    }

    async fn private_chat_hook(ctx: Context) {
        let my_name: String = ctx.try_get_route_param("my_name").await.unwrap();
        let your_name: String = ctx.try_get_route_param("your_name").await.unwrap();
        let key: BroadcastType<String> = BroadcastType::PointToPoint(my_name, your_name);
        let mut receiver_count: ReceiverCount = get_broadcast_map().receiver_count(key.clone());
        let mut body: RequestBody = ctx.get_request_body().await;
        if body.is_empty() {
            receiver_count = get_broadcast_map().receiver_count_after_decrement(key);
            body = format!("receiver_count => {:?}", receiver_count).into();
        }
        ctx.set_response_body(&body).await;
        println!("[private_chat]receiver_count => {:?}", receiver_count);
        let _ = std::io::Write::flush(&mut std::io::stdout());
    }

    async fn private_closed(ctx: Context) {
        let my_name: String = ctx.try_get_route_param("my_name").await.unwrap();
        let your_name: String = ctx.try_get_route_param("your_name").await.unwrap();
        let key: BroadcastType<String> = BroadcastType::PointToPoint(my_name, your_name);
        let receiver_count: ReceiverCount = get_broadcast_map().receiver_count_after_decrement(key);
        let body: String = format!("receiver_count => {:?}", receiver_count);
        ctx.set_response_body(&body).await;
        println!("[private_closed]receiver_count => {:?}", receiver_count);
        let _ = std::io::Write::flush(&mut std::io::stdout());
    }

    async fn sended(ctx: Context) {
        let msg: String = ctx.get_response_body_string().await;
        println!("[sended_hook]msg => {}", msg);
        let _ = std::io::Write::flush(&mut std::io::stdout());
    }

    async fn private_chat(ctx: Context) {
        let my_name: String = ctx.try_get_route_param("my_name").await.unwrap();
        let your_name: String = ctx.try_get_route_param("your_name").await.unwrap();
        let key: BroadcastType<String> = BroadcastType::PointToPoint(my_name, your_name);
        let config: WebSocketConfig<String> = WebSocketConfig::new()
            .set_context(ctx.clone())
            .set_broadcast_type(key)
            .set_buffer_size(4096)
            .set_capacity(1024)
            .set_request_hook(private_chat_hook)
            .set_sended_hook(sended)
            .set_closed_hook(private_closed);
        get_broadcast_map().run(config).await;
    }

    async fn group_chat(ctx: Context) {
        let group_name: String = ctx.try_get_route_param("group_name").await.unwrap();
        let key: BroadcastType<String> = BroadcastType::PointToGroup(group_name);
        let config: WebSocketConfig<String> = WebSocketConfig::new()
            .set_context(ctx.clone())
            .set_broadcast_type(key)
            .set_buffer_size(4096)
            .set_capacity(1024)
            .set_request_hook(group_chat_hook)
            .set_sended_hook(sended)
            .set_closed_hook(group_closed);
        get_broadcast_map().run(config).await;
    }

    async fn main() {
        let server: Server = Server::new().await;
        let config: ServerConfig = ServerConfig::new().await;
        config.host("0.0.0.0").await;
        config.port(60000).await;
        config.buffer(4096).await;
        config.disable_linger().await;
        config.disable_nodelay().await;
        server.config(config).await;
        server.route("/{group_name}", group_chat).await;
        server.route("/{my_name}/{your_name}", private_chat).await;
        server.request_middleware(request_middleware).await;
        server.request_middleware(upgrade_hook).await;
        server.request_middleware(connected_hook).await;
        let server_hook: ServerHook = server.run().await.unwrap_or_default();
        let server_hook_clone: ServerHook = server_hook.clone();
        tokio::spawn(async move {
            tokio::time::sleep(std::time::Duration::from_secs(60)).await;
            server_hook.shutdown().await;
        });
        server_hook_clone.wait().await;
    }

    let _ = tokio::time::timeout(std::time::Duration::from_secs(60), main()).await;
}

```

### 📄 File #381 - `mod.rs`
- **Path**: `hyperlane-plugin-websocket\src\tests\mod.rs`
- **Size**: `9 B`
- **Modified Time**: `2025-09-15T22:37:26.969414`

#### Content Preview

```rust
mod cfg;

```

### 📄 File #382 - `const.rs`
- **Path**: `hyperlane-plugin-websocket\src\websocket\const.rs`
- **Size**: `418 B`
- **Modified Time**: `2025-09-15T22:37:26.969414`

#### Content Preview

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

### 📄 File #383 - `enum.rs`
- **Path**: `hyperlane-plugin-websocket\src\websocket\enum.rs`
- **Size**: `971 B`
- **Modified Time**: `2025-09-15T22:37:26.969929`

#### Content Preview

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

### 📄 File #384 - `impl.rs`
- **Path**: `hyperlane-plugin-websocket\src\websocket\impl.rs`
- **Size**: `25,945 B`
- **Modified Time**: `2025-09-15T22:37:26.969929`

#### Content Preview

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
/// default hook functions that do nothing.
///
/// # Type Parameters
///
/// - `B`: The type parameter for `WebSocketConfig`, which must implement `BroadcastTypeTrait`.
impl<B: BroadcastTypeTrait> Default for WebSocketConfig<B> {
    fn default() -> Self {
        let default_hook: ArcFnContextPinBoxSendSync<()> = Arc::new(move |_| Box::pin(async {}));
        Self {
            context: Context::default(),
            buffer_size: DEFAULT_BUFFER_SIZE,
            capacity: DEFAULT_BROADCAST_SENDER_CAPACITY,
            broadcast_type: BroadcastType::default(),
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
    pub fn new() -> Self {
        Self::default()
    }

    /// Sets the buffer size for the WebSocket connection.
    ///
    /// # Arguments
    ///
    /// - `usize` - The desired buffer size in bytes.
    ///
    /// # Returns
    ///
    /// - `WebSocketConfig<B>` - The modified WebSocket configuration instance.
    pub fn set_buffer_size(mut self, buffer_size: usize) -> Self {
        self.buffer_size = buffer_size;
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
    pub fn set_broadcast_type(mut self, broadcast_type: BroadcastType<B>) -> Self {
        self.broadcast_type = broadcast_type;
        self
    }

    /// Sets the request hook function.
    ///
    /// This hook is executed when a new request is received.
    ///
    /// # Type Parameters
    ///
    /// - `F`: The type of the function, which must be `Fn(Context) -> Fut + Send + Sync + 'static`.
    /// - `Fut`: The future returned by the function, which must be `Future<Output = ()> + Send + 'static`.
    ///
    /// # Arguments
    ///
    /// - `hook` - The function to be used as the request hook.
    ///
    /// # Returns
    ///
    /// The modified WebSocket configuration instance.
    pub fn set_request_hook<F, Fut>(mut self, hook: F) -> Self
    where
        F: Fn(Context) -> Fut + Send + Sync + 'static,
        Fut: Future<Output = ()> + Send + 'static,
    {
        self.request_hook = Arc::new(move |ctx| Box::pin(hook(ctx)));
        self
    }

    /// Sets the sended hook function.
    ///
    /// This hook is executed after a message has been sent.
    ///
    /// # Type Parameters
    ///
    /// - `F`: The type of the function, which must be `Fn(Context) -> Fut + Send + Sync + 'static`.
    /// - `Fut`: The future returned by the function, which must be `Future<Output = ()> + Send + 'static`.
    ///
    /// # Arguments
    ///
    /// - `hook` - The function to be used as the sended hook.
    ///
    /// # Returns
    ///
    /// The modified WebSocket configuration instance.
    pub fn set_sended_hook<F, Fut>(mut self, hook: F) -> Self
    where
        F: Fn(Context) -> Fut + Send + Sync + 'static,
        Fut: Future<Output = ()> + Send + 'static,
    {
        self.sended_hook = Arc::new(move |ctx| Box::pin(hook(ctx)));
        self
    }

    /// Sets the closed hook function.
    ///
    /// This hook is executed when the WebSocket connection is closed.
    ///
    /// # Type Parameters
    ///
    /// - `F`: The type of the function, which must be `Fn(Context) -> Fut + Send + Sync + 'static`.
    /// - `Fut`: The future returned by the function, which must be `Future<Output = ()> + Send + 'static`.
    ///
    /// # Arguments
    ///
    /// - `hook` - The function to be used as the closed hook.
    ///
    /// # Returns
    ///
    /// The modified WebSocket configuration instance.
    pub fn set_closed_hook<F, Fut>(mut self, hook: F) -> Self
    where
        F: Fn(Context) -> Fut + Send + Sync + 'static,
        Fut: Future<Output = ()> + Send + 'static,
    {
        self.closed_hook = Arc::new(move |ctx| Box::pin(hook(ctx)));
        self
    }

    /// Retrieves a reference to the context associated with this configuration.
    ///
    /// # Returns
    ///
    /// - `&Context` - A reference to the context object.
    pub fn get_context(&self) -> &Context {
        &self.context
    }

    /// Retrieves the buffer size configured for the WebSocket connection.
    ///
    /// # Returns
    ///
    /// - `usize` - The buffer size in bytes.
    pub fn get_buffer_size(&self) -> usize {
        self.buffer_size
    }

    /// Retrieves the capacity configured for the broadcast sender.
    ///
    /// # Returns
    ///
    /// - `Capacity` - The capacity.
    pub fn get_capacity(&self) -> Capacity {
        self.capacity
    }

    /// Retrieves a reference to the broadcast type configured for this WebSocket.
    ///
    /// # Returns
    ///
    /// - `&BroadcastType<B>` - A reference to the broadcast type object.
    pub fn get_broadcast_type(&self) -> &BroadcastType<B> {
        &self.broadcast_type
    }

    /// Retrieves a reference to the request hook function.
    ///
    /// # Returns
    ///
    /// - `&ArcFnContextPinBoxSendSync<()>` - A reference to the request hook.
    pub fn get_request_hook(&self) -> &ArcFnContextPinBoxSendSync<()> {
        &self.request_hook
    }

    /// Retrieves a reference to the sended hook function.
    ///
    /// # Returns
    ///
    /// - `&ArcFnContextPinBoxSendSync<()>` - A reference to the sended hook.
    pub fn get_sended_hook(&self) -> &ArcFnContextPinBoxSendSync<()> {
        &self.sended_hook
    }

    /// Retrieves a reference to the closed hook function.
    ///
    /// # Returns
    ///
    /// - `&ArcFnContextPinBoxSendSync<()>` - A reference to the closed hook.
    pub fn get_closed_hook(&self) -> &ArcFnContextPinBoxSendSync<()> {
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
    pub fn new() -> Self {
        Self {
            broadcast_map: BroadcastMap::default(),
        }
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
    pub fn receiver_count<'a, B: BroadcastTypeTrait>(
        &self,
        broadcast_type: BroadcastType<B>,
    ) -> ReceiverCount {
        let key: String = BroadcastType::get_key(broadcast_type);
        self.broadcast_map.receiver_count(&key).unwrap_or(0)
    }

    /// Calculates the receiver count after incrementing it.
    ///
    /// Ensures the count does not exceed the maximum allowed value minus one.
    ///
    /// # Type Parameters
    ///
    /// - `B`: The type implementing `BroadcastTypeTrait`.
    ///
    /// # Arguments
    ///
    /// - `BroadcastType<B>` - The broadcast type for which to increment the receiver count.
    ///
    /// # Returns
    ///
    /// - `ReceiverCount` - The incremented receiver count.
    pub fn receiver_count_after_increment<B: BroadcastTypeTrait>(
        &self,
        broadcast_type: BroadcastType<B>,
    ) -> ReceiverCount {
        let count: ReceiverCount = self.receiver_count(broadcast_type);
        count.max(0).min(ReceiverCount::MAX - 1) + 1
    }

    /// Calculates the receiver count after decrementing it.
    ///
    /// Ensures the count does not go below 0.
    ///
    /// # Type Parameters
    ///
    /// - `B`: The type implementing `BroadcastTypeTrait`.
    ///
    /// # Arguments
    ///
    /// - `BroadcastType<B>` - The broadcast type for which to decrement the receiver count.
    ///
    /// # Returns
    ///
    /// - `ReceiverCount` - The decremented receiver count.
    pub fn receiver_count_after_decrement<B: BroadcastTypeTrait>(
        &self,
        broadcast_type: BroadcastType<B>,
    ) -> ReceiverCount {
        let count: ReceiverCount = self.receiver_count(broadcast_type);
        count.max(1).min(ReceiverCount::MAX) - 1
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
        let buffer_size: usize = config.get_buffer_size();
        let capacity: Capacity = config.get_capacity();
        let broadcast_type: BroadcastType<B> = config.get_broadcast_type().clone();
        let mut receiver: Receiver<Vec<u8>> = match &broadcast_type {
            BroadcastType::PointToPoint(key1, key2) => self.point_to_point(key1, key2, capacity),
            BroadcastType::PointToGroup(key) => self.point_to_group(key, capacity),
            BroadcastType::Unknown => panic!("BroadcastType must be PointToPoint or PointToGroup"),
        };
        let key: String = BroadcastType::get_key(broadcast_type);
        let result_handle = || async {
            ctx.aborted().await;
            ctx.closed().await;
        };
        loop {
            tokio::select! {
                request_res = ctx.ws_from_stream(buffer_size) => {
                    let mut need_break = false;
                    if request_res.is_ok() {
                        config.get_request_hook()(ctx.clone()).await;
                    } else {
                        need_break = true;
                        config.get_closed_hook()(ctx.clone()).await;
                    }
                    let body: ResponseBody = ctx.get_response_body().await;
                    let is_err: bool = self.broadcast_map.send(&key, body).is_err();
                    config.get_sended_hook()(ctx.clone()).await;
                    if need_break || is_err {
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

### 📄 File #385 - `mod.rs`
- **Path**: `hyperlane-plugin-websocket\src\websocket\mod.rs`
- **Size**: `119 B`
- **Modified Time**: `2025-09-15T22:37:26.969929`

#### Content Preview

```rust
pub(crate) mod r#const;
pub(crate) mod r#enum;
pub(crate) mod r#impl;
pub(crate) mod r#struct;
pub(crate) mod r#trait;

```

### 📄 File #386 - `struct.rs`
- **Path**: `hyperlane-plugin-websocket\src\websocket\struct.rs`
- **Size**: `2,098 B`
- **Modified Time**: `2025-09-15T22:37:26.970439`

#### Content Preview

```rust
use crate::*;

/// Represents a WebSocket instance.
///
/// This struct manages broadcast capabilities and holds the internal broadcast map
/// responsible for handling message distribution to various WebSocket connections.
#[derive(Debug, Clone)]
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
/// and various hook functions for different lifecycle events.
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
    /// The buffer size.
    ///
    /// This is the size of the buffer used for reading from the WebSocket stream.
    pub(super) buffer_size: usize,
    /// The capacity.
    ///
    /// This is the capacity of the broadcast sender channel.
    pub(super) capacity: Capacity,
    /// The broadcast type.
    ///
    /// This defines the type of broadcast this WebSocket connection will participate in
    /// (point-to-point or point-to-group).
    pub(super) broadcast_type: BroadcastType<B>,
    /// The request hook function.
    ///
    /// This hook is executed when a new request is received on the WebSocket.
    pub(super) request_hook: ArcFnContextPinBoxSendSync<()>,
    /// The sended hook function.
    ///
    /// This hook is executed after a message has been successfully sent over the WebSocket.
    pub(super) sended_hook: ArcFnContextPinBoxSendSync<()>,
    /// The closed hook function.
    ///
    /// This hook is executed when the WebSocket connection is closed.
    pub(super) closed_hook: ArcFnContextPinBoxSendSync<()>,
}

```

### 📄 File #387 - `trait.rs`
- **Path**: `hyperlane-plugin-websocket\src\websocket\trait.rs`
- **Size**: `245 B`
- **Modified Time**: `2025-09-15T22:37:26.970439`

#### Content Preview

```rust
/// A trait for types that can be used as broadcast identifiers.
///
/// Types implementing this trait must be convertible to a string,
/// be partially orderable, and be cloneable.
pub trait BroadcastTypeTrait: ToString + PartialOrd + Clone {}

```

### 📄 File #388 - `.gitignore`
- **Path**: `hyperlane-quick-start\.gitignore`
- **Size**: `50 B`
- **Modified Time**: `2025-09-15T22:37:17.324739`

#### Content Preview



### 📄 File #389 - `Cargo.lock`
- **Path**: `hyperlane-quick-start\Cargo.lock`
- **Size**: `58,324 B`
- **Modified Time**: `2025-10-01T21:58:37.485286`

#### Content Preview



### 📄 File #390 - `Cargo.toml`
- **Path**: `hyperlane-quick-start\Cargo.toml`
- **Size**: `1,497 B`
- **Modified Time**: `2025-10-01T21:58:37.503267`

#### Content Preview



### 📄 File #391 - `LICENSE`
- **Path**: `hyperlane-quick-start\LICENSE`
- **Size**: `1,066 B`
- **Modified Time**: `2025-09-15T22:37:17.325739`

#### Content Preview



### 📄 File #392 - `README.md`
- **Path**: `hyperlane-quick-start\README.md`
- **Size**: `2,129 B`
- **Modified Time**: `2025-09-15T22:37:17.325739`

#### Content Preview

```markdown
<center>

## hyperlane-quick-start

[English](README.md) | [简体中文](README.ZH-CN.md)

<img src="https://docs.ltpp.vip/img/hyperlane.png" alt="" height="160">

[![](https://img.shields.io/crates/v/hyperlane.svg)](https://crates.io/crates/hyperlane)
[![](https://img.shields.io/crates/d/hyperlane.svg)](https://img.shields.io/crates/d/hyperlane.svg)
[![](https://docs.rs/hyperlane/badge.svg)](https://docs.rs/hyperlane)
[![](https://github.com/hyperlane-dev/hyperlane/workflows/Rust/badge.svg)](https://github.com/hyperlane-dev/hyperlane/actions?query=workflow:Rust)
[![](https://img.shields.io/crates/l/hyperlane.svg)](./license)

</center>

> A lightweight, high-performance, and cross-platform Rust HTTP server library built on Tokio. It simplifies modern web service development by providing built-in support for middleware, WebSocket, Server-Sent Events (SSE), and raw TCP communication. With a unified and ergonomic API across Windows, Linux, and MacOS, it enables developers to build robust, scalable, and event-driven network applications with minimal overhead and maximum flexibility.

## Api Docs

- [Api Docs](https://docs.rs/hyperlane/latest/hyperlane/)

## Official Documentation

- [Official Documentation](https://docs.ltpp.vip/hyperlane/)

## Run

### start

```sh
cargo run
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

<img src="https://docs.ltpp.vip/img/wechat-pay.png" width="200">

### Alipay

<img src="https://docs.ltpp.vip/img/alipay-pay.jpg" width="200">

## License

This project is licensed under the MIT License. For more details, please see the [license](license) file.

## Contributing

Contributions are welcome! Please submit an issue or create a pull request.

## Contact

If you have any questions, please contact the author: [root@ltpp.vip](mailto:root@ltpp.vip).

```

### 📄 File #393 - `README.ZH-CN.md`
- **Path**: `hyperlane-quick-start\README.ZH-CN.md`
- **Size**: `2,056 B`
- **Modified Time**: `2025-09-15T22:37:17.325739`

#### Content Preview

```markdown
<center>

## hyperlane-quick-start

[English](README.md) | [简体中文](README.ZH-CN.md)

<img src="https://docs.ltpp.vip/img/hyperlane.png" alt="" height="160">

[![](https://img.shields.io/crates/v/hyperlane.svg)](https://crates.io/crates/hyperlane)
[![](https://img.shields.io/crates/d/hyperlane.svg)](https://img.shields.io/crates/d/hyperlane.svg)
[![](https://docs.rs/hyperlane/badge.svg)](https://docs.rs/hyperlane)
[![](https://github.com/hyperlane-dev/hyperlane/workflows/Rust/badge.svg)](https://github.com/hyperlane-dev/hyperlane/actions?query=workflow:Rust)
[![](https://img.shields.io/crates/l/hyperlane.svg)](./license)

</center>

> 这是一个轻量级、高性能且跨平台的 Rust HTTP 服务器库，基于 Tokio 构建。它通过提供中间件、WebSocket、服务器推送事件(SSE)和原始 TCP 通信的内置支持，简化了现代 Web 服务的开发。凭借在 Windows、Linux 和 macOS 上统一且符合人体工程学的 API，它使开发者能够以最小的开销和最大的灵活性构建强大、可扩展且事件驱动的网络应用程序。

## API 文档

- [API 文档](https://docs.rs/hyperlane/latest/hyperlane/)

## 官方文档

- [官方文档](https://docs.ltpp.vip/hyperlane/)

## 运行

### 运行

```sh
cargo run
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

<img src="https://docs.ltpp.vip/img/wechat-pay.png" width="200">

### 支付宝支付

<img src="https://docs.ltpp.vip/img/alipay-pay.jpg" width="200">

## 许可证

此项目基于 MIT 许可证授权。详细信息请查看 [license](license) 文件。

## 贡献

欢迎贡献！请提交 issue 或创建 pull request。

## 联系方式

如有任何疑问，请联系作者：[root@ltpp.vip](mailto:root@ltpp.vip)。

```

### 📄 File #394 - `config`
- **Path**: `hyperlane-quick-start\.git\config`
- **Size**: `331 B`
- **Modified Time**: `2025-09-15T22:37:17.317739`

#### Content Preview



### 📄 File #395 - `description`
- **Path**: `hyperlane-quick-start\.git\description`
- **Size**: `73 B`
- **Modified Time**: `2025-09-15T22:37:15.228194`

#### Content Preview



### 📄 File #396 - `FETCH_HEAD`
- **Path**: `hyperlane-quick-start\.git\FETCH_HEAD`
- **Size**: `242 B`
- **Modified Time**: `2025-10-01T21:58:37.431512`

#### Content Preview



### 📄 File #397 - `HEAD`
- **Path**: `hyperlane-quick-start\.git\HEAD`
- **Size**: `23 B`
- **Modified Time**: `2025-09-15T22:37:17.309951`

#### Content Preview



### 📄 File #398 - `index`
- **Path**: `hyperlane-quick-start\.git\index`
- **Size**: `9,650 B`
- **Modified Time**: `2025-10-01T21:58:37.583193`

#### Content Preview



### 📄 File #399 - `ORIG_HEAD`
- **Path**: `hyperlane-quick-start\.git\ORIG_HEAD`
- **Size**: `41 B`
- **Modified Time**: `2025-09-15T22:44:15.407859`

#### Content Preview



### 📄 File #400 - `packed-refs`
- **Path**: `hyperlane-quick-start\.git\packed-refs`
- **Size**: `114 B`
- **Modified Time**: `2025-09-15T22:37:17.298243`

#### Content Preview



### 📄 File #401 - `shallow`
- **Path**: `hyperlane-quick-start\.git\shallow`
- **Size**: `41 B`
- **Modified Time**: `2025-09-15T22:37:17.201798`

#### Content Preview



### 📄 File #402 - `applypatch-msg.sample`
- **Path**: `hyperlane-quick-start\.git\hooks\applypatch-msg.sample`
- **Size**: `478 B`
- **Modified Time**: `2025-09-15T22:37:15.228194`

#### Content Preview



### 📄 File #403 - `commit-msg.sample`
- **Path**: `hyperlane-quick-start\.git\hooks\commit-msg.sample`
- **Size**: `896 B`
- **Modified Time**: `2025-09-15T22:37:15.228194`

#### Content Preview



### 📄 File #404 - `fsmonitor-watchman.sample`
- **Path**: `hyperlane-quick-start\.git\hooks\fsmonitor-watchman.sample`
- **Size**: `4,726 B`
- **Modified Time**: `2025-09-15T22:37:15.229194`

#### Content Preview



### 📄 File #405 - `post-update.sample`
- **Path**: `hyperlane-quick-start\.git\hooks\post-update.sample`
- **Size**: `189 B`
- **Modified Time**: `2025-09-15T22:37:15.229194`

#### Content Preview



### 📄 File #406 - `pre-applypatch.sample`
- **Path**: `hyperlane-quick-start\.git\hooks\pre-applypatch.sample`
- **Size**: `424 B`
- **Modified Time**: `2025-09-15T22:37:15.229194`

#### Content Preview



### 📄 File #407 - `pre-commit.sample`
- **Path**: `hyperlane-quick-start\.git\hooks\pre-commit.sample`
- **Size**: `1,649 B`
- **Modified Time**: `2025-09-15T22:37:15.229194`

#### Content Preview



### 📄 File #408 - `pre-merge-commit.sample`
- **Path**: `hyperlane-quick-start\.git\hooks\pre-merge-commit.sample`
- **Size**: `416 B`
- **Modified Time**: `2025-09-15T22:37:15.229194`

#### Content Preview



### 📄 File #409 - `pre-push.sample`
- **Path**: `hyperlane-quick-start\.git\hooks\pre-push.sample`
- **Size**: `1,374 B`
- **Modified Time**: `2025-09-15T22:37:15.229194`

#### Content Preview



### 📄 File #410 - `pre-rebase.sample`
- **Path**: `hyperlane-quick-start\.git\hooks\pre-rebase.sample`
- **Size**: `4,898 B`
- **Modified Time**: `2025-09-15T22:37:15.230194`

#### Content Preview



### 📄 File #411 - `pre-receive.sample`
- **Path**: `hyperlane-quick-start\.git\hooks\pre-receive.sample`
- **Size**: `544 B`
- **Modified Time**: `2025-09-15T22:37:15.230194`

#### Content Preview



### 📄 File #412 - `prepare-commit-msg.sample`
- **Path**: `hyperlane-quick-start\.git\hooks\prepare-commit-msg.sample`
- **Size**: `1,492 B`
- **Modified Time**: `2025-09-15T22:37:15.230194`

#### Content Preview



### 📄 File #413 - `push-to-checkout.sample`
- **Path**: `hyperlane-quick-start\.git\hooks\push-to-checkout.sample`
- **Size**: `2,783 B`
- **Modified Time**: `2025-09-15T22:37:15.230194`

#### Content Preview



### 📄 File #414 - `sendemail-validate.sample`
- **Path**: `hyperlane-quick-start\.git\hooks\sendemail-validate.sample`
- **Size**: `2,308 B`
- **Modified Time**: `2025-09-15T22:37:15.230194`

#### Content Preview



### 📄 File #415 - `update.sample`
- **Path**: `hyperlane-quick-start\.git\hooks\update.sample`
- **Size**: `3,650 B`
- **Modified Time**: `2025-09-15T22:37:15.231194`

#### Content Preview



### 📄 File #416 - `exclude`
- **Path**: `hyperlane-quick-start\.git\info\exclude`
- **Size**: `240 B`
- **Modified Time**: `2025-09-15T22:37:15.231194`

#### Content Preview



### 📄 File #417 - `HEAD`
- **Path**: `hyperlane-quick-start\.git\logs\HEAD`
- **Size**: `349 B`
- **Modified Time**: `2025-10-01T21:58:37.584757`

#### Content Preview



### 📄 File #418 - `master`
- **Path**: `hyperlane-quick-start\.git\logs\refs\heads\master`
- **Size**: `349 B`
- **Modified Time**: `2025-10-01T21:58:37.584757`

#### Content Preview



### 📄 File #419 - `HEAD`
- **Path**: `hyperlane-quick-start\.git\logs\refs\remotes\origin\HEAD`
- **Size**: `196 B`
- **Modified Time**: `2025-09-15T22:37:17.308951`

#### Content Preview



### 📄 File #420 - `master`
- **Path**: `hyperlane-quick-start\.git\logs\refs\remotes\origin\master`
- **Size**: `153 B`
- **Modified Time**: `2025-10-01T21:58:37.366450`

#### Content Preview



### 📄 File #421 - `54822384d766ce6ee631d890def4e46ba79d8c`
- **Path**: `hyperlane-quick-start\.git\objects\00\54822384d766ce6ee631d890def4e46ba79d8c`
- **Size**: `78 B`
- **Modified Time**: `2025-10-01T21:58:36.992006`

#### Content Preview



### 📄 File #422 - `6a150fdc67b73bc4212f336e5c23af9933b057`
- **Path**: `hyperlane-quick-start\.git\objects\10\6a150fdc67b73bc4212f336e5c23af9933b057`
- **Size**: `116 B`
- **Modified Time**: `2025-10-01T21:58:36.992006`

#### Content Preview



### 📄 File #423 - `90f492cd7fdb1010952e7a3a4a30d8a87d968e`
- **Path**: `hyperlane-quick-start\.git\objects\12\90f492cd7fdb1010952e7a3a4a30d8a87d968e`
- **Size**: `164 B`
- **Modified Time**: `2025-10-01T21:58:36.986875`

#### Content Preview



### 📄 File #424 - `5ab91ae5c9cdb5a06a916525dee765e6211d61`
- **Path**: `hyperlane-quick-start\.git\objects\13\5ab91ae5c9cdb5a06a916525dee765e6211d61`
- **Size**: `678 B`
- **Modified Time**: `2025-10-01T21:58:37.065431`

#### Content Preview



### 📄 File #425 - `f8ce4b0a44372820420b5158a08b27a3404c2e`
- **Path**: `hyperlane-quick-start\.git\objects\15\f8ce4b0a44372820420b5158a08b27a3404c2e`
- **Size**: `109 B`
- **Modified Time**: `2025-10-01T21:58:37.012248`

#### Content Preview



### 📄 File #426 - `5c6629985f2e0b3a49995306bdd6b0286b6f41`
- **Path**: `hyperlane-quick-start\.git\objects\22\5c6629985f2e0b3a49995306bdd6b0286b6f41`
- **Size**: `393 B`
- **Modified Time**: `2025-10-01T21:58:37.022772`

#### Content Preview



### 📄 File #427 - `b8559eacc9f2458f2afb02f37abdc146c5c85e`
- **Path**: `hyperlane-quick-start\.git\objects\22\b8559eacc9f2458f2afb02f37abdc146c5c85e`
- **Size**: `679 B`
- **Modified Time**: `2025-10-01T21:58:37.084678`

#### Content Preview



### 📄 File #428 - `a250a9d9c3485e283e66646ebc496b82f181e5`
- **Path**: `hyperlane-quick-start\.git\objects\27\a250a9d9c3485e283e66646ebc496b82f181e5`
- **Size**: `59 B`
- **Modified Time**: `2025-10-01T21:58:37.119726`

#### Content Preview



### 📄 File #429 - `f555398305b31f3386b093c4db4dcbd49cf2e6`
- **Path**: `hyperlane-quick-start\.git\objects\27\f555398305b31f3386b093c4db4dcbd49cf2e6`
- **Size**: `392 B`
- **Modified Time**: `2025-10-01T21:58:37.022772`

#### Content Preview



### 📄 File #430 - `ed63df6d88585f1103dde2f099d2322dea88ca`
- **Path**: `hyperlane-quick-start\.git\objects\2d\ed63df6d88585f1103dde2f099d2322dea88ca`
- **Size**: `679 B`
- **Modified Time**: `2025-10-01T21:58:37.065431`

#### Content Preview



### 📄 File #431 - `a8cf67216bd3c2b97ceed09696b4c06ce0852e`
- **Path**: `hyperlane-quick-start\.git\objects\2f\a8cf67216bd3c2b97ceed09696b4c06ce0852e`
- **Size**: `660 B`
- **Modified Time**: `2025-10-01T21:58:37.132122`

#### Content Preview



### 📄 File #432 - `0d28dfbcbc1dcb97ba4c9e932efffb0636cdd0`
- **Path**: `hyperlane-quick-start\.git\objects\30\0d28dfbcbc1dcb97ba4c9e932efffb0636cdd0`
- **Size**: `78 B`
- **Modified Time**: `2025-10-01T21:58:36.992006`

#### Content Preview



### 📄 File #433 - `2608accffd421b27efeadbd1808db4235cd6bc`
- **Path**: `hyperlane-quick-start\.git\objects\31\2608accffd421b27efeadbd1808db4235cd6bc`
- **Size**: `67 B`
- **Modified Time**: `2025-10-01T21:58:37.103302`

#### Content Preview



### 📄 File #434 - `27cd89e2629a5181ae250fd6316c5f2775bc00`
- **Path**: `hyperlane-quick-start\.git\objects\33\27cd89e2629a5181ae250fd6316c5f2775bc00`
- **Size**: `112 B`
- **Modified Time**: `2025-10-01T21:58:37.022772`

#### Content Preview



### 📄 File #435 - `4b16ecc3dde7d279b3b3a7d6570e045c868a95`
- **Path**: `hyperlane-quick-start\.git\objects\40\4b16ecc3dde7d279b3b3a7d6570e045c868a95`
- **Size**: `82 B`
- **Modified Time**: `2025-10-01T21:58:37.015493`

#### Content Preview



### 📄 File #436 - `0b8c4d48c905d6f8e9b5f1ae7eb95180c9c5a6`
- **Path**: `hyperlane-quick-start\.git\objects\43\0b8c4d48c905d6f8e9b5f1ae7eb95180c9c5a6`
- **Size**: `79 B`
- **Modified Time**: `2025-10-01T21:58:36.992006`

#### Content Preview



### 📄 File #437 - `214f3861f80d366e88edfcacf9e9abc8ae937a`
- **Path**: `hyperlane-quick-start\.git\objects\48\214f3861f80d366e88edfcacf9e9abc8ae937a`
- **Size**: `105 B`
- **Modified Time**: `2025-10-01T21:58:37.123610`

#### Content Preview



### 📄 File #438 - `34d31fc11eb7debbe5c7f06dadab88eb192af6`
- **Path**: `hyperlane-quick-start\.git\objects\48\34d31fc11eb7debbe5c7f06dadab88eb192af6`
- **Size**: `81 B`
- **Modified Time**: `2025-10-01T21:58:37.011296`

#### Content Preview



### 📄 File #439 - `50ce1c515dd2247f606d3e920ee5e4d130433c`
- **Path**: `hyperlane-quick-start\.git\objects\49\50ce1c515dd2247f606d3e920ee5e4d130433c`
- **Size**: `107 B`
- **Modified Time**: `2025-10-01T21:58:37.148859`

#### Content Preview



### 📄 File #440 - `7e7bd50ff79b8b70899c7ddb2b67445bee3d61`
- **Path**: `hyperlane-quick-start\.git\objects\49\7e7bd50ff79b8b70899c7ddb2b67445bee3d61`
- **Size**: `314 B`
- **Modified Time**: `2025-10-01T21:58:37.091820`

#### Content Preview



### 📄 File #441 - `83dba23be6c95595edaa65c30e7529e84e66e5`
- **Path**: `hyperlane-quick-start\.git\objects\4a\83dba23be6c95595edaa65c30e7529e84e66e5`
- **Size**: `78 B`
- **Modified Time**: `2025-10-01T21:58:36.992006`

#### Content Preview



### 📄 File #442 - `eb508a34daebbd0220a600b37f26067bb7ab0b`
- **Path**: `hyperlane-quick-start\.git\objects\4c\eb508a34daebbd0220a600b37f26067bb7ab0b`
- **Size**: `279 B`
- **Modified Time**: `2025-10-01T21:58:37.103302`

#### Content Preview



### 📄 File #443 - `3b39e1611a66369743526c0990c3e0ea1f13d5`
- **Path**: `hyperlane-quick-start\.git\objects\4d\3b39e1611a66369743526c0990c3e0ea1f13d5`
- **Size**: `16,603 B`
- **Modified Time**: `2025-10-01T21:58:37.036698`

#### Content Preview



### 📄 File #444 - `a3fd145164ba0be2f0b975cdd129a32becb68f`
- **Path**: `hyperlane-quick-start\.git\objects\4f\a3fd145164ba0be2f0b975cdd129a32becb68f`
- **Size**: `81 B`
- **Modified Time**: `2025-10-01T21:58:37.005793`

#### Content Preview



### 📄 File #445 - `0ee3ab08804c8a6406bff9833c3ccce4b01504`
- **Path**: `hyperlane-quick-start\.git\objects\51\0ee3ab08804c8a6406bff9833c3ccce4b01504`
- **Size**: `78 B`
- **Modified Time**: `2025-10-01T21:58:36.992006`

#### Content Preview



### 📄 File #446 - `9aa533f1cbeafb3559a76be8a1baf1ef38ddf8`
- **Path**: `hyperlane-quick-start\.git\objects\52\9aa533f1cbeafb3559a76be8a1baf1ef38ddf8`
- **Size**: `678 B`
- **Modified Time**: `2025-10-01T21:58:37.065431`

#### Content Preview



### 📄 File #447 - `ec1719125d40680e7185dd8252fbcec3a9fee1`
- **Path**: `hyperlane-quick-start\.git\objects\52\ec1719125d40680e7185dd8252fbcec3a9fee1`
- **Size**: `147 B`
- **Modified Time**: `2025-10-01T21:58:37.015493`

#### Content Preview



### 📄 File #448 - `a480ed9211ef8f30fdd8d81dfce3de94c9db35`
- **Path**: `hyperlane-quick-start\.git\objects\54\a480ed9211ef8f30fdd8d81dfce3de94c9db35`
- **Size**: `47 B`
- **Modified Time**: `2025-10-01T21:58:37.022772`

#### Content Preview



### 📄 File #449 - `48cfad83eb58346dc8b84c4f08af91218044ac`
- **Path**: `hyperlane-quick-start\.git\objects\55\48cfad83eb58346dc8b84c4f08af91218044ac`
- **Size**: `98 B`
- **Modified Time**: `2025-10-01T21:58:37.120730`

#### Content Preview



### 📄 File #450 - `20d6c18c5877978a0cbee2e6badf21b4c5ee42`
- **Path**: `hyperlane-quick-start\.git\objects\56\20d6c18c5877978a0cbee2e6badf21b4c5ee42`
- **Size**: `359 B`
- **Modified Time**: `2025-10-01T21:58:37.103302`

#### Content Preview



### 📄 File #451 - `d15266d60b7c1466fecefb1822af05c233b5cf`
- **Path**: `hyperlane-quick-start\.git\objects\62\d15266d60b7c1466fecefb1822af05c233b5cf`
- **Size**: `175 B`
- **Modified Time**: `2025-10-01T21:58:37.103302`

#### Content Preview



### 📄 File #452 - `65615b924029e2a7e53212fd5ba815cb46575a`
- **Path**: `hyperlane-quick-start\.git\objects\65\65615b924029e2a7e53212fd5ba815cb46575a`
- **Size**: `55 B`
- **Modified Time**: `2025-10-01T21:58:37.015493`

#### Content Preview



### 📄 File #453 - `545319a2d8e86c21e3549bfdc02abc1d506405`
- **Path**: `hyperlane-quick-start\.git\objects\6a\545319a2d8e86c21e3549bfdc02abc1d506405`
- **Size**: `154 B`
- **Modified Time**: `2025-10-01T21:58:37.150270`

#### Content Preview



### 📄 File #454 - `9ab9c109fc482abdbf626f3746f9bc45ba2338`
- **Path**: `hyperlane-quick-start\.git\objects\6b\9ab9c109fc482abdbf626f3746f9bc45ba2338`
- **Size**: `314 B`
- **Modified Time**: `2025-10-01T21:58:37.101808`

#### Content Preview



### 📄 File #455 - `21b78e9a4050df1fb6255fe935a882dc45638a`
- **Path**: `hyperlane-quick-start\.git\objects\71\21b78e9a4050df1fb6255fe935a882dc45638a`
- **Size**: `166 B`
- **Modified Time**: `2025-10-01T21:58:36.986875`

#### Content Preview



### 📄 File #456 - `3cccb763d62c6d5d49181726557b707bb4b808`
- **Path**: `hyperlane-quick-start\.git\objects\71\3cccb763d62c6d5d49181726557b707bb4b808`
- **Size**: `170 B`
- **Modified Time**: `2025-10-01T21:58:37.103302`

#### Content Preview



### 📄 File #457 - `5fdf93e1cce1b3865e8b9ee763c2b5e2fa4b0e`
- **Path**: `hyperlane-quick-start\.git\objects\72\5fdf93e1cce1b3865e8b9ee763c2b5e2fa4b0e`
- **Size**: `679 B`
- **Modified Time**: `2025-10-01T21:58:37.065431`

#### Content Preview



### 📄 File #458 - `094932d6587d087e45c36e5a96958b5b5256d9`
- **Path**: `hyperlane-quick-start\.git\objects\74\094932d6587d087e45c36e5a96958b5b5256d9`
- **Size**: `16,598 B`
- **Modified Time**: `2025-10-01T21:58:37.054503`

#### Content Preview



### 📄 File #459 - `e10753b5318a539ca2253a1b96c3db1f3c5f61`
- **Path**: `hyperlane-quick-start\.git\objects\74\e10753b5318a539ca2253a1b96c3db1f3c5f61`
- **Size**: `183 B`
- **Modified Time**: `2025-10-01T21:58:37.103302`

#### Content Preview



### 📄 File #460 - `ba2a490553300308a2c4345f9fb6a16a67b10e`
- **Path**: `hyperlane-quick-start\.git\objects\75\ba2a490553300308a2c4345f9fb6a16a67b10e`
- **Size**: `150 B`
- **Modified Time**: `2025-10-01T21:58:37.022772`

#### Content Preview



### 📄 File #461 - `41206b87dc1306c59c955a2559f4760ebf2fb5`
- **Path**: `hyperlane-quick-start\.git\objects\76\41206b87dc1306c59c955a2559f4760ebf2fb5`
- **Size**: `678 B`
- **Modified Time**: `2025-10-01T21:58:37.086672`

#### Content Preview



### 📄 File #462 - `a1e27fecfe5f2f43ecf02f7bab725a31979d37`
- **Path**: `hyperlane-quick-start\.git\objects\78\a1e27fecfe5f2f43ecf02f7bab725a31979d37`
- **Size**: `71 B`
- **Modified Time**: `2025-10-01T21:58:37.125590`

#### Content Preview



### 📄 File #463 - `0e9f911caa19cb8d553ed5b1f343166126f063`
- **Path**: `hyperlane-quick-start\.git\objects\7b\0e9f911caa19cb8d553ed5b1f343166126f063`
- **Size**: `16,606 B`
- **Modified Time**: `2025-10-01T21:58:37.052457`

#### Content Preview



### 📄 File #464 - `c5699b50da97afc5af132dd09c2a768b8e612b`
- **Path**: `hyperlane-quick-start\.git\objects\7c\c5699b50da97afc5af132dd09c2a768b8e612b`
- **Size**: `192 B`
- **Modified Time**: `2025-10-01T21:58:37.030787`

#### Content Preview



### 📄 File #465 - `05db84f55921ac2aec694a973c463e926ab73e`
- **Path**: `hyperlane-quick-start\.git\objects\83\05db84f55921ac2aec694a973c463e926ab73e`
- **Size**: `87 B`
- **Modified Time**: `2025-10-01T21:58:37.127806`

#### Content Preview



### 📄 File #466 - `b06bf134250a25c82a0f06e326a2533c0671f5`
- **Path**: `hyperlane-quick-start\.git\objects\86\b06bf134250a25c82a0f06e326a2533c0671f5`
- **Size**: `680 B`
- **Modified Time**: `2025-10-01T21:58:37.065431`

#### Content Preview



### 📄 File #467 - `f970861b358ab4f4a4c958675ea0715d47f33f`
- **Path**: `hyperlane-quick-start\.git\objects\89\f970861b358ab4f4a4c958675ea0715d47f33f`
- **Size**: `231 B`
- **Modified Time**: `2025-10-01T21:58:37.124609`

#### Content Preview



### 📄 File #468 - `21904cd3b97aa45fed6fdd67147d208c7d2d1e`
- **Path**: `hyperlane-quick-start\.git\objects\94\21904cd3b97aa45fed6fdd67147d208c7d2d1e`
- **Size**: `199 B`
- **Modified Time**: `2025-10-01T21:58:37.103302`

#### Content Preview



### 📄 File #469 - `f00db2f5dd3614b2d249f417a63b6e734acf4c`
- **Path**: `hyperlane-quick-start\.git\objects\9f\f00db2f5dd3614b2d249f417a63b6e734acf4c`
- **Size**: `148 B`
- **Modified Time**: `2025-10-01T21:58:36.991497`

#### Content Preview



### 📄 File #470 - `09e33a57ef773cd82907a8ec686043131cc17d`
- **Path**: `hyperlane-quick-start\.git\objects\a0\09e33a57ef773cd82907a8ec686043131cc17d`
- **Size**: `181 B`
- **Modified Time**: `2025-10-01T21:58:37.153576`

#### Content Preview



### 📄 File #471 - `ce85df7a45c00c753e9c62faa0a0bed6c92c69`
- **Path**: `hyperlane-quick-start\.git\objects\a2\ce85df7a45c00c753e9c62faa0a0bed6c92c69`
- **Size**: `181 B`
- **Modified Time**: `2025-10-01T21:58:37.002871`

#### Content Preview



### 📄 File #472 - `218d4668de7760aacec67ef07760af2a1199dc`
- **Path**: `hyperlane-quick-start\.git\objects\a8\218d4668de7760aacec67ef07760af2a1199dc`
- **Size**: `392 B`
- **Modified Time**: `2025-10-01T21:58:37.152346`

#### Content Preview



### 📄 File #473 - `f9ff56624159dd922dcfafcc8598be6fbd80da`
- **Path**: `hyperlane-quick-start\.git\objects\ab\f9ff56624159dd922dcfafcc8598be6fbd80da`
- **Size**: `392 B`
- **Modified Time**: `2025-10-01T21:58:37.153576`

#### Content Preview



### 📄 File #474 - `faf493260a821249be6870f7bd9fa920c7f9eb`
- **Path**: `hyperlane-quick-start\.git\objects\b2\faf493260a821249be6870f7bd9fa920c7f9eb`
- **Size**: `51 B`
- **Modified Time**: `2025-10-01T21:58:37.015493`

#### Content Preview



### 📄 File #475 - `8da5bb90af26404909756041c14ddb88470902`
- **Path**: `hyperlane-quick-start\.git\objects\b3\8da5bb90af26404909756041c14ddb88470902`
- **Size**: `16,590 B`
- **Modified Time**: `2025-10-01T21:58:37.036698`

#### Content Preview



### 📄 File #476 - `9257c2b8d3f0cba0ef1486284b6d21e6909101`
- **Path**: `hyperlane-quick-start\.git\objects\b4\9257c2b8d3f0cba0ef1486284b6d21e6909101`
- **Size**: `150 B`
- **Modified Time**: `2025-10-01T21:58:37.103302`

#### Content Preview



### 📄 File #477 - `afbd878670485e5788ea33e904eef72a6b99bf`
- **Path**: `hyperlane-quick-start\.git\objects\b5\afbd878670485e5788ea33e904eef72a6b99bf`
- **Size**: `153 B`
- **Modified Time**: `2025-10-01T21:58:37.022772`

#### Content Preview



### 📄 File #478 - `0c5d3e17feda11c278f0289f8f70cfa9f53ea1`
- **Path**: `hyperlane-quick-start\.git\objects\bd\0c5d3e17feda11c278f0289f8f70cfa9f53ea1`
- **Size**: `393 B`
- **Modified Time**: `2025-10-01T21:58:37.035498`

#### Content Preview



### 📄 File #479 - `4dcc6f4f675052cee07b3634ff68c4fbf84268`
- **Path**: `hyperlane-quick-start\.git\objects\c0\4dcc6f4f675052cee07b3634ff68c4fbf84268`
- **Size**: `155 B`
- **Modified Time**: `2025-10-01T21:58:37.132122`

#### Content Preview



### 📄 File #480 - `073b9828073442ce38662a864702db1547585b`
- **Path**: `hyperlane-quick-start\.git\objects\c8\073b9828073442ce38662a864702db1547585b`
- **Size**: `16,615 B`
- **Modified Time**: `2025-10-01T21:58:37.065431`

#### Content Preview



### 📄 File #481 - `a1e8052532377599d045617208bba1ba266bb4`
- **Path**: `hyperlane-quick-start\.git\objects\ca\a1e8052532377599d045617208bba1ba266bb4`
- **Size**: `81 B`
- **Modified Time**: `2025-10-01T21:58:37.003591`

#### Content Preview



### 📄 File #482 - `d9869251780fb511597347f39ff87d702f44e9`
- **Path**: `hyperlane-quick-start\.git\objects\ca\d9869251780fb511597347f39ff87d702f44e9`
- **Size**: `109 B`
- **Modified Time**: `2025-10-01T21:58:37.103302`

#### Content Preview



### 📄 File #483 - `90878a24c714f3d5231d4a8db03f637c264f95`
- **Path**: `hyperlane-quick-start\.git\objects\cc\90878a24c714f3d5231d4a8db03f637c264f95`
- **Size**: `81 B`
- **Modified Time**: `2025-10-01T21:58:37.008554`

#### Content Preview



### 📄 File #484 - `efaac99b48e134655b4b4e6f7ca5ca8ec0d030`
- **Path**: `hyperlane-quick-start\.git\objects\d1\efaac99b48e134655b4b4e6f7ca5ca8ec0d030`
- **Size**: `87 B`
- **Modified Time**: `2025-10-01T21:58:36.992006`

#### Content Preview



### 📄 File #485 - `76e0369515394f9abc8c45c56ae9df4b4107d7`
- **Path**: `hyperlane-quick-start\.git\objects\d2\76e0369515394f9abc8c45c56ae9df4b4107d7`
- **Size**: `64 B`
- **Modified Time**: `2025-10-01T21:58:37.132122`

#### Content Preview



### 📄 File #486 - `21484dc2b2f513703030862c973cf3d3d56f99`
- **Path**: `hyperlane-quick-start\.git\objects\d6\21484dc2b2f513703030862c973cf3d3d56f99`
- **Size**: `164 B`
- **Modified Time**: `2025-10-01T21:58:36.981554`

#### Content Preview



### 📄 File #487 - `56cd4f53009e177c6b12252614b13369382bcf`
- **Path**: `hyperlane-quick-start\.git\objects\d9\56cd4f53009e177c6b12252614b13369382bcf`
- **Size**: `178 B`
- **Modified Time**: `2025-10-01T21:58:37.132122`

#### Content Preview



### 📄 File #488 - `ae3e6d670fc370b2d76cd5315b5ade939657a8`
- **Path**: `hyperlane-quick-start\.git\objects\d9\ae3e6d670fc370b2d76cd5315b5ade939657a8`
- **Size**: `77 B`
- **Modified Time**: `2025-10-01T21:58:37.015493`

#### Content Preview



### 📄 File #489 - `79d07f971826e79738f914e03ad756e71d46d1`
- **Path**: `hyperlane-quick-start\.git\objects\da\79d07f971826e79738f914e03ad756e71d46d1`
- **Size**: `164 B`
- **Modified Time**: `2025-10-01T21:58:36.986875`

#### Content Preview



### 📄 File #490 - `343c64d8daaa5084e9670592aeca01ef6520cf`
- **Path**: `hyperlane-quick-start\.git\objects\db\343c64d8daaa5084e9670592aeca01ef6520cf`
- **Size**: `112 B`
- **Modified Time**: `2025-10-01T21:58:37.132122`

#### Content Preview



### 📄 File #491 - `6afbbe5839c681489f15800d83af6aa9f1e72d`
- **Path**: `hyperlane-quick-start\.git\objects\dd\6afbbe5839c681489f15800d83af6aa9f1e72d`
- **Size**: `80 B`
- **Modified Time**: `2025-10-01T21:58:37.009295`

#### Content Preview



### 📄 File #492 - `e125cf1cdb5d1a83dbbc7017133f5135932428`
- **Path**: `hyperlane-quick-start\.git\objects\df\e125cf1cdb5d1a83dbbc7017133f5135932428`
- **Size**: `191 B`
- **Modified Time**: `2025-10-01T21:58:37.153576`

#### Content Preview



### 📄 File #493 - `572418295d04c05594f8428777fa22d596ea71`
- **Path**: `hyperlane-quick-start\.git\objects\e0\572418295d04c05594f8428777fa22d596ea71`
- **Size**: `165 B`
- **Modified Time**: `2025-10-01T21:58:37.132122`

#### Content Preview



### 📄 File #494 - `a13cde65b50e505d19dadd3fe66e5484c588bc`
- **Path**: `hyperlane-quick-start\.git\objects\e1\a13cde65b50e505d19dadd3fe66e5484c588bc`
- **Size**: `16,615 B`
- **Modified Time**: `2025-10-01T21:58:37.036698`

#### Content Preview



### 📄 File #495 - `e2fdb7411125c1d98d5e1d48c881cd8113ec85`
- **Path**: `hyperlane-quick-start\.git\objects\e2\e2fdb7411125c1d98d5e1d48c881cd8113ec85`
- **Size**: `392 B`
- **Modified Time**: `2025-10-01T21:58:37.036698`

#### Content Preview



### 📄 File #496 - `691a87cebb3164785c8577f4f79294bb270b6a`
- **Path**: `hyperlane-quick-start\.git\objects\e3\691a87cebb3164785c8577f4f79294bb270b6a`
- **Size**: `81 B`
- **Modified Time**: `2025-10-01T21:58:37.006934`

#### Content Preview



### 📄 File #497 - `1d1d948f1653289708f5bbda30883679905cfc`
- **Path**: `hyperlane-quick-start\.git\objects\e4\1d1d948f1653289708f5bbda30883679905cfc`
- **Size**: `165 B`
- **Modified Time**: `2025-10-01T21:58:36.985631`

#### Content Preview



### 📄 File #498 - `dbe242fdf50e77b33c66b1cc058efe5ab364b6`
- **Path**: `hyperlane-quick-start\.git\objects\e4\dbe242fdf50e77b33c66b1cc058efe5ab364b6`
- **Size**: `166 B`
- **Modified Time**: `2025-10-01T21:58:36.984783`

#### Content Preview



### 📄 File #499 - `122b5214665c1fc209ab9bc914587bf604a108`
- **Path**: `hyperlane-quick-start\.git\objects\e5\122b5214665c1fc209ab9bc914587bf604a108`
- **Size**: `16,605 B`
- **Modified Time**: `2025-10-01T21:58:37.060400`

#### Content Preview



### 📄 File #500 - `9c073963ca8b7d607f5e15dbc6e70b8685e055`
- **Path**: `hyperlane-quick-start\.git\objects\e6\9c073963ca8b7d607f5e15dbc6e70b8685e055`
- **Size**: `391 B`
- **Modified Time**: `2025-10-01T21:58:37.153576`

#### Content Preview



### 📄 File #501 - `24f83af145912a84d93d7020f00e14b61be916`
- **Path**: `hyperlane-quick-start\.git\objects\ee\24f83af145912a84d93d7020f00e14b61be916`
- **Size**: `115 B`
- **Modified Time**: `2025-10-01T21:58:37.122591`

#### Content Preview



### 📄 File #502 - `62843f8f25d44788a71a058521b4ff02cc4d97`
- **Path**: `hyperlane-quick-start\.git\objects\f7\62843f8f25d44788a71a058521b4ff02cc4d97`
- **Size**: `164 B`
- **Modified Time**: `2025-10-01T21:58:36.982677`

#### Content Preview



### 📄 File #503 - `11d5e1175f952acb54e3761aade3dcd63313c3`
- **Path**: `hyperlane-quick-start\.git\objects\ff\11d5e1175f952acb54e3761aade3dcd63313c3`
- **Size**: `78 B`
- **Modified Time**: `2025-10-01T21:58:37.013547`

#### Content Preview



### 📄 File #504 - `pack-fb865eb06a18641a3fbfae3da92074cf9ad809bd.idx`
- **Path**: `hyperlane-quick-start\.git\objects\pack\pack-fb865eb06a18641a3fbfae3da92074cf9ad809bd.idx`
- **Size**: `3,984 B`
- **Modified Time**: `2025-09-15T22:37:17.264239`

#### Content Preview



### 📄 File #505 - `pack-fb865eb06a18641a3fbfae3da92074cf9ad809bd.pack`
- **Path**: `hyperlane-quick-start\.git\objects\pack\pack-fb865eb06a18641a3fbfae3da92074cf9ad809bd.pack`
- **Size**: `29,817 B`
- **Modified Time**: `2025-10-01T21:58:37.149256`

#### Content Preview



### 📄 File #506 - `pack-fb865eb06a18641a3fbfae3da92074cf9ad809bd.rev`
- **Path**: `hyperlane-quick-start\.git\objects\pack\pack-fb865eb06a18641a3fbfae3da92074cf9ad809bd.rev`
- **Size**: `468 B`
- **Modified Time**: `2025-09-15T22:37:17.265239`

#### Content Preview



### 📄 File #507 - `master`
- **Path**: `hyperlane-quick-start\.git\refs\heads\master`
- **Size**: `41 B`
- **Modified Time**: `2025-10-01T21:58:37.584236`

#### Content Preview



### 📄 File #508 - `HEAD`
- **Path**: `hyperlane-quick-start\.git\refs\remotes\origin\HEAD`
- **Size**: `32 B`
- **Modified Time**: `2025-09-15T22:37:17.307951`

#### Content Preview



### 📄 File #509 - `master`
- **Path**: `hyperlane-quick-start\.git\refs\remotes\origin\master`
- **Size**: `41 B`
- **Modified Time**: `2025-10-01T21:58:37.366450`

#### Content Preview



### 📄 File #510 - `v6.3.5`
- **Path**: `hyperlane-quick-start\.git\refs\tags\v6.3.5`
- **Size**: `41 B`
- **Modified Time**: `2025-09-15T22:37:17.306951`

#### Content Preview



### 📄 File #511 - `v7.0.3`
- **Path**: `hyperlane-quick-start\.git\refs\tags\v7.0.3`
- **Size**: `41 B`
- **Modified Time**: `2025-10-01T21:58:37.431512`

#### Content Preview



### 📄 File #512 - `Cargo.toml`
- **Path**: `hyperlane-quick-start\app\Cargo.toml`
- **Size**: `260 B`
- **Modified Time**: `2025-09-15T22:37:17.326739`

#### Content Preview



### 📄 File #513 - `lib.rs`
- **Path**: `hyperlane-quick-start\app\lib.rs`
- **Size**: `242 B`
- **Modified Time**: `2025-09-15T22:37:17.328740`

#### Content Preview

```rust
pub mod aspect;
pub mod controller;
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

### 📄 File #514 - `mod.rs`
- **Path**: `hyperlane-quick-start\app\aspect\mod.rs`
- **Size**: `1 B`
- **Modified Time**: `2025-09-15T22:37:17.326739`

#### Content Preview

```rust


```

### 📄 File #515 - `mod.rs`
- **Path**: `hyperlane-quick-start\app\controller\mod.rs`
- **Size**: `66 B`
- **Modified Time**: `2025-10-01T21:58:37.520759`

#### Content Preview

```rust
pub mod favicon;
pub mod hello;
pub mod websocket;

use super::*;

```

### 📄 File #516 - `fn.rs`
- **Path**: `hyperlane-quick-start\app\controller\favicon\fn.rs`
- **Size**: `179 B`
- **Modified Time**: `2025-10-01T21:58:37.509446`

#### Content Preview

```rust
use super::*;

#[route("/favicon.ico")]
#[prologue_macros(
  get,
  response_status_code(301),
  response_header(LOCATION => LOGO_IMG_URL)
)]
pub async fn handle(ctx: Context) {}

```

### 📄 File #517 - `mod.rs`
- **Path**: `hyperlane-quick-start\app\controller\favicon\mod.rs`
- **Size**: `88 B`
- **Modified Time**: `2025-10-01T21:58:37.509446`

#### Content Preview

```rust
mod r#fn;

pub use r#fn::*;

use super::*;
use hyperlane_config::business::logo_img::*;

```

### 📄 File #518 - `fn.rs`
- **Path**: `hyperlane-quick-start\app\controller\hello\fn.rs`
- **Size**: `227 B`
- **Modified Time**: `2025-10-01T21:58:37.517108`

#### Content Preview

```rust
use super::*;

#[route("/hello/{name}")]
#[prologue_macros(
  methods(get, post),
  route_param(NAME_KEY => name_opt),
  response_body(format!("Hello {}", name_opt.unwrap_or_default())),
)]
pub async fn handle(ctx: Context) {}

```

### 📄 File #519 - `mod.rs`
- **Path**: `hyperlane-quick-start\app\controller\hello\mod.rs`
- **Size**: `85 B`
- **Modified Time**: `2025-09-15T22:37:17.327740`

#### Content Preview

```rust
mod r#fn;

pub use r#fn::*;

use super::*;
use hyperlane_config::business::hello::*;

```

### 📄 File #520 - `fn.rs`
- **Path**: `hyperlane-quick-start\app\controller\websocket\fn.rs`
- **Size**: `342 B`
- **Modified Time**: `2025-09-15T22:37:17.327740`

#### Content Preview

```rust
use super::*;

#[ws]
#[route("/websocket")]
#[ws_from_stream(request)]
pub async fn handle(ctx: Context) {
    println_success!("WebSocket request received");
    let request_body: &RequestBody = request.get_body();
    let _ = ctx.set_response_body(&request_body).await;
    ctx.try_get_send_body_hook().await.unwrap()(ctx.clone()).await;
}

```

### 📄 File #521 - `mod.rs`
- **Path**: `hyperlane-quick-start\app\controller\websocket\mod.rs`
- **Size**: `43 B`
- **Modified Time**: `2025-09-15T22:37:17.327740`

#### Content Preview

```rust
mod r#fn;

pub use r#fn::*;

use super::*;

```

### 📄 File #522 - `mod.rs`
- **Path**: `hyperlane-quick-start\app\exception\mod.rs`
- **Size**: `34 B`
- **Modified Time**: `2025-09-15T22:37:17.327740`

#### Content Preview

```rust
pub mod framework;

use super::*;

```

### 📄 File #523 - `fn.rs`
- **Path**: `hyperlane-quick-start\app\exception\framework\fn.rs`
- **Size**: `621 B`
- **Modified Time**: `2025-10-01T21:58:37.522858`

#### Content Preview

```rust
use super::*;

#[panic_hook]
#[epilogue_macros(
    clear_response_headers,
    response_status_code(500),
    response_body(&response_body),
    response_header(SERVER => HYPERLANE),
    response_version(HttpVersion::HTTP1_1),
    response_header(CONTENT_TYPE, &content_type),
    send
)]
pub async fn panic_hook(ctx: Context) {
    let error: Panic = ctx.try_get_panic().await.unwrap_or_default();
    let response_body: String = error.to_string();
    log_error(&response_body).await;
    println_error!(response_body);
    let content_type: String = ContentType::format_content_type_with_charset(TEXT_PLAIN, UTF8);
}

```

### 📄 File #524 - `mod.rs`
- **Path**: `hyperlane-quick-start\app\exception\framework\mod.rs`
- **Size**: `43 B`
- **Modified Time**: `2025-09-15T22:37:17.327740`

#### Content Preview

```rust
mod r#fn;

pub use r#fn::*;

use super::*;

```

### 📄 File #525 - `mod.rs`
- **Path**: `hyperlane-quick-start\app\filter\mod.rs`
- **Size**: `1 B`
- **Modified Time**: `2025-09-15T22:37:17.328740`

#### Content Preview

```rust


```

### 📄 File #526 - `mod.rs`
- **Path**: `hyperlane-quick-start\app\mapper\mod.rs`
- **Size**: `1 B`
- **Modified Time**: `2025-09-15T22:37:17.328740`

#### Content Preview

```rust


```

### 📄 File #527 - `mod.rs`
- **Path**: `hyperlane-quick-start\app\middleware\mod.rs`
- **Size**: `50 B`
- **Modified Time**: `2025-09-15T22:37:17.328740`

#### Content Preview

```rust
pub mod request;
pub mod response;

use super::*;

```

### 📄 File #528 - `mod.rs`
- **Path**: `hyperlane-quick-start\app\middleware\request\mod.rs`
- **Size**: `79 B`
- **Modified Time**: `2025-09-15T22:37:17.329739`

#### Content Preview

```rust
pub mod cross;
pub mod response;
pub mod send;
pub mod upgrade;

use super::*;

```

### 📄 File #529 - `fn.rs`
- **Path**: `hyperlane-quick-start\app\middleware\request\cross\fn.rs`
- **Size**: `311 B`
- **Modified Time**: `2025-09-15T22:37:17.329739`

#### Content Preview

```rust
use super::*;

#[request_middleware(1)]
#[response_version(HttpVersion::HTTP1_1)]
#[response_header(ACCESS_CONTROL_ALLOW_ORIGIN => WILDCARD_ANY)]
#[response_header(ACCESS_CONTROL_ALLOW_METHODS => ALL_METHODS)]
#[response_header(ACCESS_CONTROL_ALLOW_HEADERS => WILDCARD_ANY)]
pub async fn cross(ctx: Context) {}

```

### 📄 File #530 - `mod.rs`
- **Path**: `hyperlane-quick-start\app\middleware\request\cross\mod.rs`
- **Size**: `43 B`
- **Modified Time**: `2025-09-15T22:37:17.329739`

#### Content Preview

```rust
mod r#fn;

pub use r#fn::*;

use super::*;

```

### 📄 File #531 - `fn.rs`
- **Path**: `hyperlane-quick-start\app\middleware\request\response\fn.rs`
- **Size**: `808 B`
- **Modified Time**: `2025-09-15T22:37:17.329739`

#### Content Preview

```rust
use super::*;

#[request_middleware(2)]
#[response_header(DATE => gmt())]
#[response_header(SERVER => HYPERLANE)]
#[response_header(CONNECTION => KEEP_ALIVE)]
#[response_header(CONTENT_TYPE => TEXT_HTML)]
pub async fn response_header(ctx: Context) {
    let socket_addr_string: String = ctx.get_socket_addr_string().await;
    let content_type: String = ContentType::format_content_type_with_charset(TEXT_HTML, UTF8);
    ctx.set_response_header(CONTENT_TYPE, &content_type)
        .await
        .set_response_header("SocketAddr", &socket_addr_string)
        .await;
}

#[request_middleware(3)]
#[response_status_code(200)]
pub async fn response_status_code(ctx: Context) {}

#[request_middleware(4)]
#[response_body(INDEX_HTML.replace("{{ time }}", &time()))]
pub async fn response_body(ctx: Context) {}

```

### 📄 File #532 - `mod.rs`
- **Path**: `hyperlane-quick-start\app\middleware\request\response\mod.rs`
- **Size**: `89 B`
- **Modified Time**: `2025-09-15T22:37:17.329739`

#### Content Preview

```rust
mod r#fn;

pub use r#fn::*;

use super::*;
use hyperlane_config::business::templates::*;

```

### 📄 File #533 - `fn.rs`
- **Path**: `hyperlane-quick-start\app\middleware\request\send\fn.rs`
- **Size**: `137 B`
- **Modified Time**: `2025-09-15T22:37:17.329739`

#### Content Preview

```rust
use super::*;

#[ws]
#[request_middleware(6)]
pub async fn send_body(ctx: Context) {
    ctx.set_send_body_hook(send_body_hook).await;
}

```

### 📄 File #534 - `mod.rs`
- **Path**: `hyperlane-quick-start\app\middleware\request\send\mod.rs`
- **Size**: `65 B`
- **Modified Time**: `2025-09-15T22:37:17.329739`

#### Content Preview

```rust
mod r#fn;

pub use r#fn::*;

use super::*;
use service::send::*;

```

### 📄 File #535 - `fn.rs`
- **Path**: `hyperlane-quick-start\app\middleware\request\upgrade\fn.rs`
- **Size**: `411 B`
- **Modified Time**: `2025-10-01T21:58:37.527873`

#### Content Preview

```rust
use super::*;

#[ws]
#[request_middleware(5)]
#[epilogue_macros(
    response_body(&vec![]),
    response_status_code(101),
    response_header(UPGRADE => WEBSOCKET),
    response_header(CONNECTION => UPGRADE),
    response_header(SEC_WEBSOCKET_ACCEPT => WebSocketFrame::generate_accept_key(&ctx.try_get_request_header_back(SEC_WEBSOCKET_KEY).await.unwrap())),
    send
)]
pub async fn upgrade(ctx: Context) {}

```

### 📄 File #536 - `mod.rs`
- **Path**: `hyperlane-quick-start\app\middleware\request\upgrade\mod.rs`
- **Size**: `43 B`
- **Modified Time**: `2025-09-15T22:37:17.330739`

#### Content Preview

```rust
mod r#fn;

pub use r#fn::*;

use super::*;

```

### 📄 File #537 - `mod.rs`
- **Path**: `hyperlane-quick-start\app\middleware\response\mod.rs`
- **Size**: `42 B`
- **Modified Time**: `2025-09-15T22:37:17.330739`

#### Content Preview

```rust
pub mod log;
pub mod send;

use super::*;

```

### 📄 File #538 - `fn.rs`
- **Path**: `hyperlane-quick-start\app\middleware\response\log\fn.rs`
- **Size**: `264 B`
- **Modified Time**: `2025-09-15T22:37:17.330739`

#### Content Preview

```rust
use super::*;

#[response_middleware(2)]
pub async fn log(ctx: Context) {
    let request: String = ctx.get_request().await.get_string();
    let response: String = ctx.get_response().await.get_string();
    log_info(request).await;
    log_info(response).await
}

```

### 📄 File #539 - `mod.rs`
- **Path**: `hyperlane-quick-start\app\middleware\response\log\mod.rs`
- **Size**: `43 B`
- **Modified Time**: `2025-09-15T22:37:17.330739`

#### Content Preview

```rust
mod r#fn;

pub use r#fn::*;

use super::*;

```

### 📄 File #540 - `fn.rs`
- **Path**: `hyperlane-quick-start\app\middleware\response\send\fn.rs`
- **Size**: `161 B`
- **Modified Time**: `2025-10-01T21:58:37.527873`

#### Content Preview

```rust
use super::*;

#[response_middleware(1)]
#[epilogue_macros(http, reject(ctx.get_request_upgrade_type().await.is_ws()), send)]
pub async fn send(ctx: Context) {}

```

### 📄 File #541 - `mod.rs`
- **Path**: `hyperlane-quick-start\app\middleware\response\send\mod.rs`
- **Size**: `43 B`
- **Modified Time**: `2025-09-15T22:37:17.330739`

#### Content Preview

```rust
mod r#fn;

pub use r#fn::*;

use super::*;

```

### 📄 File #542 - `mod.rs`
- **Path**: `hyperlane-quick-start\app\model\mod.rs`
- **Size**: `176 B`
- **Modified Time**: `2025-09-15T22:37:17.332739`

#### Content Preview

```rust
pub mod application;
pub mod bean;
pub mod business;
pub mod data;
pub mod data_access;
pub mod data_transfer;
pub mod domain;
pub mod param;
pub mod persistent;
pub mod view;

```

### 📄 File #543 - `mod.rs`
- **Path**: `hyperlane-quick-start\app\model\application\mod.rs`
- **Size**: `1 B`
- **Modified Time**: `2025-09-15T22:37:17.331741`

#### Content Preview

```rust


```

### 📄 File #544 - `mod.rs`
- **Path**: `hyperlane-quick-start\app\model\bean\mod.rs`
- **Size**: `1 B`
- **Modified Time**: `2025-09-15T22:37:17.331741`

#### Content Preview

```rust


```

### 📄 File #545 - `mod.rs`
- **Path**: `hyperlane-quick-start\app\model\business\mod.rs`
- **Size**: `1 B`
- **Modified Time**: `2025-09-15T22:37:17.331741`

#### Content Preview

```rust


```

### 📄 File #546 - `mod.rs`
- **Path**: `hyperlane-quick-start\app\model\data\mod.rs`
- **Size**: `1 B`
- **Modified Time**: `2025-09-15T22:37:17.331741`

#### Content Preview

```rust


```

### 📄 File #547 - `mod.rs`
- **Path**: `hyperlane-quick-start\app\model\data_access\mod.rs`
- **Size**: `1 B`
- **Modified Time**: `2025-09-15T22:37:17.331741`

#### Content Preview

```rust


```

### 📄 File #548 - `mod.rs`
- **Path**: `hyperlane-quick-start\app\model\data_transfer\mod.rs`
- **Size**: `1 B`
- **Modified Time**: `2025-09-15T22:37:17.331741`

#### Content Preview

```rust


```

### 📄 File #549 - `mod.rs`
- **Path**: `hyperlane-quick-start\app\model\domain\mod.rs`
- **Size**: `1 B`
- **Modified Time**: `2025-09-15T22:37:17.332739`

#### Content Preview

```rust


```

### 📄 File #550 - `mod.rs`
- **Path**: `hyperlane-quick-start\app\model\param\mod.rs`
- **Size**: `1 B`
- **Modified Time**: `2025-09-15T22:37:17.332739`

#### Content Preview

```rust


```

### 📄 File #551 - `mod.rs`
- **Path**: `hyperlane-quick-start\app\model\persistent\mod.rs`
- **Size**: `1 B`
- **Modified Time**: `2025-09-15T22:37:17.332739`

#### Content Preview

```rust


```

### 📄 File #552 - `mod.rs`
- **Path**: `hyperlane-quick-start\app\model\view\mod.rs`
- **Size**: `1 B`
- **Modified Time**: `2025-09-15T22:37:17.332739`

#### Content Preview

```rust


```

### 📄 File #553 - `mod.rs`
- **Path**: `hyperlane-quick-start\app\service\mod.rs`
- **Size**: `29 B`
- **Modified Time**: `2025-09-15T22:37:17.333740`

#### Content Preview

```rust
pub mod send;

use super::*;

```

### 📄 File #554 - `fn.rs`
- **Path**: `hyperlane-quick-start\app\service\send\fn.rs`
- **Size**: `371 B`
- **Modified Time**: `2025-09-15T22:37:17.333740`

#### Content Preview

```rust
use super::*;

pub async fn send_body_hook(ctx: Context) {
    let body: ResponseBody = ctx.get_response_body().await;
    if ctx.get_request().await.is_ws() {
        let frame_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(&body);
        let _ = ctx.send_body_list_with_data(&frame_list).await;
    } else {
        let _ = ctx.send_body().await;
    }
}

```

### 📄 File #555 - `mod.rs`
- **Path**: `hyperlane-quick-start\app\service\send\mod.rs`
- **Size**: `43 B`
- **Modified Time**: `2025-09-15T22:37:17.333740`

#### Content Preview

```rust
mod r#fn;

pub use r#fn::*;

use super::*;

```

### 📄 File #556 - `mod.rs`
- **Path**: `hyperlane-quick-start\app\utils\mod.rs`
- **Size**: `1 B`
- **Modified Time**: `2025-09-15T22:37:17.333740`

#### Content Preview

```rust


```

### 📄 File #557 - `mod.rs`
- **Path**: `hyperlane-quick-start\app\view\mod.rs`
- **Size**: `1 B`
- **Modified Time**: `2025-09-15T22:37:17.333740`

#### Content Preview

```rust


```

### 📄 File #558 - `Cargo.toml`
- **Path**: `hyperlane-quick-start\config\Cargo.toml`
- **Size**: `182 B`
- **Modified Time**: `2025-09-15T22:37:17.333740`

#### Content Preview



### 📄 File #559 - `lib.rs`
- **Path**: `hyperlane-quick-start\config\lib.rs`
- **Size**: `73 B`
- **Modified Time**: `2025-10-01T21:58:37.543855`

#### Content Preview

```rust
pub mod business;
pub mod framework;
pub mod process;

use hyperlane::*;

```

### 📄 File #560 - `mod.rs`
- **Path**: `hyperlane-quick-start\config\business\mod.rs`
- **Size**: `71 B`
- **Modified Time**: `2025-09-15T22:37:17.334894`

#### Content Preview

```rust
pub mod hello;
pub mod logo_img;
pub mod not_found;
pub mod templates;

```

### 📄 File #561 - `const.rs`
- **Path**: `hyperlane-quick-start\config\business\hello\const.rs`
- **Size**: `43 B`
- **Modified Time**: `2025-10-01T21:58:37.534840`

#### Content Preview

```rust
pub const NAME_KEY: &'static str = "name";

```

### 📄 File #562 - `mod.rs`
- **Path**: `hyperlane-quick-start\config\business\hello\mod.rs`
- **Size**: `34 B`
- **Modified Time**: `2025-09-15T22:37:17.334894`

#### Content Preview

```rust
mod r#const;

pub use r#const::*;

```

### 📄 File #563 - `const.rs`
- **Path**: `hyperlane-quick-start\config\business\logo_img\const.rs`
- **Size**: `82 B`
- **Modified Time**: `2025-10-01T21:58:37.534840`

#### Content Preview

```rust
pub const LOGO_IMG_URL: &'static str = "https://docs.ltpp.vip/img/hyperlane.png";

```

### 📄 File #564 - `mod.rs`
- **Path**: `hyperlane-quick-start\config\business\logo_img\mod.rs`
- **Size**: `34 B`
- **Modified Time**: `2025-09-15T22:37:17.334894`

#### Content Preview

```rust
mod r#const;

pub use r#const::*;

```

### 📄 File #565 - `const.rs`
- **Path**: `hyperlane-quick-start\config\business\not_found\const.rs`
- **Size**: `109 B`
- **Modified Time**: `2025-10-01T21:58:37.543855`

#### Content Preview

```rust
pub const NOT_FOUND_HTML: &'static str =
    include_str!("../../../resources/static/not_found/index.html");

```

### 📄 File #566 - `mod.rs`
- **Path**: `hyperlane-quick-start\config\business\not_found\mod.rs`
- **Size**: `34 B`
- **Modified Time**: `2025-09-15T22:37:17.334894`

#### Content Preview

```rust
mod r#const;

pub use r#const::*;

```

### 📄 File #567 - `const.rs`
- **Path**: `hyperlane-quick-start\config\business\templates\const.rs`
- **Size**: `100 B`
- **Modified Time**: `2025-10-01T21:58:37.543855`

#### Content Preview

```rust
pub const INDEX_HTML: &'static str = include_str!("../../../resources/templates/index/index.html");

```

### 📄 File #568 - `mod.rs`
- **Path**: `hyperlane-quick-start\config\business\templates\mod.rs`
- **Size**: `34 B`
- **Modified Time**: `2025-09-15T22:37:17.335894`

#### Content Preview

```rust
mod r#const;

pub use r#const::*;

```

### 📄 File #569 - `const.rs`
- **Path**: `hyperlane-quick-start\config\framework\const.rs`
- **Size**: `449 B`
- **Modified Time**: `2025-10-01T21:58:37.543855`

#### Content Preview

```rust
use super::*;

pub const SERVER_PORT: usize = 60000;
pub const SERVER_HOST: &'static str = "0.0.0.0";
pub const SERVER_BUFFER: usize = 4096;
pub const SERVER_LOG_SIZE: usize = 100_024_000;
pub const SERVER_LOG_DIR: &'static str = "./tmp/logs";
pub const SERVER_INNER_PRINT: bool = true;
pub const SERVER_INNER_LOG: bool = true;
pub const SERVER_NODELAY: bool = false;
pub const SERVER_LINGER: OptionDuration = None;
pub const SERVER_TTI: u32 = 128;

```

### 📄 File #570 - `mod.rs`
- **Path**: `hyperlane-quick-start\config\framework\mod.rs`
- **Size**: `49 B`
- **Modified Time**: `2025-09-15T22:37:17.335894`

#### Content Preview

```rust
mod r#const;

pub use r#const::*;

use super::*;

```

### 📄 File #571 - `const.rs`
- **Path**: `hyperlane-quick-start\config\process\const.rs`
- **Size**: `71 B`
- **Modified Time**: `2025-10-01T21:58:37.560829`

#### Content Preview

```rust
pub const PID_FILE_PATH: &'static str = "./tmp/process/hyperlane.pid";

```

### 📄 File #572 - `mod.rs`
- **Path**: `hyperlane-quick-start\config\process\mod.rs`
- **Size**: `34 B`
- **Modified Time**: `2025-10-01T21:58:37.561336`

#### Content Preview

```rust
mod r#const;

pub use r#const::*;

```

### 📄 File #573 - `Cargo.toml`
- **Path**: `hyperlane-quick-start\init\Cargo.toml`
- **Size**: `298 B`
- **Modified Time**: `2025-09-15T22:37:17.335894`

#### Content Preview



### 📄 File #574 - `lib.rs`
- **Path**: `hyperlane-quick-start\init\lib.rs`
- **Size**: `80 B`
- **Modified Time**: `2025-09-15T22:37:17.336894`

#### Content Preview

```rust
pub mod business;
pub mod framework;

use hyperlane::*;
use hyperlane_utils::*;

```

### 📄 File #575 - `mod.rs`
- **Path**: `hyperlane-quick-start\init\business\mod.rs`
- **Size**: `1 B`
- **Modified Time**: `2025-09-15T22:37:17.335894`

#### Content Preview

```rust


```

### 📄 File #576 - `mod.rs`
- **Path**: `hyperlane-quick-start\init\framework\mod.rs`
- **Size**: `47 B`
- **Modified Time**: `2025-09-15T22:37:17.336894`

#### Content Preview

```rust
pub mod shutdown;
pub mod wait;

use super::*;

```

### 📄 File #577 - `fn.rs`
- **Path**: `hyperlane-quick-start\init\framework\shutdown\fn.rs`
- **Size**: `251 B`
- **Modified Time**: `2025-10-01T21:58:37.565503`

#### Content Preview

```rust
use super::*;

pub fn set_shutdown(shutdown: ArcFnPinBoxFutureSend<()>) {
    let _ = SHUTDOWN.set(shutdown);
}

pub fn shutdown() -> ArcFnPinBoxFutureSend<()> {
    SHUTDOWN
        .get_or_init(|| Arc::new(|| Box::pin(async {})))
        .clone()
}

```

### 📄 File #578 - `mod.rs`
- **Path**: `hyperlane-quick-start\init\framework\shutdown\mod.rs`
- **Size**: `107 B`
- **Modified Time**: `2025-09-15T22:37:17.336894`

#### Content Preview

```rust
mod r#fn;
mod r#static;

pub use r#fn::*;

use super::*;
use r#static::*;

use std::sync::{Arc, OnceLock};

```

### 📄 File #579 - `static.rs`
- **Path**: `hyperlane-quick-start\init\framework\shutdown\static.rs`
- **Size**: `98 B`
- **Modified Time**: `2025-09-15T22:37:17.336894`

#### Content Preview

```rust
use super::*;

pub(super) static SHUTDOWN: OnceLock<ArcFnPinBoxFutureSend<()>> = OnceLock::new();

```

### 📄 File #580 - `fn.rs`
- **Path**: `hyperlane-quick-start\init\framework\wait\fn.rs`
- **Size**: `1,403 B`
- **Modified Time**: `2025-10-01T21:58:37.569735`

#### Content Preview

```rust
use super::*;

#[hyperlane(config: ServerConfig)]
async fn configure_config(server: &Server) {
    config.host(SERVER_HOST).await;
    config.port(SERVER_PORT).await;
    config.ttl(SERVER_TTI).await;
    config.linger(SERVER_LINGER).await;
    config.nodelay(SERVER_NODELAY).await;
    config.buffer(SERVER_BUFFER).await;
    server.config(config).await;
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
    configure_config(&server).await;
    println_success!("Server initialization successful");
    let server_result: ServerResult<ServerHook> = server.run().await;
    match server_result {
        Ok(server_hook) => {
            let host_port: String = format!("{SERVER_HOST}:{SERVER_PORT}");
            println_success!("Server listen in: ", host_port);
            let shutdown: ArcFnPinBoxFutureSend<()> = server_hook.get_shutdown_hook().clone();
            set_shutdown(shutdown);
            server_hook.wait().await;
        }
        Err(server_error) => println_error!("Server run error: ", server_error),
    }
}

pub fn run() {
    runtime().block_on(process::create(create_server));
}

```

### 📄 File #581 - `mod.rs`
- **Path**: `hyperlane-quick-start\init\framework\wait\mod.rs`
- **Size**: `213 B`
- **Modified Time**: `2025-10-01T21:58:37.570259`

#### Content Preview

```rust
mod r#fn;

pub use r#fn::*;

use super::{shutdown::*, *};
#[allow(unused_imports)]
use hyperlane_app::*;
use hyperlane_config::framework::*;
use hyperlane_plugin::process;

use tokio::runtime::{Builder, Runtime};

```

### 📄 File #582 - `Cargo.toml`
- **Path**: `hyperlane-quick-start\plugin\Cargo.toml`
- **Size**: `223 B`
- **Modified Time**: `2025-09-15T22:37:17.336894`

#### Content Preview



### 📄 File #583 - `lib.rs`
- **Path**: `hyperlane-quick-start\plugin\lib.rs`
- **Size**: `55 B`
- **Modified Time**: `2025-10-01T21:58:37.577576`

#### Content Preview

```rust
pub mod log;
pub mod process;

use hyperlane_utils::*;

```

### 📄 File #584 - `fn.rs`
- **Path**: `hyperlane-quick-start\plugin\log\fn.rs`
- **Size**: `345 B`
- **Modified Time**: `2025-09-15T22:37:17.337896`

#### Content Preview

```rust
use super::*;

pub async fn log_info<T>(data: T)
where
    T: AsRef<str>,
{
    LOG.async_info(data, log_handler).await;
}

pub async fn log_debug<T>(data: T)
where
    T: AsRef<str>,
{
    LOG.async_debug(data, log_handler).await;
}

pub async fn log_error<T>(data: T)
where
    T: AsRef<str>,
{
    LOG.async_error(data, log_handler).await;
}

```

### 📄 File #585 - `mod.rs`
- **Path**: `hyperlane-quick-start\plugin\log\mod.rs`
- **Size**: `158 B`
- **Modified Time**: `2025-09-15T22:37:17.337896`

#### Content Preview

```rust
mod r#fn;
mod r#static;

pub use r#fn::*;
pub use r#static::*;

use super::*;
use hyperlane_config::framework::*;
use hyperlane_utils::once_cell::sync::Lazy;

```

### 📄 File #586 - `static.rs`
- **Path**: `hyperlane-quick-start\plugin\log\static.rs`
- **Size**: `181 B`
- **Modified Time**: `2025-09-15T22:37:17.337896`

#### Content Preview

```rust
use super::*;

pub static LOG: Lazy<Log> = Lazy::new(|| {
    let mut log: Log = Log::default();
    log.path(SERVER_LOG_DIR);
    log.limit_file_size(SERVER_LOG_SIZE);
    log
});

```

### 📄 File #587 - `fn.rs`
- **Path**: `hyperlane-quick-start\plugin\process\fn.rs`
- **Size**: `1,975 B`
- **Modified Time**: `2025-10-01T21:58:37.578093`

#### Content Preview

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
        .set_pid_file(PID_FILE_PATH)
        .set_server_hook(server_hook);
    let is_daemon: bool = args.len() >= 3 && args[2].to_lowercase() == "-d";
    let start_server = || async {
        if is_daemon {
            match manager.start_daemon().await {
                Ok(_) => println_success!("Server started in background successfully"),
                Err(e) => println_error!(format!("Error starting server in background: {e}")),
            };
        } else {
            println_success!("Server started successfully");
            manager.start().await;
        }
    };
    let stop_server = || async {
        match manager.stop().await {
            Ok(_) => println_success!("Server stopped successfully"),
            Err(e) => println_error!(format!("Error stopping server: {e}")),
        };
    };
    let hot_restart_server = || async {
        match manager
            .watch_detached(&["--clear", "--skip-local-deps", "-q", "-x", "run"])
            .await
        {
            Ok(_) => println_success!("Server started successfully"),
            Err(e) => println_error!(format!("Error starting server in background: {e}")),
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
        "hot" => hot_restart_server().await,
        _ => {
            println_error!(format!("Invalid command: {command}"));
        }
    }
}

```

### 📄 File #588 - `mod.rs`
- **Path**: `hyperlane-quick-start\plugin\process\mod.rs`
- **Size**: `116 B`
- **Modified Time**: `2025-10-01T21:58:37.581639`

#### Content Preview

```rust
mod r#fn;

pub use r#fn::*;

use super::*;
use hyperlane_config::process::*;

use std::{env::args, future::Future};

```

### 📄 File #589 - `index.html`
- **Path**: `hyperlane-quick-start\resources\static\not_found\index.html`
- **Size**: `788 B`
- **Modified Time**: `2025-10-01T21:58:37.582152`

#### Content Preview

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
      >
    </p>
  </body>
</html>

```

### 📄 File #590 - `index.html`
- **Path**: `hyperlane-quick-start\resources\templates\index\index.html`
- **Size**: `798 B`
- **Modified Time**: `2025-10-01T21:58:37.582673`

#### Content Preview

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
      >
    </p>
  </body>
</html>

```

### 📄 File #591 - `main.rs`
- **Path**: `hyperlane-quick-start\src\main.rs`
- **Size**: `79 B`
- **Modified Time**: `2025-09-15T22:37:17.338894`

#### Content Preview

```rust
use hyperlane_init;

fn main() {
    hyperlane_init::framework::wait::run();
}

```

### 📄 File #592 - `.gitignore`
- **Path**: `hyperlane-time\.gitignore`
- **Size**: `18 B`
- **Modified Time**: `2025-09-15T22:37:15.186780`

#### Content Preview



### 📄 File #593 - `Cargo.toml`
- **Path**: `hyperlane-time\Cargo.toml`
- **Size**: `746 B`
- **Modified Time**: `2025-09-15T22:37:15.186780`

#### Content Preview



### 📄 File #594 - `LICENSE`
- **Path**: `hyperlane-time\LICENSE`
- **Size**: `1,066 B`
- **Modified Time**: `2025-09-15T22:37:15.186780`

#### Content Preview



### 📄 File #595 - `README.md`
- **Path**: `hyperlane-time\README.md`
- **Size**: `2,085 B`
- **Modified Time**: `2025-09-15T22:37:15.187787`

#### Content Preview

```markdown
<center>

## hyperlane-time

[![](https://img.shields.io/crates/v/hyperlane-time.svg)](https://crates.io/crates/hyperlane-time)
[![](https://img.shields.io/crates/d/hyperlane-time.svg)](https://img.shields.io/crates/d/hyperlane-time.svg)
[![](https://docs.rs/hyperlane-time/badge.svg)](https://docs.rs/hyperlane-time)
[![](https://github.com/hyperlane-dev/hyperlane-time/workflows/Rust/badge.svg)](https://github.com/hyperlane-dev/hyperlane-time/actions?query=workflow:Rust)
[![](https://img.shields.io/crates/l/hyperlane-time.svg)](./LICENSE)

</center>

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

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Contact

For any inquiries, please reach out to the author at [root@ltpp.vip](mailto:root@ltpp.vip).

```

### 📄 File #596 - `config`
- **Path**: `hyperlane-time\.git\config`
- **Size**: `324 B`
- **Modified Time**: `2025-09-15T22:37:15.180588`

#### Content Preview



### 📄 File #597 - `description`
- **Path**: `hyperlane-time\.git\description`
- **Size**: `73 B`
- **Modified Time**: `2025-09-15T22:37:12.972096`

#### Content Preview



### 📄 File #598 - `FETCH_HEAD`
- **Path**: `hyperlane-time\.git\FETCH_HEAD`
- **Size**: `109 B`
- **Modified Time**: `2025-10-01T21:58:34.908391`

#### Content Preview



### 📄 File #599 - `HEAD`
- **Path**: `hyperlane-time\.git\HEAD`
- **Size**: `23 B`
- **Modified Time**: `2025-09-15T22:37:15.173589`

#### Content Preview



### 📄 File #600 - `index`
- **Path**: `hyperlane-time\.git\index`
- **Size**: `989 B`
- **Modified Time**: `2025-09-15T22:44:11.387195`

#### Content Preview



### 📄 File #601 - `ORIG_HEAD`
- **Path**: `hyperlane-time\.git\ORIG_HEAD`
- **Size**: `41 B`
- **Modified Time**: `2025-09-15T22:44:12.969263`

#### Content Preview



### 📄 File #602 - `packed-refs`
- **Path**: `hyperlane-time\.git\packed-refs`
- **Size**: `114 B`
- **Modified Time**: `2025-09-15T22:37:15.164995`

#### Content Preview



### 📄 File #603 - `shallow`
- **Path**: `hyperlane-time\.git\shallow`
- **Size**: `41 B`
- **Modified Time**: `2025-09-15T22:37:15.106441`

#### Content Preview



### 📄 File #604 - `applypatch-msg.sample`
- **Path**: `hyperlane-time\.git\hooks\applypatch-msg.sample`
- **Size**: `478 B`
- **Modified Time**: `2025-09-15T22:37:12.972096`

#### Content Preview



### 📄 File #605 - `commit-msg.sample`
- **Path**: `hyperlane-time\.git\hooks\commit-msg.sample`
- **Size**: `896 B`
- **Modified Time**: `2025-09-15T22:37:12.972096`

#### Content Preview



### 📄 File #606 - `fsmonitor-watchman.sample`
- **Path**: `hyperlane-time\.git\hooks\fsmonitor-watchman.sample`
- **Size**: `4,726 B`
- **Modified Time**: `2025-09-15T22:37:12.972096`

#### Content Preview



### 📄 File #607 - `post-update.sample`
- **Path**: `hyperlane-time\.git\hooks\post-update.sample`
- **Size**: `189 B`
- **Modified Time**: `2025-09-15T22:37:12.973096`

#### Content Preview



### 📄 File #608 - `pre-applypatch.sample`
- **Path**: `hyperlane-time\.git\hooks\pre-applypatch.sample`
- **Size**: `424 B`
- **Modified Time**: `2025-09-15T22:37:12.973096`

#### Content Preview



### 📄 File #609 - `pre-commit.sample`
- **Path**: `hyperlane-time\.git\hooks\pre-commit.sample`
- **Size**: `1,649 B`
- **Modified Time**: `2025-09-15T22:37:12.973096`

#### Content Preview



### 📄 File #610 - `pre-merge-commit.sample`
- **Path**: `hyperlane-time\.git\hooks\pre-merge-commit.sample`
- **Size**: `416 B`
- **Modified Time**: `2025-09-15T22:37:12.973096`

#### Content Preview



### 📄 File #611 - `pre-push.sample`
- **Path**: `hyperlane-time\.git\hooks\pre-push.sample`
- **Size**: `1,374 B`
- **Modified Time**: `2025-09-15T22:37:12.974097`

#### Content Preview



### 📄 File #612 - `pre-rebase.sample`
- **Path**: `hyperlane-time\.git\hooks\pre-rebase.sample`
- **Size**: `4,898 B`
- **Modified Time**: `2025-09-15T22:37:12.974097`

#### Content Preview



### 📄 File #613 - `pre-receive.sample`
- **Path**: `hyperlane-time\.git\hooks\pre-receive.sample`
- **Size**: `544 B`
- **Modified Time**: `2025-09-15T22:37:12.974097`

#### Content Preview



### 📄 File #614 - `prepare-commit-msg.sample`
- **Path**: `hyperlane-time\.git\hooks\prepare-commit-msg.sample`
- **Size**: `1,492 B`
- **Modified Time**: `2025-09-15T22:37:12.974097`

#### Content Preview



### 📄 File #615 - `push-to-checkout.sample`
- **Path**: `hyperlane-time\.git\hooks\push-to-checkout.sample`
- **Size**: `2,783 B`
- **Modified Time**: `2025-09-15T22:37:12.974097`

#### Content Preview



### 📄 File #616 - `sendemail-validate.sample`
- **Path**: `hyperlane-time\.git\hooks\sendemail-validate.sample`
- **Size**: `2,308 B`
- **Modified Time**: `2025-09-15T22:37:12.974097`

#### Content Preview



### 📄 File #617 - `update.sample`
- **Path**: `hyperlane-time\.git\hooks\update.sample`
- **Size**: `3,650 B`
- **Modified Time**: `2025-09-15T22:37:12.975098`

#### Content Preview



### 📄 File #618 - `exclude`
- **Path**: `hyperlane-time\.git\info\exclude`
- **Size**: `240 B`
- **Modified Time**: `2025-09-15T22:37:12.975098`

#### Content Preview



### 📄 File #619 - `HEAD`
- **Path**: `hyperlane-time\.git\logs\HEAD`
- **Size**: `189 B`
- **Modified Time**: `2025-09-15T22:37:15.174588`

#### Content Preview



### 📄 File #620 - `master`
- **Path**: `hyperlane-time\.git\logs\refs\heads\master`
- **Size**: `189 B`
- **Modified Time**: `2025-09-15T22:37:15.175589`

#### Content Preview



### 📄 File #621 - `HEAD`
- **Path**: `hyperlane-time\.git\logs\refs\remotes\origin\HEAD`
- **Size**: `189 B`
- **Modified Time**: `2025-09-15T22:37:15.172589`

#### Content Preview



### 📄 File #622 - `pack-6e08451308d3bfead0713de09bb80ca471015a9b.idx`
- **Path**: `hyperlane-time\.git\objects\pack\pack-6e08451308d3bfead0713de09bb80ca471015a9b.idx`
- **Size**: `1,520 B`
- **Modified Time**: `2025-09-15T22:37:15.126243`

#### Content Preview



### 📄 File #623 - `pack-6e08451308d3bfead0713de09bb80ca471015a9b.pack`
- **Path**: `hyperlane-time\.git\objects\pack\pack-6e08451308d3bfead0713de09bb80ca471015a9b.pack`
- **Size**: `9,141 B`
- **Modified Time**: `2025-09-15T22:37:15.125739`

#### Content Preview



### 📄 File #624 - `pack-6e08451308d3bfead0713de09bb80ca471015a9b.rev`
- **Path**: `hyperlane-time\.git\objects\pack\pack-6e08451308d3bfead0713de09bb80ca471015a9b.rev`
- **Size**: `116 B`
- **Modified Time**: `2025-09-15T22:37:15.127246`

#### Content Preview



### 📄 File #625 - `master`
- **Path**: `hyperlane-time\.git\refs\heads\master`
- **Size**: `41 B`
- **Modified Time**: `2025-09-15T22:37:15.174588`

#### Content Preview



### 📄 File #626 - `HEAD`
- **Path**: `hyperlane-time\.git\refs\remotes\origin\HEAD`
- **Size**: `32 B`
- **Modified Time**: `2025-09-15T22:37:15.171588`

#### Content Preview



### 📄 File #627 - `v0.7.8`
- **Path**: `hyperlane-time\.git\refs\tags\v0.7.8`
- **Size**: `41 B`
- **Modified Time**: `2025-09-15T22:37:15.170587`

#### Content Preview



### 📄 File #628 - `rust.yml`
- **Path**: `hyperlane-time\.github\workflows\rust.yml`
- **Size**: `9,636 B`
- **Modified Time**: `2025-09-15T22:37:15.186780`

#### Content Preview

```yaml
name: Rust
on:
  push:
    branches: [master]
env:
  CARGO_TERM_COLOR: always
jobs:
  setup:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.read.outputs.version }}
      tag: ${{ steps.read.outputs.tag }}
      package_name: ${{ steps.read.outputs.package_name }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Install rust-toolchain
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
          components: rustfmt, clippy
      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: |
            ~/.cargo/registry
            ~/.cargo/git
            target
          key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}
      - name: Install toml-cli
        run: cargo install toml-cli
      - name: Cache toml-cli
        uses: actions/cache@v3
        with:
          path: ~/.cargo/bin/toml
          key: toml-cli-${{ runner.os }}
      - name: Read cargo metadata
        id: read
        run: |
          VERSION=$(toml get Cargo.toml package.version --raw)
          PACKAGE_NAME=$(toml get Cargo.toml package.name --raw)
          echo "📦 Detected package: $PACKAGE_NAME v$VERSION"
          if [ -z "$VERSION" ] || [ -z "$PACKAGE_NAME" ]; then
            echo "❌ Failed to read package info from Cargo.toml"
          fi
          echo "version=$VERSION" >> $GITHUB_OUTPUT
          echo "tag=v$VERSION" >> $GITHUB_OUTPUT
          echo "package_name=$PACKAGE_NAME" >> $GITHUB_OUTPUT

  check:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup rust
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
          components: rustfmt
      - name: Format check
        run: cargo fmt -- --check

  tests:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Prepare environment
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
      - name: Run tests
        run: cargo test --all-features -- --nocapture

  clippy:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Load clippy
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
          components: clippy
      - name: Run clippy
        run: cargo clippy --all-features -- -A warnings

  build:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup build
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
      - name: Build release
        run: cargo check --release --all-features

  publish:
    needs: [setup, check, tests, clippy, build]
    if: needs.setup.outputs.tag != ''
    runs-on: ubuntu-latest
    outputs:
      published: ${{ steps.publish.outputs.published }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Restore toml-cli
        uses: actions/cache@v3
        with:
          path: ~/.cargo/bin/toml
          key: toml-cli-${{ runner.os }}
      - name: Publish to crates.io
        id: publish
        env:
          CARGO_REGISTRY_TOKEN: ${{ secrets.CARGO_REGISTRY_TOKEN }}
        run: |
          set -e
          echo "published=false" >> $GITHUB_OUTPUT
          echo "${{ secrets.CARGO_REGISTRY_TOKEN }}" | cargo login
          PACKAGE_NAME=$(toml get Cargo.toml package.name --raw)
          VERSION=${{ needs.setup.outputs.version }}
          if cargo publish --allow-dirty; then
            echo "published=true" >> $GITHUB_OUTPUT
            echo "🎉🎉🎉 PUBLISH SUCCESSFUL 🎉🎉🎉"
            echo "✅ Successfully published $PACKAGE_NAME v$VERSION to crates.io"
            echo "📦 Crates.io: [https://crates.io/crates/$PACKAGE_NAME/$VERSION](https://crates.io/crates/$PACKAGE_NAME/$VERSION)"
            echo "📚 Docs.rs: [https://docs.rs/$PACKAGE_NAME/$VERSION](https://docs.rs/$PACKAGE_NAME/$VERSION)"
          else
            echo "❌ Publish failed"
          fi

  release:
    needs: [setup, check, tests, clippy, build]
    permissions:
      contents: write
      packages: write
    if: needs.setup.outputs.tag != ''
    runs-on: ubuntu-latest
    outputs:
      released: ${{ steps.release.outputs.released }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Get package name
        id: package_info
        run: |
          echo "package_name=${{ needs.setup.outputs.package_name }}" >> $GITHUB_OUTPUT
      - name: Check tag status
        id: check_tag
        run: |
          if git tag -l | grep -q "^${{ needs.setup.outputs.tag }}$"; then
            echo "tag_exists=true" >> $GITHUB_OUTPUT
            echo "🏷️ Tag ${{ needs.setup.outputs.tag }} exists locally"
          else
            echo "tag_exists=false" >> $GITHUB_OUTPUT
            echo "🏷️ Tag ${{ needs.setup.outputs.tag }} does not exist locally"
          fi
          if git ls-remote --tags origin | grep -q "refs/tags/${{ needs.setup.outputs.tag }}$"; then
            echo "remote_tag_exists=true" >> $GITHUB_OUTPUT
            echo "🌐 Tag ${{ needs.setup.outputs.tag }} exists on remote"
          else
            echo "remote_tag_exists=false" >> $GITHUB_OUTPUT
            echo "🌐 Tag ${{ needs.setup.outputs.tag }} does not exist on remote"
          fi
      - name: Check release status
        id: check_release
        run: |
          if gh release view "${{ needs.setup.outputs.tag }}" > /dev/null 2>&1; then
            echo "release_exists=true" >> $GITHUB_OUTPUT
            echo "📦 Release ${{ needs.setup.outputs.tag }} already exists"
          else
            echo "release_exists=false" >> $GITHUB_OUTPUT
            echo "📦 Release ${{ needs.setup.outputs.tag }} does not exist"
          fi
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - name: Create or update release
        id: release
        run: |
          set -e
          echo "released=false" >> $GITHUB_OUTPUT
          PACKAGE_NAME="${{ steps.package_info.outputs.package_name }}"
          VERSION="${{ needs.setup.outputs.version }}"
          TAG="${{ needs.setup.outputs.tag }}"
          echo "📦 Building source archives..."
          git archive --format=zip --prefix="${PACKAGE_NAME}-${VERSION}/" HEAD > "${PACKAGE_NAME}-${VERSION}.zip"
          git archive --format=tar.gz --prefix="${PACKAGE_NAME}-${VERSION}/" HEAD > "${PACKAGE_NAME}-${VERSION}.tar.gz"
          if [ "${{ steps.check_release.outputs.release_exists }}" = "true" ]; then
            echo "🔄 Updating existing release: $TAG"
            gh release view "$TAG" --json assets --jq '.assets[].name' | while read asset; do
              if [ -n "$asset" ]; then
                echo "🗑️ Deleting asset: $asset"
                gh release delete-asset "$TAG" "$asset" --yes || true
              fi
            done
            if gh release edit "$TAG" \
              --title "$TAG (Updated $(date '+%Y-%m-%d %H:%M:%S'))" \
              --notes "Release $TAG - Updated at $(date '+%Y-%m-%d %H:%M:%S UTC')
            ## Changes
            - Version: $VERSION
            - Package: $PACKAGE_NAME
            ## Links
            📦 [Crate on crates.io](https://crates.io/crates/$PACKAGE_NAME/$VERSION)
            📚 [Documentation on docs.rs](https://docs.rs/$PACKAGE_NAME/$VERSION)
            📋 [Commit History](https://github.com/${{ github.repository }}/commits/$TAG)" && \
               gh release upload "$TAG" "${PACKAGE_NAME}-${VERSION}.zip" "${PACKAGE_NAME}-${VERSION}.tar.gz" --clobber; then
              echo "released=true" >> $GITHUB_OUTPUT
              echo "✅ Updated release $TAG"
              echo "🔖 Tag: $TAG"
              echo "🚀 Release: [GitHub Release](${{ github.server_url }}/${{ github.repository }}/releases/tag/$TAG)"
            else
              echo "❌ Failed to update release"
            fi
          else
            if [ "${{ steps.check_tag.outputs.remote_tag_exists }}" = "false" ]; then
              echo "🏷️ Creating and pushing tag: $TAG"
              git tag "$TAG"
              git push origin "$TAG"
            fi
            echo "🆕 Creating new release: $TAG"
            if gh release create "$TAG" \
              --title "$TAG (Created $(date '+%Y-%m-%d %H:%M:%S'))" \
              --notes "Release $TAG - Created at $(date '+%Y-%m-%d %H:%M:%S UTC')
            ## Changes
            - Version: $VERSION
            - Package: $PACKAGE_NAME
            ## Links
            📦 [Crate on crates.io](https://crates.io/crates/$PACKAGE_NAME/$VERSION)
            📚 [Documentation on docs.rs](https://docs.rs/$PACKAGE_NAME/$VERSION)
            📋 [Commit History](https://github.com/${{ github.repository }}/commits/$TAG)" \
              --latest && \
               gh release upload "$TAG" "${PACKAGE_NAME}-${VERSION}.zip" "${PACKAGE_NAME}-${VERSION}.tar.gz"; then
              echo "released=true" >> $GITHUB_OUTPUT
              echo "✅ Created release $TAG"
              echo "🔖 Tag: $TAG"
              echo "🚀 Release: [GitHub Release](${{ github.server_url }}/${{ github.repository }}/releases/tag/$TAG)"
            else
              echo "❌ Failed to create release"
            fi
          fi
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

```

### 📄 File #629 - `lib.rs`
- **Path**: `hyperlane-time\src\lib.rs`
- **Size**: `316 B`
- **Modified Time**: `2025-09-15T22:37:15.187787`

#### Content Preview

```rust
//! hyperlane-time
//!
//! A library for fetching the current time based on the system's locale settings.

pub(crate) mod time;

pub use time::r#fn::*;

pub(crate) use time::r#enum::from_env_var;

pub(crate) use std::{
    env, fmt,
    fmt::Write,
    str::FromStr,
    time::{Duration, SystemTime, UNIX_EPOCH},
};

```

### 📄 File #630 - `cfg.rs`
- **Path**: `hyperlane-time\src\time\cfg.rs`
- **Size**: `1,211 B`
- **Modified Time**: `2025-09-15T22:37:15.187787`

#### Content Preview

```rust
#[test]
fn test_lang() {
    use crate::time::r#enum::from_env_var;
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

### 📄 File #631 - `enum.rs`
- **Path**: `hyperlane-time\src\time\enum.rs`
- **Size**: `5,784 B`
- **Modified Time**: `2025-09-15T22:37:15.187787`

#### Content Preview

```rust
use crate::*;

/// Represents supported languages.
///
/// Each variant corresponds to a specific language and locale combination.
#[derive(Debug, Clone, PartialEq)]
pub enum Lang {
    /// English (United States).
    EnUsUtf8,
    /// Chinese (China).
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
        write!(f, "{}", lang_str)
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

/// Implementation of Default trait for Lang.
///
/// Provides a default value for the Lang enum.
impl Default for Lang {
    /// Returns the default language.
    ///
    /// # Returns
    ///
    /// - `Lang` - The default language (Chinese/China).
    fn default() -> Self {
        Lang::ZhCnUtf8
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

```

### 📄 File #632 - `fn.rs`
- **Path**: `hyperlane-time\src\time\fn.rs`
- **Size**: `8,755 B`
- **Modified Time**: `2025-09-15T22:37:15.187787`

#### Content Preview

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

/// Determines if a year is a leap year.
///
/// # Arguments
///
/// - `u64` - The year to check.
///
/// # Returns
///
/// - `bool` - Whether the year is a leap year.
pub fn is_leap_year(year: u64) -> bool {
    (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0)
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
        "{:04}-{:02}-{:02} {:02}:{:02}:{:02}",
        year, month, day, hour, minute, second
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
    write!(&mut date_time, "{:04}-{:02}-{:02}", year, month, day).unwrap_or_default();
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
            return (year, month, (days_since_epoch + 1) as u64);
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
    let hours: u64 = (seconds_of_day / 3600) as u64;
    let minutes: u64 = ((seconds_of_day % 3600) / 60) as u64;
    let seconds: u64 = (seconds_of_day % 60) as u64;
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
        "{:04}-{:02}-{:02} {:02}:{:02}:{:02}.{:03}",
        year, month, day, hour, minute, second, millisecond
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
        "{:04}-{:02}-{:02} {:02}:{:02}:{:02}.{:06}",
        year, month, day, hour, minute, second, microseconds
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

### 📄 File #633 - `mod.rs`
- **Path**: `hyperlane-time\src\time\mod.rs`
- **Size**: `64 B`
- **Modified Time**: `2025-09-15T22:37:15.187787`

#### Content Preview

```rust
pub(crate) mod cfg;
pub(crate) mod r#enum;
pub(crate) mod r#fn;

```

### 📄 File #634 - `.gitignore`
- **Path**: `hyperlane-utils\.gitignore`
- **Size**: `18 B`
- **Modified Time**: `2025-09-15T22:37:22.172645`

#### Content Preview



### 📄 File #635 - `Cargo.toml`
- **Path**: `hyperlane-utils\Cargo.toml`
- **Size**: `1,705 B`
- **Modified Time**: `2025-10-01T21:58:43.209529`

#### Content Preview



### 📄 File #636 - `LICENSE`
- **Path**: `hyperlane-utils\LICENSE`
- **Size**: `1,066 B`
- **Modified Time**: `2025-09-15T22:37:22.172645`

#### Content Preview



### 📄 File #637 - `README.md`
- **Path**: `hyperlane-utils\README.md`
- **Size**: `1,186 B`
- **Modified Time**: `2025-09-15T22:37:22.172645`

#### Content Preview

```markdown
<center>

## hyperlane-utils

[![](https://img.shields.io/crates/v/hyperlane-utils.svg)](https://crates.io/crates/hyperlane-utils)
[![](https://img.shields.io/crates/d/hyperlane-utils.svg)](https://img.shields.io/crates/d/hyperlane-utils.svg)
[![](https://docs.rs/hyperlane-utils/badge.svg)](https://docs.rs/hyperlane-utils)
[![](https://github.com/hyperlane-dev/hyperlane-utils/workflows/Rust/badge.svg)](https://github.com/hyperlane-dev/hyperlane-utils/actions?query=workflow:Rust)
[![](https://img.shields.io/crates/l/hyperlane-utils.svg)](./LICENSE)

</center>

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

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Contact

For any inquiries, please reach out to the author at [root@ltpp.vip](mailto:root@ltpp.vip).

```

### 📄 File #638 - `config`
- **Path**: `hyperlane-utils\.git\config`
- **Size**: `325 B`
- **Modified Time**: `2025-09-15T22:37:22.166642`

#### Content Preview



### 📄 File #639 - `description`
- **Path**: `hyperlane-utils\.git\description`
- **Size**: `73 B`
- **Modified Time**: `2025-09-15T22:37:19.442179`

#### Content Preview



### 📄 File #640 - `FETCH_HEAD`
- **Path**: `hyperlane-utils\.git\FETCH_HEAD`
- **Size**: `473 B`
- **Modified Time**: `2025-10-01T21:58:43.162923`

#### Content Preview



### 📄 File #641 - `HEAD`
- **Path**: `hyperlane-utils\.git\HEAD`
- **Size**: `23 B`
- **Modified Time**: `2025-09-15T22:37:22.158642`

#### Content Preview



### 📄 File #642 - `index`
- **Path**: `hyperlane-utils\.git\index`
- **Size**: `639 B`
- **Modified Time**: `2025-10-01T21:58:43.209529`

#### Content Preview



### 📄 File #643 - `ORIG_HEAD`
- **Path**: `hyperlane-utils\.git\ORIG_HEAD`
- **Size**: `41 B`
- **Modified Time**: `2025-09-15T22:44:19.087178`

#### Content Preview



### 📄 File #644 - `packed-refs`
- **Path**: `hyperlane-utils\.git\packed-refs`
- **Size**: `114 B`
- **Modified Time**: `2025-09-15T22:37:22.148643`

#### Content Preview



### 📄 File #645 - `shallow`
- **Path**: `hyperlane-utils\.git\shallow`
- **Size**: `41 B`
- **Modified Time**: `2025-09-15T22:37:22.041021`

#### Content Preview



### 📄 File #646 - `applypatch-msg.sample`
- **Path**: `hyperlane-utils\.git\hooks\applypatch-msg.sample`
- **Size**: `478 B`
- **Modified Time**: `2025-09-15T22:37:19.442179`

#### Content Preview



### 📄 File #647 - `commit-msg.sample`
- **Path**: `hyperlane-utils\.git\hooks\commit-msg.sample`
- **Size**: `896 B`
- **Modified Time**: `2025-09-15T22:37:19.442179`

#### Content Preview



### 📄 File #648 - `fsmonitor-watchman.sample`
- **Path**: `hyperlane-utils\.git\hooks\fsmonitor-watchman.sample`
- **Size**: `4,726 B`
- **Modified Time**: `2025-09-15T22:37:19.442179`

#### Content Preview



### 📄 File #649 - `post-update.sample`
- **Path**: `hyperlane-utils\.git\hooks\post-update.sample`
- **Size**: `189 B`
- **Modified Time**: `2025-09-15T22:37:19.443183`

#### Content Preview



### 📄 File #650 - `pre-applypatch.sample`
- **Path**: `hyperlane-utils\.git\hooks\pre-applypatch.sample`
- **Size**: `424 B`
- **Modified Time**: `2025-09-15T22:37:19.443183`

#### Content Preview



### 📄 File #651 - `pre-commit.sample`
- **Path**: `hyperlane-utils\.git\hooks\pre-commit.sample`
- **Size**: `1,649 B`
- **Modified Time**: `2025-09-15T22:37:19.443183`

#### Content Preview



### 📄 File #652 - `pre-merge-commit.sample`
- **Path**: `hyperlane-utils\.git\hooks\pre-merge-commit.sample`
- **Size**: `416 B`
- **Modified Time**: `2025-09-15T22:37:19.443183`

#### Content Preview



### 📄 File #653 - `pre-push.sample`
- **Path**: `hyperlane-utils\.git\hooks\pre-push.sample`
- **Size**: `1,374 B`
- **Modified Time**: `2025-09-15T22:37:19.443183`

#### Content Preview



### 📄 File #654 - `pre-rebase.sample`
- **Path**: `hyperlane-utils\.git\hooks\pre-rebase.sample`
- **Size**: `4,898 B`
- **Modified Time**: `2025-09-15T22:37:19.443183`

#### Content Preview



### 📄 File #655 - `pre-receive.sample`
- **Path**: `hyperlane-utils\.git\hooks\pre-receive.sample`
- **Size**: `544 B`
- **Modified Time**: `2025-09-15T22:37:19.444184`

#### Content Preview



### 📄 File #656 - `prepare-commit-msg.sample`
- **Path**: `hyperlane-utils\.git\hooks\prepare-commit-msg.sample`
- **Size**: `1,492 B`
- **Modified Time**: `2025-09-15T22:37:19.444184`

#### Content Preview



### 📄 File #657 - `push-to-checkout.sample`
- **Path**: `hyperlane-utils\.git\hooks\push-to-checkout.sample`
- **Size**: `2,783 B`
- **Modified Time**: `2025-09-15T22:37:19.444184`

#### Content Preview



### 📄 File #658 - `sendemail-validate.sample`
- **Path**: `hyperlane-utils\.git\hooks\sendemail-validate.sample`
- **Size**: `2,308 B`
- **Modified Time**: `2025-09-15T22:37:19.444184`

#### Content Preview



### 📄 File #659 - `update.sample`
- **Path**: `hyperlane-utils\.git\hooks\update.sample`
- **Size**: `3,650 B`
- **Modified Time**: `2025-09-15T22:37:19.444184`

#### Content Preview



### 📄 File #660 - `exclude`
- **Path**: `hyperlane-utils\.git\info\exclude`
- **Size**: `240 B`
- **Modified Time**: `2025-09-15T22:37:19.445184`

#### Content Preview



### 📄 File #661 - `HEAD`
- **Path**: `hyperlane-utils\.git\logs\HEAD`
- **Size**: `343 B`
- **Modified Time**: `2025-10-01T21:58:43.216333`

#### Content Preview



### 📄 File #662 - `master`
- **Path**: `hyperlane-utils\.git\logs\refs\heads\master`
- **Size**: `343 B`
- **Modified Time**: `2025-10-01T21:58:43.217059`

#### Content Preview



### 📄 File #663 - `HEAD`
- **Path**: `hyperlane-utils\.git\logs\refs\remotes\origin\HEAD`
- **Size**: `190 B`
- **Modified Time**: `2025-09-15T22:37:22.158642`

#### Content Preview



### 📄 File #664 - `master`
- **Path**: `hyperlane-utils\.git\logs\refs\remotes\origin\master`
- **Size**: `153 B`
- **Modified Time**: `2025-10-01T21:58:43.102881`

#### Content Preview



### 📄 File #665 - `f3eb9bddac6b16cedc6f87996a3d4e7f946578`
- **Path**: `hyperlane-utils\.git\objects\0c\f3eb9bddac6b16cedc6f87996a3d4e7f946578`
- **Size**: `167 B`
- **Modified Time**: `2025-10-01T21:58:43.035397`

#### Content Preview



### 📄 File #666 - `2f8d9a1b3db3bdb1b7db067b437b28b5fd6797`
- **Path**: `hyperlane-utils\.git\objects\11\2f8d9a1b3db3bdb1b7db067b437b28b5fd6797`
- **Size**: `211 B`
- **Modified Time**: `2025-10-01T21:58:43.045009`

#### Content Preview



### 📄 File #667 - `efaf3ab811cdbc2c4d35a227e3580ef7e9b037`
- **Path**: `hyperlane-utils\.git\objects\13\efaf3ab811cdbc2c4d35a227e3580ef7e9b037`
- **Size**: `211 B`
- **Modified Time**: `2025-10-01T21:58:43.038516`

#### Content Preview



### 📄 File #668 - `9d2e65453f76916c714ebafe77f666ec99cf6c`
- **Path**: `hyperlane-utils\.git\objects\22\9d2e65453f76916c714ebafe77f666ec99cf6c`
- **Size**: `166 B`
- **Modified Time**: `2025-10-01T21:58:43.033816`

#### Content Preview



### 📄 File #669 - `42b4648037f4e680a6ac00f8493832087343d4`
- **Path**: `hyperlane-utils\.git\objects\25\42b4648037f4e680a6ac00f8493832087343d4`
- **Size**: `167 B`
- **Modified Time**: `2025-10-01T21:58:43.036982`

#### Content Preview



### 📄 File #670 - `de6f85aa5602241a9209f14557a546dfefd89d`
- **Path**: `hyperlane-utils\.git\objects\57\de6f85aa5602241a9209f14557a546dfefd89d`
- **Size**: `212 B`
- **Modified Time**: `2025-10-01T21:58:43.039884`

#### Content Preview



### 📄 File #671 - `32acfb7f82699cd6a6459e688ee23e3c6b810f`
- **Path**: `hyperlane-utils\.git\objects\67\32acfb7f82699cd6a6459e688ee23e3c6b810f`
- **Size**: `858 B`
- **Modified Time**: `2025-10-01T21:58:43.045009`

#### Content Preview



### 📄 File #672 - `15af91ad27fd2d1487f7e43b63cedad7a149b8`
- **Path**: `hyperlane-utils\.git\objects\9e\15af91ad27fd2d1487f7e43b63cedad7a149b8`
- **Size**: `858 B`
- **Modified Time**: `2025-10-01T21:58:43.045009`

#### Content Preview



### 📄 File #673 - `f0d36334794774236f41b59168e2686aeae332`
- **Path**: `hyperlane-utils\.git\objects\bb\f0d36334794774236f41b59168e2686aeae332`
- **Size**: `857 B`
- **Modified Time**: `2025-10-01T21:58:43.055554`

#### Content Preview



### 📄 File #674 - `pack-78110a727ebec78f36ff99029a073b184aa2d39d.idx`
- **Path**: `hyperlane-utils\.git\objects\pack\pack-78110a727ebec78f36ff99029a073b184aa2d39d.idx`
- **Size**: `1,380 B`
- **Modified Time**: `2025-09-15T22:37:22.095720`

#### Content Preview



### 📄 File #675 - `pack-78110a727ebec78f36ff99029a073b184aa2d39d.pack`
- **Path**: `hyperlane-utils\.git\objects\pack\pack-78110a727ebec78f36ff99029a073b184aa2d39d.pack`
- **Size**: `5,003 B`
- **Modified Time**: `2025-09-15T22:37:22.095720`

#### Content Preview



### 📄 File #676 - `pack-78110a727ebec78f36ff99029a073b184aa2d39d.rev`
- **Path**: `hyperlane-utils\.git\objects\pack\pack-78110a727ebec78f36ff99029a073b184aa2d39d.rev`
- **Size**: `96 B`
- **Modified Time**: `2025-09-15T22:37:22.096749`

#### Content Preview



### 📄 File #677 - `master`
- **Path**: `hyperlane-utils\.git\refs\heads\master`
- **Size**: `41 B`
- **Modified Time**: `2025-10-01T21:58:43.216333`

#### Content Preview



### 📄 File #678 - `HEAD`
- **Path**: `hyperlane-utils\.git\refs\remotes\origin\HEAD`
- **Size**: `32 B`
- **Modified Time**: `2025-09-15T22:37:22.157643`

#### Content Preview



### 📄 File #679 - `master`
- **Path**: `hyperlane-utils\.git\refs\remotes\origin\master`
- **Size**: `41 B`
- **Modified Time**: `2025-10-01T21:58:43.102881`

#### Content Preview



### 📄 File #680 - `v10.3.8`
- **Path**: `hyperlane-utils\.git\refs\tags\v10.3.8`
- **Size**: `41 B`
- **Modified Time**: `2025-09-15T22:37:22.155643`

#### Content Preview



### 📄 File #681 - `v11.0.0`
- **Path**: `hyperlane-utils\.git\refs\tags\v11.0.0`
- **Size**: `41 B`
- **Modified Time**: `2025-10-01T21:58:43.160923`

#### Content Preview



### 📄 File #682 - `v11.0.1`
- **Path**: `hyperlane-utils\.git\refs\tags\v11.0.1`
- **Size**: `41 B`
- **Modified Time**: `2025-10-01T21:58:43.161923`

#### Content Preview



### 📄 File #683 - `v11.0.2`
- **Path**: `hyperlane-utils\.git\refs\tags\v11.0.2`
- **Size**: `41 B`
- **Modified Time**: `2025-10-01T21:58:43.102881`

#### Content Preview



### 📄 File #684 - `rust.yml`
- **Path**: `hyperlane-utils\.github\workflows\rust.yml`
- **Size**: `9,636 B`
- **Modified Time**: `2025-09-15T22:37:22.172645`

#### Content Preview

```yaml
name: Rust
on:
  push:
    branches: [master]
env:
  CARGO_TERM_COLOR: always
jobs:
  setup:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.read.outputs.version }}
      tag: ${{ steps.read.outputs.tag }}
      package_name: ${{ steps.read.outputs.package_name }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Install rust-toolchain
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
          components: rustfmt, clippy
      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: |
            ~/.cargo/registry
            ~/.cargo/git
            target
          key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}
      - name: Install toml-cli
        run: cargo install toml-cli
      - name: Cache toml-cli
        uses: actions/cache@v3
        with:
          path: ~/.cargo/bin/toml
          key: toml-cli-${{ runner.os }}
      - name: Read cargo metadata
        id: read
        run: |
          VERSION=$(toml get Cargo.toml package.version --raw)
          PACKAGE_NAME=$(toml get Cargo.toml package.name --raw)
          echo "📦 Detected package: $PACKAGE_NAME v$VERSION"
          if [ -z "$VERSION" ] || [ -z "$PACKAGE_NAME" ]; then
            echo "❌ Failed to read package info from Cargo.toml"
          fi
          echo "version=$VERSION" >> $GITHUB_OUTPUT
          echo "tag=v$VERSION" >> $GITHUB_OUTPUT
          echo "package_name=$PACKAGE_NAME" >> $GITHUB_OUTPUT

  check:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup rust
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
          components: rustfmt
      - name: Format check
        run: cargo fmt -- --check

  tests:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Prepare environment
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
      - name: Run tests
        run: cargo test --all-features -- --nocapture

  clippy:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Load clippy
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
          components: clippy
      - name: Run clippy
        run: cargo clippy --all-features -- -A warnings

  build:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup build
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable
      - name: Build release
        run: cargo check --release --all-features

  publish:
    needs: [setup, check, tests, clippy, build]
    if: needs.setup.outputs.tag != ''
    runs-on: ubuntu-latest
    outputs:
      published: ${{ steps.publish.outputs.published }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Restore toml-cli
        uses: actions/cache@v3
        with:
          path: ~/.cargo/bin/toml
          key: toml-cli-${{ runner.os }}
      - name: Publish to crates.io
        id: publish
        env:
          CARGO_REGISTRY_TOKEN: ${{ secrets.CARGO_REGISTRY_TOKEN }}
        run: |
          set -e
          echo "published=false" >> $GITHUB_OUTPUT
          echo "${{ secrets.CARGO_REGISTRY_TOKEN }}" | cargo login
          PACKAGE_NAME=$(toml get Cargo.toml package.name --raw)
          VERSION=${{ needs.setup.outputs.version }}
          if cargo publish --allow-dirty; then
            echo "published=true" >> $GITHUB_OUTPUT
            echo "🎉🎉🎉 PUBLISH SUCCESSFUL 🎉🎉🎉"
            echo "✅ Successfully published $PACKAGE_NAME v$VERSION to crates.io"
            echo "📦 Crates.io: [https://crates.io/crates/$PACKAGE_NAME/$VERSION](https://crates.io/crates/$PACKAGE_NAME/$VERSION)"
            echo "📚 Docs.rs: [https://docs.rs/$PACKAGE_NAME/$VERSION](https://docs.rs/$PACKAGE_NAME/$VERSION)"
          else
            echo "❌ Publish failed"
          fi

  release:
    needs: [setup, check, tests, clippy, build]
    permissions:
      contents: write
      packages: write
    if: needs.setup.outputs.tag != ''
    runs-on: ubuntu-latest
    outputs:
      released: ${{ steps.release.outputs.released }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Get package name
        id: package_info
        run: |
          echo "package_name=${{ needs.setup.outputs.package_name }}" >> $GITHUB_OUTPUT
      - name: Check tag status
        id: check_tag
        run: |
          if git tag -l | grep -q "^${{ needs.setup.outputs.tag }}$"; then
            echo "tag_exists=true" >> $GITHUB_OUTPUT
            echo "🏷️ Tag ${{ needs.setup.outputs.tag }} exists locally"
          else
            echo "tag_exists=false" >> $GITHUB_OUTPUT
            echo "🏷️ Tag ${{ needs.setup.outputs.tag }} does not exist locally"
          fi
          if git ls-remote --tags origin | grep -q "refs/tags/${{ needs.setup.outputs.tag }}$"; then
            echo "remote_tag_exists=true" >> $GITHUB_OUTPUT
            echo "🌐 Tag ${{ needs.setup.outputs.tag }} exists on remote"
          else
            echo "remote_tag_exists=false" >> $GITHUB_OUTPUT
            echo "🌐 Tag ${{ needs.setup.outputs.tag }} does not exist on remote"
          fi
      - name: Check release status
        id: check_release
        run: |
          if gh release view "${{ needs.setup.outputs.tag }}" > /dev/null 2>&1; then
            echo "release_exists=true" >> $GITHUB_OUTPUT
            echo "📦 Release ${{ needs.setup.outputs.tag }} already exists"
          else
            echo "release_exists=false" >> $GITHUB_OUTPUT
            echo "📦 Release ${{ needs.setup.outputs.tag }} does not exist"
          fi
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - name: Create or update release
        id: release
        run: |
          set -e
          echo "released=false" >> $GITHUB_OUTPUT
          PACKAGE_NAME="${{ steps.package_info.outputs.package_name }}"
          VERSION="${{ needs.setup.outputs.version }}"
          TAG="${{ needs.setup.outputs.tag }}"
          echo "📦 Building source archives..."
          git archive --format=zip --prefix="${PACKAGE_NAME}-${VERSION}/" HEAD > "${PACKAGE_NAME}-${VERSION}.zip"
          git archive --format=tar.gz --prefix="${PACKAGE_NAME}-${VERSION}/" HEAD > "${PACKAGE_NAME}-${VERSION}.tar.gz"
          if [ "${{ steps.check_release.outputs.release_exists }}" = "true" ]; then
            echo "🔄 Updating existing release: $TAG"
            gh release view "$TAG" --json assets --jq '.assets[].name' | while read asset; do
              if [ -n "$asset" ]; then
                echo "🗑️ Deleting asset: $asset"
                gh release delete-asset "$TAG" "$asset" --yes || true
              fi
            done
            if gh release edit "$TAG" \
              --title "$TAG (Updated $(date '+%Y-%m-%d %H:%M:%S'))" \
              --notes "Release $TAG - Updated at $(date '+%Y-%m-%d %H:%M:%S UTC')
            ## Changes
            - Version: $VERSION
            - Package: $PACKAGE_NAME
            ## Links
            📦 [Crate on crates.io](https://crates.io/crates/$PACKAGE_NAME/$VERSION)
            📚 [Documentation on docs.rs](https://docs.rs/$PACKAGE_NAME/$VERSION)
            📋 [Commit History](https://github.com/${{ github.repository }}/commits/$TAG)" && \
               gh release upload "$TAG" "${PACKAGE_NAME}-${VERSION}.zip" "${PACKAGE_NAME}-${VERSION}.tar.gz" --clobber; then
              echo "released=true" >> $GITHUB_OUTPUT
              echo "✅ Updated release $TAG"
              echo "🔖 Tag: $TAG"
              echo "🚀 Release: [GitHub Release](${{ github.server_url }}/${{ github.repository }}/releases/tag/$TAG)"
            else
              echo "❌ Failed to update release"
            fi
          else
            if [ "${{ steps.check_tag.outputs.remote_tag_exists }}" = "false" ]; then
              echo "🏷️ Creating and pushing tag: $TAG"
              git tag "$TAG"
              git push origin "$TAG"
            fi
            echo "🆕 Creating new release: $TAG"
            if gh release create "$TAG" \
              --title "$TAG (Created $(date '+%Y-%m-%d %H:%M:%S'))" \
              --notes "Release $TAG - Created at $(date '+%Y-%m-%d %H:%M:%S UTC')
            ## Changes
            - Version: $VERSION
            - Package: $PACKAGE_NAME
            ## Links
            📦 [Crate on crates.io](https://crates.io/crates/$PACKAGE_NAME/$VERSION)
            📚 [Documentation on docs.rs](https://docs.rs/$PACKAGE_NAME/$VERSION)
            📋 [Commit History](https://github.com/${{ github.repository }}/commits/$TAG)" \
              --latest && \
               gh release upload "$TAG" "${PACKAGE_NAME}-${VERSION}.zip" "${PACKAGE_NAME}-${VERSION}.tar.gz"; then
              echo "released=true" >> $GITHUB_OUTPUT
              echo "✅ Created release $TAG"
              echo "🔖 Tag: $TAG"
              echo "🚀 Release: [GitHub Release](${{ github.server_url }}/${{ github.repository }}/releases/tag/$TAG)"
            else
              echo "❌ Failed to create release"
            fi
          fi
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

```

### 📄 File #685 - `lib.rs`
- **Path**: `hyperlane-utils\src\lib.rs`
- **Size**: `861 B`
- **Modified Time**: `2025-09-15T22:37:22.172645`

#### Content Preview

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
pub use futures;
pub use inventory;
pub use log;
pub use num_cpus;
pub use once_cell;
pub use serde;
pub use serde_json;
pub use serde_urlencoded;
pub use serde_xml_rs;
pub use simd_json;
pub use twox_hash;
pub use urlencoding;
pub use utoipa;
pub use utoipa_rapidoc;
pub use utoipa_swagger_ui;

```

### 📄 File #686 - `appreciate.md`
- **Path**: `ltpp-docs\src\appreciate.md`
- **Size**: `292 B`
- **Modified Time**: `2025-09-15T22:37:47.184462`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: 赞赏作者,赞赏,appreciate,作者
title: 赞赏作者
index: true
icon: blog
category:
  - 赞赏
  - appreciate
  - 作者
sidebar: false
---

<Share colorful />

<Appreciate />

<CratesDownloads />

<GitHubMetrics />

<Bottom />

```

### 📄 File #687 - `catalog.md`
- **Path**: `ltpp-docs\src\catalog.md`
- **Size**: `294 B`
- **Modified Time**: `2025-09-15T22:37:47.185463`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: 文档目录,目录,Eastspire
title: 文档目录
index: true
icon: book
category:
  - 目录
  - 文档目录
  - Eastspire
sidebar: false
---

<Share colorful />

> [!tip]
>
> `Eastspire` 文档目录

<Catalog :level=2 />

<Bottom />

```

### 📄 File #688 - `README.md`
- **Path**: `ltpp-docs\src\README.md`
- **Size**: `3,848 B`
- **Modified Time**: `2025-09-15T22:37:47.184462`

#### Content Preview

```markdown
---
home: true
icon: home
head:
  - - meta
    - name: keywords
      content: 文档首页
title: 文档首页
heroText: Eastspire文档
tagline: 只要我们为人民的利益坚持好的，为人民的利益改正错的，我们这个队伍就一定会兴旺起来。
heroFullScreen: true
bgImage: /img/light-background.png
bgImageDark: /img/dark-background.png
heroAlt: ''
actions:
  - text: 立即开始
    link: /catalog
    icon: signs-post
    type: primary

  - text: 作者主页
    icon: star
    link: https://github.com/eastspire

  - text: 赞赏作者
    icon: sun
    link: /appreciate

  - text: 联系作者
    icon: user
    link: mailto:root@ltpp.vip

features:
  - title: ltpp
    details: ltpp在线开发平台
    icon: blog
    link: /ltpp/

  - title: ltpp-share
    details: ltpp公益资源分享
    icon: blog
    link: /ltpp-share/

  - title: color-output
    details: 输出库
    icon: blog
    link: /color-output/

  - title: hyperlane
    details: web后端框架
    icon: blog
    link: /hyperlane/

  - title: http-request
    details: http请求库
    icon: blog
    link: /http-request/

  - title: tcplane
    details: tcp后端框架
    icon: blog
    link: /tcplane/

  - title: tcp-request
    details: tcp请求库
    icon: blog
    link: /tcp-request/

  - title: udp
    details: udp后端框架
    icon: blog
    link: /udp/

  - title: udp-request
    details: udp请求库
    icon: blog
    link: /udp-request/

  - title: lombok-macros
    details: lombok属性宏
    icon: blog
    link: /lombok-macros/

  - title: std-macro-extensions
    details: 标准库宏扩展
    icon: blog
    link: /std-macro-extensions/

  - title: china-identification...
    details: 中国身份证号校验库
    icon: blog
    link: /china-identification-card/

  - title: compare-version
    details: 版本比较库
    icon: blog
    link: /compare-version/

  - title: bin-encode-decode
    details: 二进制编解码库
    icon: blog
    link: /bin-encode-decode/

  - title: http-compress
    details: http压缩解压库
    icon: blog
    link: /http-compress/

  - title: http-constant
    details: http常量库
    icon: blog
    link: /http-constant/

  - title: http-type
    details: http类型库
    icon: blog
    link: /http-type/

  - title: file-operation
    details: 文件操作库
    icon: blog
    link: /file-operation/

  - title: recoverable-spawn
    details: 可恢复线程
    icon: blog
    link: /recoverable-spawn/

  - title: recoverable-thread-pool
    details: 可恢复线程池
    icon: blog
    link: /recoverable-thread-pool/

  - title: clonelicious
    details: 克隆宏
    icon: blog
    link: /clonelicious/

  - title: future-fn
    details: 异步闭包移动宏
    icon: blog
    link: /future-fn/

  - title: server-manager
    details: 服务进程管理
    icon: blog
    link: /server-manager/

  - title: ltpp-rust-web-server
    details: ltpp-web服务器
    icon: blog
    link: /ltpp-rust-web-server/

  - title: cloud-file-storage
    details: 云端存储
    icon: blog
    link: /cloud-file-storage/

  - title: hyperlane-log
    details: hyperlane日志库
    icon: blog
    link: /hyperlane-log/

  - title: hyperlane-time
    details: hyperlane时间库
    icon: blog
    link: /hyperlane-time/

  - title: hyperlane-macros
    details: hyperlane宏
    icon: blog
    link: /hyperlane-macros/

  - title: hyperlane-broadcast
    details: Hyperlane广播库
    icon: blog
    link: /hyperlane-broadcast/

  - title: hyperlane-utils
    details: Hyperlane工具库
    icon: blog
    link: /hyperlane-utils/

  - title: hyperlane-plugin
    details: websocket插件
    icon: blog
    link: /hyperlane-plugin-websocket/

  - title: hot-restart
    details: 热重启
    icon: blog
    link: /hot-restart/
---

<Bottom />

```

### 📄 File #689 - `license.md`
- **Path**: `ltpp-docs\src\hyperlane\license.md`
- **Size**: `1,226 B`
- **Modified Time**: `2025-09-15T22:37:47.198100`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: License
title: License
icon: gears
category:
  - license
order: 9
---

<Share colorful />

MIT License

Copyright (c) 2024 尤雨东

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<Bottom />

```

### 📄 File #690 - `README.md`
- **Path**: `ltpp-docs\src\hyperlane\README.md`
- **Size**: `6,821 B`
- **Modified Time**: `2025-09-15T22:37:47.194975`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: Web后端框架,hyperlane,web,rust,hyperlane官网,hyperlane框架官网,hyperlane文档,hyperlane官方文档,hyperlane框架官方文档
title: Web后端框架
index: true
icon: fas fa-rocket
category:
  - hyperlane
  - web
  - rust
dir:
  order: 26
---

<Share colorful />

[GITHUB 地址](https://github.com/hyperlane-dev/hyperlane)

<center>

<img src="/img/hyperlane.png" alt="" height="160">

[![](https://img.shields.io/crates/v/hyperlane.svg)](https://crates.io/crates/hyperlane)
[![](https://img.shields.io/crates/d/hyperlane.svg)](https://img.shields.io/crates/d/hyperlane.svg)
[![](https://docs.rs/hyperlane/badge.svg)](https://docs.rs/hyperlane)
[![](https://github.com/hyperlane-dev/hyperlane/workflows/Rust/badge.svg)](https://github.com/hyperlane-dev/hyperlane/actions?query=workflow:Rust)
[![](https://img.shields.io/crates/l/hyperlane.svg)](./license)

</center>

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

## 许可证

此项目基于 MIT 许可证授权。详细信息请查看 [license](license) 文件。

## 贡献

欢迎贡献！请提交 issue 或创建 pull request。

## 联系方式

如有任何疑问，请联系作者：[root@ltpp.vip](mailto:root@ltpp.vip)。

<Bottom />

```

### 📄 File #691 - `config.md`
- **Path**: `ltpp-docs\src\hyperlane\config\config.md`
- **Size**: `3,725 B`
- **Modified Time**: `2025-09-15T22:37:47.194975`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: ServerConfig,hyperlane,web,rust,config,config_str,host,port,http_buffer,ws_buffer,linger,nodelay,ttl
title: 服务配置
index: true
icon: fas fa-cogs
category:
  - hyperlane
  - web
  - rust
  - config
  - ServerConfig
  - host
  - port
  - http_buffer
  - ws_buffer
  - linger
  - nodelay
  - ttl
  - config_str
  - config
order: 2
---

<Share colorful />

### 设置 `host`

> [!tip]
>
> `hyperlane` 框架绑定 `host` 方式如下：

```rust
let config: ServerConfig = ServerConfig::new().await;
config.host("0.0.0.0").await;
```

### 设置 `port`

> [!tip]
>
> `hyperlane` 框架绑定端口方式如下：

```rust
let config: ServerConfig = ServerConfig::new().await;
config.port(60000).await;
```

### 设置 `http_buffer`

> [!tip]
>
> `hyperlane` 框架设置 `HTTP` 缓冲区大小方式如下（不设置或者设置为 `0` 则默认是 `4096` 字节）：

```rust
let config: ServerConfig = ServerConfig::new().await;
config.http_buffer(4096).await;
```

### 设置 `ws_buffer`

> [!tip]
>
> `hyperlane` 框架设置 `websocket` 缓冲区大小方式如下：
> 不设置或者设置为 `0` 则默认是 `4096` 字节。

```rust
server.ws_buffer(4096).await;
```

### 设置 `linger`

> [!tip]
>
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

> [!tip]
>
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

> [!tip]
>
> `hyperlane` 框架支持配置 `ttl`，该选项基于 `Tokio` 的 `TcpStream::set_ttl`，用于控制 `IP_TTL` 选项，以设置传输数据包的生存时间（`Time To Live`），从而影响数据包在网络中的跳数限制。

```rust
let config: ServerConfig = ServerConfig::new().await;
config.ttl(128).await;
```

### 设置 `config_str`

> [!tip]
>
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

<Bottom />

```

### 📄 File #692 - `middleware.md`
- **Path**: `ltpp-docs\src\hyperlane\config\middleware.md`
- **Size**: `1,548 B`
- **Modified Time**: `2025-09-15T22:37:47.194975`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: 中间件,hyperlane,web,rust,config,middleware
title: 中间件
index: true
icon: fas fa-layer-group
category:
  - hyperlane
  - web
  - rust
  - config
  - middleware
order: 5
---

<Share colorful />

> [!tip]
>
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

<Bottom />

```

### 📄 File #693 - `panic-hook.md`
- **Path**: `ltpp-docs\src\hyperlane\config\panic-hook.md`
- **Size**: `822 B`
- **Modified Time**: `2025-09-15T22:37:47.195978`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: 恐慌钩子,clone,web,rust,config,panic-hook
title: 恐慌钩子
index: true
icon: fas fa-bug
category:
  - clone
  - web
  - rust
  - config
  - panic-hook
order: 4
---

<Share colorful />

> [!tip]
>
> `hyperlane` 框架内部会对 `panic` 进行捕获，用户可通过钩子进行设置（不设置，框架默认不处理），
> 需要注意的是，触发 `panic` 后在执行 `panic_hook` 之前，框架会重置 `aborted` 状态，
> 支持多次注册，触发 `panic` 会按照注册顺序进行执行，如果任何阶段设置了 `aborted`，则后续注册的 `panic_hook` 将不会执行。

```rust
server.panic_hook(|cxt: Context| {
    let error: Panic = ctx.get_panic().await.unwrap_or_default();
    // do something
}).await;
```

<Bottom />

```

### 📄 File #694 - `README.md`
- **Path**: `ltpp-docs\src\hyperlane\config\README.md`
- **Size**: `219 B`
- **Modified Time**: `2025-09-15T22:37:47.194975`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: 框架配置,hyperlane,web,rust,config
title: 框架配置
index: false
icon: fas fa-cogs
category:
  - hyperlane
  - web
  - rust
  - config
dir:
  order: 3
---

```

### 📄 File #695 - `route.md`
- **Path**: `ltpp-docs\src\hyperlane\config\route.md`
- **Size**: `736 B`
- **Modified Time**: `2025-09-15T22:37:47.195978`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: 路由,hyperlane,web,rust,config,route
title: 路由
index: true
icon: fas fa-route
category:
  - hyperlane
  - web
  - rust
  - config
  - route
order: 6
---

<Share colorful />

> [!tip]
>
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

<Bottom />

```

### 📄 File #696 - `runtime.md`
- **Path**: `ltpp-docs\src\hyperlane\config\runtime.md`
- **Size**: `902 B`
- **Modified Time**: `2025-09-15T22:37:47.195978`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: 运行时,hyperlane,web,rust,config,runtime
title: 运行时
index: true
icon: fas fa-running
category:
  - hyperlane
  - web
  - rust
  - config
  - runtime
order: 1
---

<Share colorful />

> [!tip]
>
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

<Bottom />

```

### 📄 File #697 - `server.md`
- **Path**: `ltpp-docs\src\hyperlane\config\server.md`
- **Size**: `1,162 B`
- **Modified Time**: `2025-09-15T22:37:47.195978`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: 创建 Server,hyperlane,web,rust,config,server
title: 创建 Server
index: true
icon: fas fa-server
category:
  - hyperlane
  - web
  - rust
  - config
  - server
order: 3
---

<Share colorful />

> [!tip]
>
> `hyperlane` 框架创建服务方式如下，需要调用 `run` 方法，服务才会正常运行。
>
> `ServerHook` 提供了等待框架运行完成和框架停止运行的 `hook`
>
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

<Bottom />

```

### 📄 File #698 - `async.md`
- **Path**: `ltpp-docs\src\hyperlane\help\async.md`
- **Size**: `418 B`
- **Modified Time**: `2025-09-15T22:37:47.195978`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: 异步,hyperlane,web,rust,help,install
title: 异步
index: true
icon: fas fa-bolt
category:
  - hyperlane
  - web
  - rust
  - help
  - install
order: 3
---

<Share colorful />

### 异步

> [!tip]
> 由于 `hyperlane` 框架本身涉及到锁的数据均采取 `tokio`中的读写锁实现，所以涉及到锁的方法调用均需要 `await`。

<Bottom />

```

### 📄 File #699 - `build.md`
- **Path**: `ltpp-docs\src\hyperlane\help\build.md`
- **Size**: `900 B`
- **Modified Time**: `2025-09-15T22:37:47.196978`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: 构建,hyperlane,web,rust,help,install
title: 构建
index: true
icon: fas fa-box-open
category:
  - hyperlane
  - web
  - rust
  - help
  - install
order: 4
---

<Share colorful />

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

<Bottom />

```

### 📄 File #700 - `explain.md`
- **Path**: `ltpp-docs\src\hyperlane\help\explain.md`
- **Size**: `686 B`
- **Modified Time**: `2025-09-15T22:37:47.196978`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: 说明,hyperlane,web,rust,help,explain
title: 说明
index: true
icon: fas fa-info-circle
category:
  - hyperlane
  - web
  - rust
  - help
  - explain
order: 1
---

<Share colorful />

### 框架说明

> [!tip]
>
> `hyperlane` 仅提供最核心的功能(路由、中间件、异常处理、请求处理等基础核心的功能)。其余功能支持全部复用 `crate.io` 生态，这意味着你可以在 `hyperlane` 里使用 `crate.io` 里的第三方库，在 `hyperlane` 里集成他们是非常容易的事情。

### 推荐阅读

> [!tip]
> 推荐阅读 [点击阅读](../../hyperlane-utils/README.md) 。

<Bottom />

```

### 📄 File #701 - `flamegraph.md`
- **Path**: `ltpp-docs\src\hyperlane\help\flamegraph.md`
- **Size**: `520 B`
- **Modified Time**: `2025-09-15T22:37:47.196978`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: 火焰图,hyperlane,web,rust,help,flamegraph
title: 火焰图
index: true
icon: fas fa-fire-alt
category:
  - hyperlane
  - web
  - rust
  - help
  - flamegraph
order: 5
---

<Share colorful />

> [!tip]
>
> `hyperlane` 框架使用 `flamegraph`，使用前提是需要有 `perf` 环境，生成火焰图步骤如下：

### 安装

```sh
cargo install flamegraph
```

### 使用

```sh
CARGO_PROFILE_RELEASE_DEBUG=true cargo flamegraph --release
```

<Bottom />

```

### 📄 File #702 - `install.md`
- **Path**: `ltpp-docs\src\hyperlane\help\install.md`
- **Size**: `440 B`
- **Modified Time**: `2025-09-15T22:37:47.197598`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: 安装,hyperlane,web,rust,help,install
title: 安装
index: true
icon: fas fa-download
category:
  - hyperlane
  - web
  - rust
  - help
  - install
order: 2
---

<Share colorful />

### 安装

> [!tip]
>
> 如果不使用 `Cargo.lock` 提交到 `git`，请在 `Cargo.toml` 文件的版本号前加 `=` 来锁定版本。

#### 命令

```shell
cargo add hyperlane;
```

<Bottom />

```

### 📄 File #703 - `README.md`
- **Path**: `ltpp-docs\src\hyperlane\help\README.md`
- **Size**: `229 B`
- **Modified Time**: `2025-09-15T22:37:47.195978`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: 帮助,hyperlane,web,rust,help
title: 帮助
index: false
icon: fas fa-question-circle
category:
  - hyperlane
  - web
  - rust
  - help
expanded: true
dir:
  order: 7
---

```

### 📄 File #704 - `plaintext_flamegraph.svg`
- **Path**: `ltpp-docs\src\hyperlane\markdown-images\plaintext_flamegraph.svg`
- **Size**: `519,722 B`
- **Modified Time**: `2025-09-15T22:37:47.199103`

#### Content Preview



### 📄 File #705 - `auth.md`
- **Path**: `ltpp-docs\src\hyperlane\middleware\auth.md`
- **Size**: `1,392 B`
- **Modified Time**: `2025-09-15T22:37:47.199103`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content:
title: 身份校验中间件
index: true
icon: fas fa-user-shield
category:
  - hyperlane
  - web
  - rust
  - middleware
  - auth
order: 3
---

<Share colorful />

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

<Bottom />

```

### 📄 File #706 - `cross.md`
- **Path**: `ltpp-docs\src\hyperlane\middleware\cross.md`
- **Size**: `1,156 B`
- **Modified Time**: `2025-09-15T22:37:47.199103`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content:
title: 跨域中间件
index: true
icon: fas fa-exchange-alt
category:
  - hyperlane
  - web
  - rust
  - middleware
  - multi-server
order: 1
---

<Share colorful />

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

<Bottom />

```

### 📄 File #707 - `README.md`
- **Path**: `ltpp-docs\src\hyperlane\middleware\README.md`
- **Size**: `228 B`
- **Modified Time**: `2025-09-15T22:37:47.199103`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: 中间件,hyperlane,web,rust,middleware
title: 中间件
index: false
icon: fas fa-layer-group
category:
  - hyperlane
  - web
  - rust
  - middleware
dir:
  order: 4
---

```

### 📄 File #708 - `static-file.md`
- **Path**: `ltpp-docs\src\hyperlane\middleware\static-file.md`
- **Size**: `1,966 B`
- **Modified Time**: `2025-09-15T22:37:47.199103`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content:
title: 静态资源中间件
index: true
icon: fas fa-file
category:
  - hyperlane
  - web
  - rust
  - middleware
  - static-file
order: 4
---

<Share colorful />

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

<Bottom />

```

### 📄 File #709 - `timeout.md`
- **Path**: `ltpp-docs\src\hyperlane\middleware\timeout.md`
- **Size**: `1,554 B`
- **Modified Time**: `2025-09-15T22:37:47.200103`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content:
title: 超时中间件
index: true
icon: fas fa-stopwatch
category:
  - hyperlane
  - web
  - rust
  - middleware
  - timeout
order: 2
---

<Share colorful />

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

<Bottom />

```

### 📄 File #710 - `directory.md`
- **Path**: `ltpp-docs\src\hyperlane\quick-start\directory.md`
- **Size**: `9,126 B`
- **Modified Time**: `2025-09-15T22:37:47.200103`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content:
title: 目录结构
index: true
icon: fas fa-folder-open
category:
  - hyperlane
  - web
  - rust
  - quick-start
order: 1
---

<Share colorful />

> [!tip]
>
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

---

### `config`（配置目录）

- 被调用：

  - `init`：读取配置初始化。
  - `app`：全局配置使用，如数据库、缓存、超时等。

- 子目录说明：

  - `business`：业务层配置，如风控策略、规则开关。
  - `hyperlane`：服务监听、路由、中间件配置。
  - `server_manager`：进程托管策略。

### `init`（初始化目录）

- 调用：

  - `config`：读取配置。
  - `plugin`：初始化日志、服务等插件。
  - `app`：初始化 controller/service 等组件。

- 被调用：

  - 由主程序启动时触发。

### `plugin`（插件目录）

- 被调用：

  - `controller` / `service` / `init` 均可能调用。

- 子模块：

  - `log`：日志记录、链路追踪。
  - `server_manager`：守护进程、PID 控制等。

---

### `resources`（资源目录）

- 子目录说明：

  - `static/html`、`img`：被 `view` 层或浏览器直接访问。
  - `templates/html`：被 `controller` 或 `view` 用于渲染页面。

<Bottom />

```

### 📄 File #711 - `README.md`
- **Path**: `ltpp-docs\src\hyperlane\quick-start\README.md`
- **Size**: `1,063 B`
- **Modified Time**: `2025-09-15T22:37:47.200103`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: 快速开始,hyperlane,web,rust,quick-start,quick,start
title: 快速开始
index: true
icon: fas fa-play-circle
category:
  - hyperlane
  - web
  - rust
  - quick-start
  - quick
  - start
dir:
  order: 1
---

<Share colorful />

## 快速开始

> [!tip]
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

> [!tip]
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

<Bottom />

```

### 📄 File #712 - `close-keep-alive.md`
- **Path**: `ltpp-docs\src\hyperlane\speed\close-keep-alive.md`
- **Size**: `10,868 B`
- **Modified Time**: `2025-09-15T22:37:47.201103`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content:
title: 关闭Keep Alive
index: true
icon: fas fa-toggle-off
category:
  - hyperlane
  - web
  - rust
  - speed
  - close-keep-alive
order: 3
---

<Share colorful />

[GITHUB 地址](https://github.com/hyperlane-dev/web-server-pressure-measurement/tree/master/close-keep-alive)

### wrk

#### 压测命令

```sh
wrk -c360 -d60s -H "Connection: close" http://127.0.0.1:60000/
```

#### 压测结果

> [!tip]
> 测试 `360` 并发，持续 `60s` 请求。`QPS` 结果如下：
>
> - 1 `Hyperlane框架` ：51031.27
> - 2 `Tokio` ：49555.87
> - 3 `Rocket框架` ：49345.76
> - 4 `Gin框架` ：40149.75
> - 5 `Go标准库` ：38364.06
> - 6 `Rust标准库` ：30142.55
> - 7 `Node标准库` ：28286.96

#### hyperlane 框架

```sh
Running 1m test @ http://127.0.0.1:60000/
  2 threads and 360 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     3.51ms    2.12ms 254.29ms   74.68%
    Req/Sec    25.69k     1.78k   42.56k    74.94%
  3066756 requests in 1.00m, 298.32MB read
Requests/sec:  51031.27
Transfer/sec:      4.96MB
```

#### Rust 标准库

```sh
Running 1m test @ http://127.0.0.1:60000/
  2 threads and 360 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    13.39ms   39.09ms 938.33ms   93.24%
    Req/Sec    15.17k     1.25k   19.88k    71.08%
  1811006 requests in 1.00m, 151.99MB read
Requests/sec:  30142.55
Transfer/sec:      2.53MB
```

#### Tokio 框架

```sh
Running 1m test @ http://127.0.0.1:60000/
  2 threads and 360 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     3.64ms    2.97ms 331.60ms   89.67%
    Req/Sec    24.93k     2.37k   31.57k    64.49%
  2976845 requests in 1.00m, 249.83MB read
Requests/sec:  49555.87
Transfer/sec:      4.16MB
```

#### Rocket 框架

```sh
Running 1m test @ http://127.0.0.1:60000/
  2 threads and 360 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     3.70ms    3.23ms 246.75ms   92.68%
    Req/Sec    24.83k     2.31k   47.87k    71.72%
  2963056 requests in 1.00m, 729.05MB read
Requests/sec:  49345.76
Transfer/sec:     12.14MB
```

#### Gin 框架

```sh
Running 1m test @ http://127.0.0.1:60000/
  2 threads and 360 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     4.69ms    2.66ms  37.49ms   68.89%
    Req/Sec    20.22k     3.79k   28.13k    59.02%
  2412349 requests in 1.00m, 322.08MB read
Requests/sec:  40149.75
Transfer/sec:      5.36MB
```

#### Go 标准库

```sh
Running 1m test @ http://127.0.0.1:60000/
  2 threads and 360 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     4.96ms    3.17ms 248.63ms   75.61%
    Req/Sec    19.33k     4.01k   28.20k    59.12%
  2303964 requests in 1.00m, 307.61MB read
Requests/sec:  38364.06
Transfer/sec:      5.12MB
```

#### Node 标准库

```sh
Running 1m test @ http://127.0.0.1:60000/
  2 threads and 360 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     4.76ms    3.48ms  55.44ms   68.85%
    Req/Sec    14.22k     2.88k   28.04k    83.54%
  1699058 requests in 1.00m, 233.33MB read
  Socket errors: connect 337, read 0, write 0, timeout 0
Requests/sec:  28286.96
Transfer/sec:      3.88MB
```

### ab

#### 压测命令

```sh
ab -n 1000000 -c 1000 -r http://127.0.0.1:60000/
```

#### 压测结果

> [!tip]
> 测试 `1000` 并发，一共 `100w` 请求。`QPS` 结果如下：
>
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

<Bottom />

```

### 📄 File #713 - `env.md`
- **Path**: `ltpp-docs\src\hyperlane\speed\env.md`
- **Size**: `2,058 B`
- **Modified Time**: `2025-09-15T22:37:47.201103`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content:
title: 环境信息
index: true
icon: fas fa-server
category:
  - hyperlane
  - web
  - rust
  - speed
order: 1
---

<Share colorful />

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

<Bottom />

```

### 📄 File #714 - `flamegraph.md`
- **Path**: `ltpp-docs\src\hyperlane\speed\flamegraph.md`
- **Size**: `271 B`
- **Modified Time**: `2025-09-15T22:37:47.201606`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content:
title: 火焰图
index: true
icon: fas fa-fire-alt
category:
  - hyperlane
  - web
  - rust
  - speed
  - flamegraph
order: 5
---

<Share colorful />

## plaintext

![](../markdown-images/plaintext_flamegraph.svg)

```

### 📄 File #715 - `open-keep-alive.md`
- **Path**: `ltpp-docs\src\hyperlane\speed\open-keep-alive.md`
- **Size**: `11,086 B`
- **Modified Time**: `2025-09-15T22:37:47.201606`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content:
title: 开启Keep Alive
index: true
icon: fas fa-toggle-on
category:
  - hyperlane
  - web
  - rust
  - speed
  - open-keep-alive
order: 4
---

<Share colorful />

[GITHUB 地址](https://github.com/hyperlane-dev/web-server-pressure-measurement/tree/master/open-keep-alive)

### wrk

#### 压测命令

```sh
wrk -c360 -d60s http://127.0.0.1:60000/
```

#### 压测结果

> [!tip]
> 测试 `360` 并发，持续 `60s` 请求。`QPS` 结果如下：
>
> - 1 `Tokio` ：340130.92
> - 2 `Hyperlane框架` ：324323.71
> - 3 `Rocket框架` ：298945.31
> - 4 `Rust标准库` ：291218.96
> - 5 `Gin框架` ：242570.16
> - 6 `Go标准库` ：234178.93
> - 7 `Node标准库` ：139412.13

#### hyperlane 框架

```sh
Running 1m test @ http://127.0.0.1:60000/
  2 threads and 360 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     1.46ms    7.74ms 230.59ms   99.57%
    Req/Sec   163.12k     9.54k  187.65k    67.75%
  19476349 requests in 1.00m, 1.94GB read
Requests/sec: 324323.71
Transfer/sec:     33.10MB
```

#### Rust 标准库

```sh
Running 1m test @ http://127.0.0.1:60000/
  2 threads and 360 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     1.64ms    8.62ms 238.68ms   99.48%
    Req/Sec   146.49k    20.42k  190.38k    61.42%
  17494266 requests in 1.00m, 1.52GB read
Requests/sec: 291218.96
Transfer/sec:     25.83MB
```

#### Tokio 框架

```sh
Running 1m test @ http://127.0.0.1:60000/
  2 threads and 360 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     1.22ms    5.96ms 230.76ms   99.76%
    Req/Sec   171.05k     7.56k  192.19k    70.08%
  20423683 requests in 1.00m, 1.77GB read
Requests/sec: 340130.92
Transfer/sec:     30.17MB
```

#### Rocket 框架

```sh
Running 1m test @ http://127.0.0.1:60000/
  2 threads and 360 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     1.42ms    6.67ms 228.04ms   99.67%
    Req/Sec   150.37k     7.48k  172.42k    70.08%
  17955815 requests in 1.00m, 4.00GB read
Requests/sec: 298945.31
Transfer/sec:     68.14MB
```

#### Gin 框架

```sh
Running 1m test @ http://127.0.0.1:60000/
  2 threads and 360 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     1.67ms    4.67ms 249.72ms   99.63%
    Req/Sec   122.08k     4.39k  133.88k    69.58%
  14577127 requests in 1.00m, 1.97GB read
Requests/sec: 242570.16
Transfer/sec:     33.54MB
```

#### Go 标准库

```sh
Running 1m test @ http://127.0.0.1:60000/
  2 threads and 360 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     1.58ms    1.15ms  32.24ms   78.06%
    Req/Sec   117.80k     4.43k  130.07k    70.67%
  14064777 requests in 1.00m, 1.90GB read
Requests/sec: 234178.93
Transfer/sec:     32.38MB
```

#### Node 标准库

```sh
Running 1m test @ http://127.0.0.1:60000/
  2 threads and 360 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     2.58ms  837.62us  45.39ms   89.66%
    Req/Sec    70.11k     2.79k   74.29k    98.33%
  8371733 requests in 1.00m, 1.16GB read
Requests/sec: 139412.13
Transfer/sec:     19.81MB
```

### ab

#### 压测命令

```sh
ab -n 1000000 -c 1000 -r -k http://127.0.0.1:60000/
```

#### 压测结果

> [!tip]
> 测试 `1000` 并发，一共 `100w` 请求。`QPS` 结果如下：
>
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

<Bottom />

```

### 📄 File #716 - `README.md`
- **Path**: `ltpp-docs\src\hyperlane\speed\README.md`
- **Size**: `227 B`
- **Modified Time**: `2025-09-15T22:37:47.200103`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: 性能测试,hyperlane,web,rust,speed
title: 性能测试
index: false
icon: fas fa-tachometer-alt
category:
  - hyperlane
  - web
  - rust
  - speed
dir:
  order: 2
---

```

### 📄 File #717 - `request-time.md`
- **Path**: `ltpp-docs\src\hyperlane\speed\request-time.md`
- **Size**: `630 B`
- **Modified Time**: `2025-09-15T22:37:47.201606`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content:
title: 响应时间测试
index: true
icon: fas fa-stopwatch
category:
  - hyperlane
  - web
  - rust
  - speed
  - request
  - time
order: 2
---

<Share colorful />

[GITHUB 地址](https://github.com/hyperlane-dev/test-request)

> [!tip]
> 测试累计请求 `1w` 次

| 场景      | http-request 平均耗时 | hyper 平均耗时 |
| --------- | --------------------- | -------------- |
| TCP 失败  | 39us                  | 78us           |
| hyperlane | 100us                 | 150us          |
| 阿帕奇    | 300us                 | 2500us         |

<Bottom />

```

### 📄 File #718 - `addr.md`
- **Path**: `ltpp-docs\src\hyperlane\usage-introduction\addr.md`
- **Size**: `848 B`
- **Modified Time**: `2025-09-15T22:37:47.202154`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content:
title: 客户端地址
index: true
icon: fas fa-map-marker-alt
category:
  - hyperlane
  - web
  - rust
  - usage-introduction
  - file-extension
order: 5
---

<Share colorful />

> [!tip]
>
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

<Bottom />

```

### 📄 File #719 - `async.md`
- **Path**: `ltpp-docs\src\hyperlane\usage-introduction\async.md`
- **Size**: `1,862 B`
- **Modified Time**: `2025-09-15T22:37:47.202154`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content:
title: 异步运行时
index: true
icon: fas fa-bolt
category:
  - hyperlane
  - web
  - rust
  - usage-introduction
  - async
order: 1
---

<Share colorful />

> [!tip]
>
> `hyperlane` 框架在 `v3.0.0` 之前不对异步做任何处理，如果需要异步操作，可以引入第三方库
>
> `hyperlane` 框架在 `v3.0.0` 之后内置异步机制

> [!tip]
>
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

<Bottom />

```

### 📄 File #720 - `attribute.md`
- **Path**: `ltpp-docs\src\hyperlane\usage-introduction\attribute.md`
- **Size**: `1,349 B`
- **Modified Time**: `2025-09-15T22:37:47.202154`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content:
title: 属性
index: true
icon: fas fa-tag
category:
  - hyperlane
  - web
  - rust
  - usage-introduction
  - attribute
order: 9
---

<Share colorful />

> [!tip]
>
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

> [!tip]
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

<Bottom />

```

### 📄 File #721 - `connection.md`
- **Path**: `ltpp-docs\src\hyperlane\usage-introduction\connection.md`
- **Size**: `1,467 B`
- **Modified Time**: `2025-09-15T22:37:47.202154`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content:
title: 连接管理
index: true
icon: fas fa-link
category:
  - hyperlane
  - web
  - rust
  - usage-introduction
  - connection
order: 12
---

<Share colorful />

> [!tip]
>
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

<Bottom />

```

### 📄 File #722 - `cookie.md`
- **Path**: `ltpp-docs\src\hyperlane\usage-introduction\cookie.md`
- **Size**: `2,890 B`
- **Modified Time**: `2025-09-15T22:37:47.202154`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content:
title: Cookie 操作
index: true
icon: fas fa-cookie-bite
category:
  - hyperlane
  - web
  - rust
  - usage-introduction
  - cookie
order: 13
---

<Share colorful />

> [!tip]
>
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

> [!tip]
>
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

<Bottom />

```

### 📄 File #723 - `multi-server.md`
- **Path**: `ltpp-docs\src\hyperlane\usage-introduction\multi-server.md`
- **Size**: `1,173 B`
- **Modified Time**: `2025-09-15T22:37:47.203158`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content:
title: 多服务
index: true
icon: fas fa-server
category:
  - hyperlane
  - web
  - rust
  - config
  - multi-server
order: 11
---

<Share colorful />

> [!tip]
>
> `hyperlane` 框架支持多服务模式，仅需创建多个 `server` 实例并进行监听即可

### 多服务

> [!tip]
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

```

### 📄 File #724 - `panic.md`
- **Path**: `ltpp-docs\src\hyperlane\usage-introduction\panic.md`
- **Size**: `1,203 B`
- **Modified Time**: `2025-09-15T22:37:47.203158`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content:
title: 恐慌
index: true
icon: fas fa-exclamation-triangle
category:
  - hyperlane
  - web
  - rust
  - usage-introduction
  - panic
order: 10
---

<Share colorful />

> [!tip]
>
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

<Bottom />

```

### 📄 File #725 - `README.md`
- **Path**: `ltpp-docs\src\hyperlane\usage-introduction\README.md`
- **Size**: `248 B`
- **Modified Time**: `2025-09-15T22:37:47.202154`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: 使用介绍,hyperlane,web,rust,usage-introduction
title: 使用介绍
index: false
icon: fas fa-book-open
category:
  - hyperlane
  - web
  - rust
  - usage-introduction
dir:
  order: 5
---

```

### 📄 File #726 - `request.md`
- **Path**: `ltpp-docs\src\hyperlane\usage-introduction\request.md`
- **Size**: `3,763 B`
- **Modified Time**: `2025-09-15T22:37:47.203158`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content:
title: 请求
index: true
icon: fas fa-arrow-alt-circle-down
category:
  - hyperlane
  - web
  - rust
  - usage-introduction
  - request
order: 5
---

<Share colorful />

> [!tip]
>
> `hyperlane` 框架对 `ctx` 额外封装了子字段的方法，可以直接调用大部分子字段的 `get` 和 `set` 方法名称。
> 例如：调用 `request` 上的 `get_method` 方法，
> 一般需要从 `ctx` 解出 `request`，再调用`request.get_method()`，
> 可以简化成直接调用 `ctx.get_request_method().await`。
>
> **调用规律**
>
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

> [!tip]
>
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

> [!tip]
> 将获得完整的原始结构体字符串结构。

```rust
ctx.get_request().await.to_string();
```

#### 通过 `get_string`

> [!tip]
> 将获得简化的结构体字符串结构。

```rust
ctx.get_request().await.get_string();
```

#### 通过 `ctx.get_request_string`

```rust
let request_string: String = ctx.get_request_string().await;
```

<Bottom />

```

### 📄 File #727 - `response.md`
- **Path**: `ltpp-docs\src\hyperlane\usage-introduction\response.md`
- **Size**: `4,895 B`
- **Modified Time**: `2025-09-15T22:37:47.203158`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content:
title: 响应
index: true
icon: fas fa-arrow-alt-circle-up
category:
  - hyperlane
  - web
  - rust
  - usage-introduction
  - response
order: 6
---

<Share colorful />

> [!tip]
>
> `hyperlane` 框架没有发送响应前通过 `ctx` 中 `get_response` 获取的只是响应的初始化实例，里面其实没有数据，
> 只有当用户发送响应时才会构建出完整 `http` 响应，此后再次 `get_response` 才能获取到响应内容。

> [!tip]
>
> `hyperlane` 框架对 `ctx` 额外封装了子字段的方法，可以直接调用大部分子字段的 `get` 和 `set` 方法名称，
> 例如：调用 `response` 上的 `get_status_code` 方法。
>
> **调用规律**
>
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
>
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

> [!tip]
>
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

> [!tip]
> 将获得完整的原始结构体字符串结构。

```rust
ctx.get_response().await.to_string();
```

#### 通过 `get_string`

> [!tip]
> 将获得简化的结构体字符串结构。

```rust
ctx.get_response().await.get_string();
```

#### 通过 `ctx.get_response_string`

```rust
let response_string: String = ctx.get_response_string().await;
```

<Bottom />

```

### 📄 File #728 - `route.md`
- **Path**: `ltpp-docs\src\hyperlane\usage-introduction\route.md`
- **Size**: `1,656 B`
- **Modified Time**: `2025-09-15T22:37:47.203158`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content:
title: 路由
index: true
icon: fas fa-route
category:
  - hyperlane
  - web
  - rust
  - usage-introduction
  - request
order: 4
---

<Share colorful />

## 静态路由

> [!tip]
>
> `hyperlane` 框架支持静态路由（如果重复注册相同的静态路由，框架会抛出异常，程序退出运行），使用方法如下：

### 注册

```rust
server.route("/test", |ctx: Context| {}).await;
```

## 动态路由

> [!tip]
>
> `hyperlane` 框架支持动态路由（如果重复注册相同模式的动态路由，框架会抛出异常，程序退出运行），具体使用方法如下：

### 注册

> [!tip]
> 动态路由使用 `{}` 包裹，有两种写法
>
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

<Bottom />

```

### 📄 File #729 - `send.md`
- **Path**: `ltpp-docs\src\hyperlane\usage-introduction\send.md`
- **Size**: `4,192 B`
- **Modified Time**: `2025-09-15T22:37:47.204158`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content:
title: 发送响应
index: true
icon: fas fa-paper-plane
category:
  - hyperlane
  - web
  - rust
  - usage-introduction
  - send
order: 14
---

<Share colorful />

> [!tip]
>
> `hyperlane` 框架提供了多种响应发送方法，支持完整 HTTP 响应发送、仅响应体发送，以及连接管理。
>
> - `send_with_data`: 发送完整响应并设置响应体。
> - `send_once_with_data`: 发送完整响应并立即关闭连接。
> - `send_body_with_data`: 仅发送响应体并保留连接。
> - `send_body_once_with_data`: 仅发送响应体并立即关闭连接。
>
> - `send_body_list_with_data`: 批量发送响应体，适用于 WebSocket 等场景。
> - `send_body_list_once_with_data`: 批量发送响应体并立即关闭连接。

## 发送完整 HTTP 响应

### send 方法

> [!tip]
> 发送完整的 HTTP 响应，发送后 TCP 连接保留。

```rust
let send_result: ResponseResult = ctx.send().await;
```

### send_once 方法

> [!tip]
> 发送完整的 HTTP 响应，发送后立即关闭 TCP 连接。

```rust
let send_result: ResponseResult = ctx.send_once().await;
```

## 发送响应体

### send_body 方法

> [!tip]
> 仅发送响应体内容，发送后 TCP 连接保留。适用于流式响应和 WebSocket。

```rust
let send_result: ResponseResult = ctx.send_body().await;
```

### send_once_body 方法

> [!tip]
> 仅发送响应体内容，发送后立即关闭 TCP 连接。

```rust
let send_result: ResponseResult = ctx.send_once_body().await;
```

## 发送带数据的响应

### send_with_data 方法

> [!tip]
> 发送完整的 HTTP 响应，并将提供的数据作为响应体，发送后 TCP 连接保留。

```rust
let send_result: ResponseResult = ctx.send_with_data("Hello, World!").await;
```

### send_once_with_data 方法

> [!tip]
> 发送完整的 HTTP 响应，并将提供的数据作为响应体，发送后立即关闭 TCP 连接。

```rust
let send_result: ResponseResult = ctx.send_once_with_data("Hello, World!").await;
```

### send_body_with_data 方法

> [!tip]
> 仅发送响应体内容，并将提供的数据作为响应体，发送后 TCP 连接保留。

```rust
let send_result: ResponseResult = ctx.send_body_with_data("chunk data").await;
```

### send_body_once_with_data 方法

> [!tip]
> 仅发送响应体内容，并将提供的数据作为响应体，发送后立即关闭 TCP 连接。

```rust
let send_result: ResponseResult = ctx.send_body_once_with_data("final chunk").await;
```

### send_body_list_with_data 方法

> [!tip]
> 批量发送多个响应体数据，适用于 WebSocket 桢列表等场景，发送后 TCP 连接保留。

```rust
let frame_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(&request_body);
ctx.send_body_list_with_data(&frame_list).await.unwrap();
```

### send_body_list_once_with_data 方法

> [!tip]
> 批量发送多个响应体数据，发送后立即关闭 TCP 连接。

```rust
let frame_list: Vec<ResponseBody> = WebSocketFrame::create_frame_list(&request_body);
ctx.send_body_list_once_with_data(&frame_list).await.unwrap();
```

## 刷新缓冲区

### flush 方法

> [!tip]
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

<Bottom />

```

### 📄 File #730 - `sse.md`
- **Path**: `ltpp-docs\src\hyperlane\usage-introduction\sse.md`
- **Size**: `2,773 B`
- **Modified Time**: `2025-09-15T22:37:47.204158`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content:
title: SSE
index: true
icon: fas fa-broadcast-tower
category:
  - hyperlane
  - web
  - rust
  - usage-introduction
  - sse
order: 7
---

<Share colorful />

[GITHUB 地址](https://github.com/hyperlane-dev/hyperlane-quick-start/tree/sse)

> [!tip]
>
> `hyperlane` 框架支持 `sse`，服务端主动推送，下面是每隔 `1s` 完成一次推送，并在 `10` 次后关闭连接。

> [!tip]
>
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

```

### 📄 File #731 - `stream.md`
- **Path**: `ltpp-docs\src\hyperlane\usage-introduction\stream.md`
- **Size**: `1,182 B`
- **Modified Time**: `2025-09-15T22:37:47.204158`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content:
title: 流
index: true
icon: fas fa-water
category:
  - hyperlane
  - web
  - rust
  - usage-introduction
  - stream
order: 2
---

<Share colorful />

> [!tip]
>
> `hyperlane` 框架接收请求和发送响应均依赖 `stream`，类型是 [`ArcRwLockStream`](../type/stream.md) 需要注意框架提供的 `stream` 仅可读，使用方式如下：

### 获取 `stream`

```rust
let stream_lock: ArcRwLockStream = ctx.get_stream().await.clone().unwrap();
```

### 获取客户端地址

> [!tip]
>
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

> [!tip]
> 此方法会关闭 `TCP` 连接，不会终止当前的生命周期（当前声明周期结束不会进入下一次生命周期循环，需要重新建立 `TCP` 连接），当前声明周期内的代码正常执行，但是不会再发送响应。

```rust
ctx.closed().await;
```

<Bottom />

```

### 📄 File #732 - `websocket.md`
- **Path**: `ltpp-docs\src\hyperlane\usage-introduction\websocket.md`
- **Size**: `1,809 B`
- **Modified Time**: `2025-09-15T22:37:47.204158`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content:
title: WebSocket
index: true
icon: fas fa-exchange-alt
category:
  - hyperlane
  - web
  - rust
  - usage-introduction
  - websocket
order: 8
---

<Share colorful />

> [!tip]
>
> `hyperlane` 框架支持 `websocket` 协议，服务端自动处理协议升级，支持请求中间件，路由处理，响应中间件。

### 服务端代码

> [!tip]
>
> `hyperlane` 框架发送 `websocket` 响应使用`send_body`，与 `sse` 相同。
> 由于 `websocket`协议基于`http`，所以可以像使用 `http` 一样处理请求，
> 但是需要注意响应数据需要通过，`WebSocketFrame::create_frame_list` 进行帧处理。
> 如果开发者尝试调用 `send` 会导致客户端处理错误，
> （服务端发送响应前需要处理成符合`websocket` 规范的响应，客户端才能正确解析）。所以对于 `websocket` 响应，
> 请统一使用 `send_body` 或者 `send_body_list_with_data` 方法。

#### 单点发送

> [!tip]
>
> 完整代码参考 [`发送响应`](./send.md) 里 **WebSocket 发送** 部分 。

#### 广播发送

> [!tip]
>
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

```

### 📄 File #733 - `inner-utils.md`
- **Path**: `ltpp-docs\src\hyperlane\utils\inner-utils.md`
- **Size**: `811 B`
- **Modified Time**: `2025-09-15T22:37:47.205161`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content:
title: 框架内置工具
index: true
icon: fas fa-tools
category:
  - hyperlane
  - web
  - rust
  - utils
  - internal-utils
order: 1
---

<Share colorful />

## http-constant

> [!tip]
>
> `hyperlane` 框架使用了 `http-constant` 库（框架已内置，无需额外安装和导入），
> 使用参考 [官方文档](../../http-constant/README.md)。

## http-compress

> [!tip]
>
> `hyperlane` 框架使用了 `http-compress` 库（框架已内置，无需额外安装和导入），
> 使用参考 [官方文档](../../http-compress/README.md)。

## http-type

> [!tip]
>
> `hyperlane` 框架使用了 `http-type` 库（框架已内置，无需额外安装和导入），
> 使用参考 [官方文档](../../http-type/README.md)。

<Bottom />

```

### 📄 File #734 - `README.md`
- **Path**: `ltpp-docs\src\hyperlane\utils\README.md`
- **Size**: `218 B`
- **Modified Time**: `2025-09-15T22:37:47.204158`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: 工具使用,hyperlane,web,rust,utils
title: 工具使用
index: false
icon: fas fa-tools
category:
  - hyperlane
  - web
  - rust
  - utils
dir:
  order: 6
---

```

### 📄 File #735 - `recommend-utils.md`
- **Path**: `ltpp-docs\src\hyperlane\utils\recommend-utils.md`
- **Size**: `6,599 B`
- **Modified Time**: `2025-09-15T22:37:47.205161`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content:
title: 推荐工具
index: true
icon: fas fa-thumbs-up
category:
  - hyperlane
  - web
  - rust
  - utils
  - recommend-utils
order: 2
---

<Share colorful />

## hyperlane-utils

> [!tip]
>
> `hyperlane` 框架推荐使用 `hyperlane-utils` 库（需额外安装和导入），
> 使用参考 [官方文档](../../hyperlane-utils/README.md)。

## lombok

> [!tip]
>
> `hyperlane` 框架推荐使用 `lombok` 库（需额外安装和导入），
> 使用参考 [官方文档](../../lombok-macros/README.md)。

## clonelicious

> [!tip]
>
> `hyperlane` 框架推荐使用 `clonelicious` 库，内部提供变量捕获和克隆（需额外安装和导入），
> 使用参考 [官方文档](../../clonelicious/README.md)。

## future-fn

> [!tip]
>
> `hyperlane` 框架推荐使用 `future-fn` 库（需额外安装和导入），
> 使用参考 [官方文档](../../future-fn/README.md)。

## std-macro-extensions

> [!tip]
>
> `hyperlane` 框架推荐使用 `std-macro-extensions` 库（需额外安装和导入），
> 使用参考 [官方文档](../../std-macro-extensions/README.md)。

## color-output

> [!tip]
>
> `hyperlane` 框架推荐使用 `color-output` 库（需额外安装和导入），
> 使用参考 [官方文档](../../color-output/README.md)。

## bin-encode-decode

> [!tip]
>
> `hyperlane` 框架推荐使用 `bin-encode-decode` 库（需额外安装和导入），
> 使用参考 [官方文档](../../bin-encode-decode/README.md)。

## file-operation

> [!tip]
>
> `hyperlane` 框架推荐使用 `file-operation` 库（需额外安装和导入），
> 使用参考 [官方文档](../../file-operation/README.md)。

## compare-version

> [!tip]
>
> `hyperlane` 框架推荐使用 `compare-version` 库（需额外安装和导入），
> 使用参考 [官方文档](../../compare-version/README.md)。

## hyperlane-log

> [!tip]
>
> `hyperlane` 框架使用 `hyperlane-log` 库（需额外安装和导入），
> 使用参考 [官方文档](../../hyperlane-log/README.md)。

## hyperlane-time

> [!tip]
>
> `hyperlane` 框架推荐使用 `hyperlane-time` 库（需额外安装和导入），
> 使用参考 [官方文档](../../hyperlane-time/README.md)。

## recoverable-spawn

> [!tip]
>
> `hyperlane` 框架推荐使用 `recoverable-spawn` 库（需额外安装和导入），
> 使用参考 [官方文档](../../recoverable-spawn/README.md)。

## recoverable-thread-pool

> [!tip]
>
> `hyperlane` 框架推荐使用 `recoverable-thread-pool` 库（需额外安装和导入），
> 使用参考 [官方文档](../../recoverable-thread-pool/README.md)。

## http-request

> [!tip]
>
> `hyperlane` 框架推荐使用 `http-request` 库，支持 `http` 和 `https`（需额外安装和导入），
> 使用参考 [官方文档](../../http-request/README.md)。

## hyperlane-broadcast

> [!tip]
>
> `hyperlane` 框架推荐使用 `hyperlane-broadcast` 库（需额外安装和导入），
> 使用参考 [官方文档](../../hyperlane-broadcast/README.md)。

## hyperlane-plugin-websocket

> [!tip]
>
> `hyperlane` 框架推荐使用 `hyperlane-plugin-websocket` 库（需额外安装和导入），
> 使用参考 [官方文档](../../hyperlane-plugin-websocket/README.md)。

## urlencoding

> [!tip]
>
> `hyperlane` 框架推荐使用 `urlencoding` 库（需额外安装和导入），可以实现 `url` 编解码。

## server-manager

> [!tip]
>
> `hyperlane` 框架推荐使用 `server-manager` 库（需额外安装和导入），
> 使用参考 [官方文档](../../server-manager/README.md)。

## chunkify

> [!tip]
>
> `hyperlane` 框架推荐使用 `chunkify` 库（需额外安装和导入），
> 使用参考 [官方文档](../../chunkify/README.md)。

## china_identification_card

> [!tip]
>
> `hyperlane` 框架推荐使用 `china_identification_card` 库（需额外安装和导入），
> 使用参考 [官方文档](../../china-identification-card/README.md)。

## utoipa

> [!tip]
>
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

<Bottom />

```

### 📄 File #736 - `license.md`
- **Path**: `ltpp-docs\src\hyperlane-ai\license.md`
- **Size**: `1,225 B`
- **Modified Time**: `2025-09-15T22:37:47.191474`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: License,LICENSE
title: License
icon: gears
category:
  - LICENSE
---

<Share colorful />

MIT License

Copyright (c) 2024 尤雨东

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<Bottom />

```

### 📄 File #737 - `README.md`
- **Path**: `ltpp-docs\src\hyperlane-ai\README.md`
- **Size**: `2,725 B`
- **Modified Time**: `2025-09-15T22:37:47.191474`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: Hyperlane AI,hyperlane-ai
title: Hyperlane大模型
index: true
icon: fas fa-tools
category:
  - hyperlane-ai
dir:
  order: 49
---

<Share colorful />

[GITHUB 地址](https://github.com/hyperlane-dev/hyperlane-ai)

<center>

[![](https://img.shields.io/crates/l/hyperlane_utils.svg)](./LICENSE)

</center>

本项目提供了一个完整的流水线，用于微调语言模型并将其转换为 GGUF 格式以实现高效推理。

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

## 许可证

本项目采用 MIT 许可证进行授权。详情请参阅 [LICENSE](LICENSE) 文件。

## 贡献指南

欢迎贡献！如有问题请提交 Issue 或发起 Pull Request。

## 联系方式

如有任何疑问，请通过邮箱 [root@ltpp.vip](mailto:root@ltpp.vip) 联系作者。

<Bottom />

```

### 📄 File #738 - `license.md`
- **Path**: `ltpp-docs\src\hyperlane-broadcast\license.md`
- **Size**: `1,225 B`
- **Modified Time**: `2025-09-15T22:37:47.192474`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: License,LICENSE
title: License
icon: gears
category:
  - LICENSE
---

<Share colorful />

MIT License

Copyright (c) 2024 尤雨东

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<Bottom />

```

### 📄 File #739 - `README.md`
- **Path**: `ltpp-docs\src\hyperlane-broadcast\README.md`
- **Size**: `2,576 B`
- **Modified Time**: `2025-09-15T22:37:47.192474`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: Hyperlane广播库,hyperlane-broadcast
title: Hyperlane广播库
index: true
icon: fas fa-broadcast-tower
category:
  - hyperlane-broadcast
dir:
  order: 44
---

<Share colorful />

[GITHUB 地址](https://github.com/hyperlane-dev/hyperlane-broadcast)

<center>

[![](https://img.shields.io/crates/v/hyperlane-broadcast.svg)](https://crates.io/crates/hyperlane-broadcast)
[![](https://img.shields.io/crates/d/hyperlane-broadcast.svg)](https://img.shields.io/crates/d/hyperlane-broadcast.svg)
[![](https://docs.rs/hyperlane-broadcast/badge.svg)](https://docs.rs/hyperlane-broadcast)
[![](https://github.com/hyperlane-dev/hyperlane-broadcast/workflows/Rust/badge.svg)](https://github.com/hyperlane-dev/hyperlane-broadcast/actions?query=workflow:Rust)
[![](https://img.shields.io/crates/l/hyperlane_broadcast.svg)](./LICENSE)

</center>

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

本项目采用 [MIT 许可证](LICENSE)。

## 贡献指南

我们欢迎任何形式的贡献！如有建议或想法，请通过 issue 或 pull request 提交。

## 联系方式

如有任何问题，欢迎联系作者：[root@ltpp.vip](mailto:root@ltpp.vip)。

<Bottom />

```

### 📄 File #740 - `license.md`
- **Path**: `ltpp-docs\src\hyperlane-log\license.md`
- **Size**: `1,225 B`
- **Modified Time**: `2025-09-15T22:37:47.192474`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: License,LICENSE
title: License
icon: gears
category:
  - LICENSE
---

<Share colorful />

MIT License

Copyright (c) 2024 尤雨东

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<Bottom />

```

### 📄 File #741 - `README.md`
- **Path**: `ltpp-docs\src\hyperlane-log\README.md`
- **Size**: `4,112 B`
- **Modified Time**: `2025-09-15T22:37:47.192474`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: hyperlane日志库,hyperlane,log,rust
title: hyperlane日志库
index: true
icon: fas fa-file-alt
category:
  - hyperlane
  - log
  - rust
dir:
  order: 28
---

<Share colorful />

[GITHUB 地址](https://github.com/hyperlane-dev/hyperlane-log)

<center>

[![](https://img.shields.io/crates/v/hyperlane-log.svg)](https://crates.io/crates/hyperlane-log)
[![](https://img.shields.io/crates/d/hyperlane-log.svg)](https://img.shields.io/crates/d/hyperlane-log.svg)
[![](https://docs.rs/hyperlane-log/badge.svg)](https://docs.rs/hyperlane-log)
[![](https://github.com/hyperlane-dev/hyperlane-log/workflows/Rust/badge.svg)](https://github.com/hyperlane-dev/hyperlane-log/actions?query=workflow:Rust)
[![](https://img.shields.io/crates/l/hyperlane-log.svg)](./LICENSE)

</center>

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

## 许可证

该项目采用 MIT 许可证。详细信息请参阅 [LICENSE](LICENSE) 文件。

## 贡献

欢迎贡献！请提交问题或拉取请求。

## 联系方式

如有任何问题，请通过 [root@ltpp.vip](mailto:root@ltpp.vip) 联系作者。

<Bottom />

```

### 📄 File #742 - `license.md`
- **Path**: `ltpp-docs\src\hyperlane-macros\license.md`
- **Size**: `1,225 B`
- **Modified Time**: `2025-09-15T22:37:47.193474`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: License,LICENSE
title: License
icon: gears
category:
  - LICENSE
---

<Share colorful />

MIT License

Copyright (c) 2024 尤雨东

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<Bottom />

```

### 📄 File #743 - `README.md`
- **Path**: `ltpp-docs\src\hyperlane-macros\README.md`
- **Size**: `21,478 B`
- **Modified Time**: `2025-09-15T22:37:47.193474`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: hyperlane-macros,hyperlane-macros
title: hyperlane-macros
index: true
icon: fas fa-puzzle-piece
category:
  - hyperlane-macros
dir:
  order: 48
---

<Share colorful />

[GITHUB 地址](https://github.com/hyperlane-dev/hyperlane-macros)

<center>

[![](https://img.shields.io/crates/v/hyperlane-macros.svg)](https://crates.io/crates/hyperlane-macros)
[![](https://img.shields.io/crates/d/hyperlane-macros.svg)](https://img.shields.io/crates/d/hyperlane-macros.svg)
[![](https://docs.rs/hyperlane-macros/badge.svg)](https://docs.rs/hyperlane-macros)
[![](https://github.com/hyperlane-dev/hyperlane-macros/workflows/Rust/badge.svg)](https://github.com/hyperlane-dev/hyperlane-macros/actions?query=workflow:Rust)
[![](https://img.shields.io/crates/l/hyperlane-macros.svg)](./LICENSE)

</center>

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

## 许可证

该项目使用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 贡献

欢迎贡献！请提交问题或拉取请求。

## 联系方式

如有任何问题，请联系作者 [root@ltpp.vip](mailto:root@ltpp.vip)。

<Bottom />

```

### 📄 File #744 - `license.md`
- **Path**: `ltpp-docs\src\hyperlane-plugin-websocket\license.md`
- **Size**: `1,225 B`
- **Modified Time**: `2025-09-15T22:37:47.193474`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: License,LICENSE
title: License
icon: gears
category:
  - LICENSE
---

<Share colorful />

MIT License

Copyright (c) 2024 尤雨东

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<Bottom />

```

### 📄 File #745 - `README.md`
- **Path**: `ltpp-docs\src\hyperlane-plugin-websocket\README.md`
- **Size**: `6,326 B`
- **Modified Time**: `2025-09-15T22:37:47.193474`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: HyperlaneWebSocket插件,hyperlane-plugin-websocket
title: HyperlaneWebSocket插件
index: true
icon: fas fa-plug
category:
  - hyperlane-plugin-websocket
dir:
  order: 46
---

<Share colorful />

[GITHUB 地址](https://github.com/hyperlane-dev/hyperlane-plugin-websocket)

<center>

[![](https://img.shields.io/crates/v/hyperlane-plugin-websocket.svg)](https://crates.io/crates/hyperlane-plugin-websocket)
[![](https://img.shields.io/crates/d/hyperlane-plugin-websocket.svg)](https://img.shields.io/crates/d/hyperlane-plugin-websocket.svg)
[![](https://docs.rs/hyperlane-plugin-websocket/badge.svg)](https://docs.rs/hyperlane-plugin-websocket)
[![](https://github.com/hyperlane-dev/hyperlane-plugin-websocket/workflows/Rust/badge.svg)](https://github.com/hyperlane-dev/hyperlane-plugin-websocket/actions?query=workflow:Rust)
[![](https://img.shields.io/crates/l/hyperlane-plugin-websocket.svg)](./LICENSE)

</center>

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

## 许可证

本项目使用 MIT 协议，详情请参见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎贡献代码！请提交 issue 或 pull request。

## 联系方式

如有任何问题，请联系作者 [root@ltpp.vip](mailto:root@ltpp.vip)。

<Bottom />

```

### 📄 File #746 - `license.md`
- **Path**: `ltpp-docs\src\hyperlane-time\license.md`
- **Size**: `1,225 B`
- **Modified Time**: `2025-09-15T22:37:47.194473`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: License,LICENSE
title: License
icon: gears
category:
  - LICENSE
---

<Share colorful />

MIT License

Copyright (c) 2024 尤雨东

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<Bottom />

```

### 📄 File #747 - `README.md`
- **Path**: `ltpp-docs\src\hyperlane-time\README.md`
- **Size**: `2,261 B`
- **Modified Time**: `2025-09-15T22:37:47.193474`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: hyperlane时间库,hyperlane,time,rust
title: hyperlane时间库
index: true
icon: fas fa-clock
category:
  - hyperlane
  - time
  - rust
dir:
  order: 29
---

<Share colorful />

[GITHUB 地址](https://github.com/hyperlane-dev/hyperlane-time)

<center>

[![](https://img.shields.io/crates/v/hyperlane-time.svg)](https://crates.io/crates/hyperlane-time)
[![](https://img.shields.io/crates/d/hyperlane-time.svg)](https://img.shields.io/crates/d/hyperlane-time.svg)
[![](https://docs.rs/hyperlane-time/badge.svg)](https://docs.rs/hyperlane-time)  
[![](https://github.com/hyperlane-dev/hyperlane-time/workflows/Rust/badge.svg)](https://github.com/hyperlane-dev/hyperlane-time/actions?query=workflow:Rust)
[![](https://img.shields.io/crates/l/hyperlane-time.svg)](./LICENSE)

</center>

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

## 许可证

本项目使用 MIT 许可证。详情请见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎贡献！请提交问题或拉取请求。

## 联系

如有任何问题，请通过邮件联系作者 [root@ltpp.vip](mailto:root@ltpp.vip)。

<Bottom />

```

### 📄 File #748 - `license.md`
- **Path**: `ltpp-docs\src\hyperlane-utils\license.md`
- **Size**: `1,225 B`
- **Modified Time**: `2025-09-15T22:37:47.194975`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: License,LICENSE
title: License
icon: gears
category:
  - LICENSE
---

<Share colorful />

MIT License

Copyright (c) 2024 尤雨东

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<Bottom />

```

### 📄 File #749 - `README.md`
- **Path**: `ltpp-docs\src\hyperlane-utils\README.md`
- **Size**: `1,413 B`
- **Modified Time**: `2025-09-15T22:37:47.194473`

#### Content Preview

```markdown
---
head:
  - - meta
    - name: keywords
      content: Hyperlane工具库,hyperlane-utils
title: Hyperlane工具库
index: true
icon: fas fa-tools
category:
  - hyperlane-utils
dir:
  order: 45
---

<Share colorful />

[GITHUB 地址](https://github.com/hyperlane-dev/hyperlane-utils)

<center>

[![](https://img.shields.io/crates/v/hyperlane-utils.svg)](https://crates.io/crates/hyperlane-utils)
[![](https://img.shields.io/crates/d/hyperlane-utils.svg)](https://img.shields.io/crates/d/hyperlane-utils.svg)
[![](https://docs.rs/hyperlane-utils/badge.svg)](https://docs.rs/hyperlane-utils)
[![](https://github.com/hyperlane-dev/hyperlane-utils/workflows/Rust/badge.svg)](https://github.com/hyperlane-dev/hyperlane-utils/actions?query=workflow:Rust)
[![](https://img.shields.io/crates/l/hyperlane_utils.svg)](./LICENSE)

</center>

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

## 许可证

本项目采用 MIT 许可证进行授权。详情请参阅 [LICENSE](LICENSE) 文件。

## 贡献指南

欢迎贡献！如有问题请提交 Issue 或发起 Pull Request。

## 联系方式

如有任何疑问，请通过邮箱 [root@ltpp.vip](mailto:root@ltpp.vip) 联系作者。

<Bottom />

```

