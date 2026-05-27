from __future__ import annotations

ARTICLE_META_AND_ABOUT_HTML = """
<html>
  <body>
    <article class="article-shell article-shell--regression">
      <p class="et_pb_title_meta_container">
        by <span class="author vcard"><a href="https://example.com/author/example-author" rel="author">Example Author</a></span>
        | <span class="published">May 22, 2026</span>
        | <a href="https://example.com/blog/" rel="category tag">Blog</a>,
        <a href="https://example.com/threat-research/" rel="category tag">Threat Research</a>
      </p>
      <div class="article-shell__body">
        <p>Example paragraph one.</p>
        <p>Example paragraph two.</p>
      </div>
      <section class="et_pb_section et_pb_text_10">
        <h2><strong>About ExampleCorp</strong></h2>
        <p>ExampleCorp is a fictional company description that should not survive cleanup.</p>
        <div class="et_pb_button_module_wrapper">
          <a href="https://example.com/contact/">Contact us &gt;</a>
        </div>
        <p><a href="https://example.com/about/">About Us &gt;</a></p>
        <p><a href="https://example.com/blog/">Blog &gt;</a></p>
      </section>
    </article>
  </body>
</html>
"""

ARTICLE_FAQ_HTML = """
<html>
  <body>
    <article class="article-shell article-shell--faq">
      <div class="article-shell__body">
        <h2>Frequently Asked Questions</h2>
        <div class="dsm-faq-container">
          <div class="dsm-faq-item-wrapper dsm_faq_child_0">
            <div class="dsm-title-wrapper">
              <div class="dsm_open_icon"><span>K</span></div>
              <div class="dsm_close_icon"><span>L</span></div>
              <div class="dsm-faq-title">What is the example case?</div>
            </div>
            <div class="dsm-faq-answer">
              <p>The example case is a synthetic regression fixture.</p>
            </div>
          </div>
        </div>
        <p>Body content that should remain after cleanup.</p>
      </div>
    </article>
  </body>
</html>
"""

ARTICLE_PAID_ACCESS_HTML = """
<html>
  <body>
    <main class="main">
      <div class="container-fluid wrapper">
        <div class="row">
          <div class="col-xs-12">
            <header class="post-header">
              <a class="post-badge" href="/blog/">blog</a>
              <h1>Example Security Article</h1>
              <p>By Example Author</p>
            </header>
          </div>
          <div class="col-xs-12 col-lg-8 col-xl-9">
            <article class="post tag-example featured post-access-paid has-sidebar">
              <p>The first article paragraph stays in the body.</p>
              <p>The second article paragraph also stays in the body.</p>
              <div class="post-access-cta p-lg text-center paid">
                <h2>This post is for paid members only</h2>
                <p>Become a paid member for unlimited ad-free access to articles, bonus podcast content, and more.</p>
                <a href="/membership/">Subscribe</a>
                <a href="/signup/">Sign up for free access</a>
                <a href="/signin/">Sign in</a>
              </div>
            </article>
          </div>
          <aside class="col-xs-12 col-lg-4 col-xl-3 has-sidebar">
            <h2>More like this</h2>
            <a href="/related/one">Related one</a>
            <a href="/related/two">Related two</a>
          </aside>
        </div>
      </div>
    </main>
  </body>
</html>
"""

ARTICLE_HERO_SUBTITLE_HTML = """
<html>
  <body>
    <main>
      <section class="sandbox-intro">
        <div class="sandbox-intro__content">
          <div class="heading heading--sub heading--center heading--primary sandbox-intro__title-sub">Malware sandbox</div>
          <h1 class="heading heading--center sandbox-intro__title">Analyze malware and phishing in a safe environment</h1>
          <p class="paragraph paragraph--largest sandbox-intro__text">Easy to use. Configurable. Quick to deliver the verdict.</p>
          <div class="sandbox-intro__actions">
            <a href="https://example.test/get-started/">Get started</a>
            <a href="https://example.test/contact/">Contact sales</a>
          </div>
        </div>
      </section>
    </main>
  </body>
</html>
"""

