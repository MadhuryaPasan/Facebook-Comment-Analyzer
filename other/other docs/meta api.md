`1403723142829428/posts
?fields=admin_creator,
created_time,
full_picture,
message,
message_tags,
shares,
is_hidden,
attachments{url,media,media_type},
comments.limit(0).summary(true),
reactions.type(LIKE).limit(0).summary(true).as(like),
reactions.type(LOVE).limit(0).summary(true).as(love),
reactions.type(CARE).limit(0).summary(true).as(care),
reactions.type(HAHA).limit(0).summary(true).as(haha),
reactions.type(WOW).limit(0).summary(true).as(wow),
reactions.type(SAD).limit(0).summary(true).as(sad),
reactions.type(ANGRY).limit(0).summary(true).as(angry)
&limit=5`



1403723142829428/posts?fields=admin_creator,created_time,full_picture,message,message_tags,shares,is_hidden,attachments{url,media,media_type},comments.limit(0).summary(true),reactions.type(LIKE).limit(0).summary(true).as(like),reactions.type(LOVE).limit(0).summary(true).as(love),reactions.type(CARE).limit(0).summary(true).as(care),reactions.type(HAHA).limit(0).summary(true).as(haha),reactions.type(WOW).limit(0).summary(true).as(wow),reactions.type(SAD).limit(0).summary(true).as(sad),reactions.type(ANGRY).limit(0).summary(true).as(angry)&limit=5


attachments{url} -- give actual link for the original post on facebook
