#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class BlogPost(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class BlogHome(Handler):
    def render_front(self):
        posts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT 5")
        self.render("main-blog.html", posts=posts)

    def get(self):
        self.render_front()

class NewPost(Handler):
    def render_front(self, title = "", body = "", error = ""):
        self.render("new-blog.html", title = title, body = body, error = error)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            a = BlogPost(title = title, body = body)
            a.put()
            id = a.key().id()
            self.redirect("/blog/%s" % str(a.key().id()))
        else:
            error = "We need both a title and a body!"
            self.render_front(title, body, error = error)

class ViewPostHandler(Handler):
    def get(self, id):
        id = int(id)
        post = BlogPost.get_by_id(id, parent = None)
        if post:
           self.render("post.html", post = post)
        else:
            error = "There is no post with that ID!"
            self.write(error)

class FrontPage(Handler):
    def get(self):
        self.redirect("/blog")

app = webapp2.WSGIApplication([
    ('/', FrontPage),
    ('/blog', BlogHome),
    ('/blog/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', handler = ViewPostHandler, name = 'post')
])