ARTICLE_ARTICLE_CHROME_HTML = """
<html>
  <body>
    <a class="sr-only focus:not-sr-only" href="#main">Skip to content</a>
    <div id="app">
      <header id="site-header" class="banner">
        <div class="text-settings-dropdown-nav">
          Story text Size Small Standard Large Width Standard Wide Links Standard Orange Subscribers only Learn more Pin to story
        </div>
      </header>
      <main class="main" id="main">
        <article class="double-column h-entry post-2142564 post type-post status-publish format-standard has-post-thumbnail hentry category-information-technology category-features category-security tag-encryption tag-networking-2 tag-security tag-wi-fi">
          <h1>Example Security Article</h1>
          <p>Body paragraph one stays.</p>
          <p>Body paragraph two stays.</p>
        </article>
        <div class="comments-wrapper col-span-3 hidden py-5">Comments Forum view Loading comments...</div>
        <div class="single-most-read">Most Read 1. Item one 2. Item two 3. Item three</div>
        <div class="staff-picks-title font-impact xs:justify-center flex flex-row items-center gap-2 bg-gray-600 px-5 py-2 text-xl font-extrabold uppercase text-green-400 lg:text-2xl">
          <span>Staff Picks</span>
        </div>
        <div class="comments-picks-list">
          <article class="comment-pick">
            <p>Reader comment card content that should not survive cleanup.</p>
          </article>
        </div>
      </main>
    </div>
  </body>
</html>
"""

ARTICLE_HUBSPOT_ROW_WRAPPER_HTML = """
<html>
  <body>
    <div class="body-container-wrapper">
      <div class="body-container container-fluid">
        <div class="row-fluid-wrapper row-depth-1 row-number-1">
          <div class="row-fluid">
            <div class="span12 widget-span widget-type-custom_widget">
              <div class="article-content">
                <h1>Fragnesia (CVE-2026-46300) - Mitigation and Kernel Update</h1>
                <p>CloudLinux explains the mitigation and kernel update steps.</p>
                <p>Patched kernels and KernelCare livepatches are coming shortly.</p>
              </div>
            </div>
          </div>
        </div>
        <div class="row-fluid-wrapper row-depth-1 row-number-2">
          <div class="row-fluid">
            <div class="news-form" id="news-form">
              <a href="/subscribe/">Subscribe</a>
              <a href="/trial/">Get a Trial</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </body>
</html>
"""

ARTICLE_DIVI_ABOUT_AND_FAQ_HTML = """
<html>
  <body>
    <article class="et_pb_post">
      <div class="et_pb_section et_pb_section_0">
        <div class="et_pb_text_0">Blog</div>
      </div>
      <div class="et_pb_title_container">
        <p class="et_pb_title_meta_container">
          by | <span class="published">Mar 30, 2026</span> | <a href="/blog/" rel="category tag">Blog</a>, <a href="/dprk-it-worker-fraud/" rel="category tag">DPRK IT Worker Fraud Investigations &amp; Research</a>
        </p>
      </div>
      <div class="article-info">
        <div>Blog</div>
        <div class="info-date">Mar 30, 2026</div>
        <div class="info-author">Example Author</div>
        <ul class="tag-list">
          <li><a href="/tag/example">Example</a></li>
        </ul>
      </div>
      <div class="article-content">
        <h1>Example Interview Story</h1>
        <p>Real body content should remain.</p>
        <div class="dsm-faq-container">
          <div class="dsm_faq_child_0 dsm-faq-item-wrapper">
            <div class="dsm-title-wrapper">
              <div class="dsm_open_icon"><span>K</span></div>
              <div class="dsm_close_icon"><span>L</span></div>
              <h4 class="dsm-faq-title">What is the example case?</h4>
            </div>
            <div class="dsm-faq-content">The example answer should remain.</div>
          </div>
        </div>
        <section class="et_pb_text_10">
          <h2><strong>About ExampleCorp</strong></h2>
          <p>ExampleCorp is a fictional company description that should not survive cleanup.</p>
          <a href="/services/example/">Example Service</a>
        </section>
      </div>
    </article>
  </body>
</html>
"""

__all__ = [
    "ARTICLE_META_AND_ABOUT_HTML",
    "ARTICLE_FAQ_HTML",
    "ARTICLE_PAID_ACCESS_HTML",
    "ARTICLE_HERO_SUBTITLE_HTML",
    "ARTICLE_ARTICLE_CHROME_HTML",
    "ARTICLE_HUBSPOT_ROW_WRAPPER_HTML",
    "ARTICLE_DIVI_ABOUT_AND_FAQ_HTML",
]
