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

__all__ = ["ARTICLE_META_AND_ABOUT_HTML", "ARTICLE_FAQ_HTML"]
