
INSERT INTO members (email, passwd, name, byear, faculty)
VALUES 
  ('naruto@example.com', 'rasengan', 'Naruto Uzumaki', 1990, 'Ninja Arts'),
  ('sasuke@example.com', 'sharingan', 'Sasuke Uchiha', 1995, 'Strategic Studies'),
  ('sakura@example.com', 'cherryblossom', 'Sakura Haruno', 1988, 'Medical Ninjutsu');


INSERT INTO books (book_id, title, author, pyear)
VALUES 
  (1, 'The Tale of Hokage', 'Masashi Kishimoto', 1999),
  (2, 'Sharingan Secrets', 'Itachi Uchiha', 2005),
  (3, 'Medical Ninjutsu Handbook', 'Tsunade Senju', 2002);


INSERT INTO borrowings (bid, member, book_id, start_date, end_date)
VALUES 
  (1, 'naruto@example.com', 1, '2024-02-01', '2024-02-15'),
  (2, 'sasuke@example.com', 2, '2024-02-05', '2024-02-20'),
  (3, 'sakura@example.com', 3, '2024-02-10', '2024-02-25');


INSERT INTO penalties (pid, bid, amount, paid_amount)
VALUES 
  (1, 1, 10, 5),
  (2, 2, 15, 0),
  (3, 3, 8, 8);


INSERT INTO reviews (rid, book_id, member, rating, rtext, rdate)
VALUES 
  (1, 1, 'naruto@example.com', 5, 'Believe it!', '2024-02-12'),
  (2, 2, 'sasuke@example.com', 4, 'Intriguing insights into the Uchiha clan.', '2024-02-18'),
  (3, 3, 'sakura@example.com', 3, 'Useful medical techniques.', '2024-02-22');
