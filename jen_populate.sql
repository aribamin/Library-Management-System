
INSERT INTO members (email, passwd, name, byear, faculty)
VALUES 
  ('naruto@example.com', 'rasengan', 'Naruto Uzumaki', 1990, 'Ninja Arts'),
  ('sasuke@example.com', 'sharingan', 'Sasuke Uchiha', 1995, 'Strategic Studies'),
  ('sakura@example.com', 'cherryblossom', 'Sakura Haruno', 1988, 'Medical Ninjutsu');


INSERT INTO books (book_id, title, author, pyear)
VALUES 
  (1, 'The Tale of Hokage', 'hokage again', 1999),
  (2, 'Sharingan Secrets', 'Itachi Uchiha', 2005),
  (3, 'Medical Ninjutsu Handbook', 'Tsunade Senju', 2002),
  (4, 'The Tale of Hokage1', 'Masashi Kishimoto', 1999),
  (5, 'The tale of Hokage2', 'Masashi Kishimoto2', 1999),
  (6, 'The tale of Hokage3', 'Masashi Kishimoto3', 1999),
  (7, 'The tale of Hokage4', 'Masashi Kishimoto4', 1999),
  (8, 'the bale of Hokage5', 'Masashi Kishimoto5', 1999),
  (9, 'The Tale of Hokage5', 'Masashi Kishimoto8', 1999),
  (10, 'The Tale of Hokage7', 'Masashi Kishimoto7', 1999),
  (11, 'The Tale of Hokage8', 'Masashi Kishimoto0', 1999),
  (12, 'The Tale of Hokage88', 'Masashi Kishimoto', 1999),
  (13, 'The Tale of nopeage1', 'hokage Kishimoto', 1999),
  (14, 'The Tale of nopeage2', 'Masashi hokage', 1999),
  (15, 'The Tale of nopeage3', 'Masashokageshimoto', 1999),
  (16, 'The Tale of nopeage3', 'Masashi hokage1', 1999),
  (17, 'The Tale of nopeage3', 'Masashi hokage5', 1999),
  (18, 'The Tale of nopeage3', 'Masashi Kishimoto', 1999);



INSERT INTO borrowings (bid, member, book_id, start_date, end_date) VALUES
  (1, 'naruto@example.com', 1, '2024-02-01', '2024-02-15'),
  (2, 'naruto@example.com', 2, '2024-02-01', '2024-02-15'),
  (3, 'sasuke@example.com', 2, '2024-02-05', '2024-02-20'),
  (4, 'sakura@example.com', 3, '2024-02-10', '2024-02-25'),
  (5, 'naruto@example.com', 1, '2024-02-17', '2024-03-01'),
  (6, 'naruto@example.com', 1, '2024-03-05', NULL),
  (7, 'kakashi@example.com', 4, '2024-03-01', NULL),
  (8, 'hinata@example.com', 5, '2024-03-02', NULL),
  (9, 'kakashi@example.com', 2, '2024-02-25', '2024-03-07'),
  (10, 'naruto@example.com', 3, '2024-02-28', NULL),
  (11, 'naruto@example.com', 4, '2024-03-03', NULL),
  (12, 'naruto@example.com', 5, '2024-03-04', NULL),
  (13, 'naruto@example.com', 6, '2024-03-10', NULL),
  (14, 'sasuke@example.com', 7, '2024-03-15', NULL),
  (15, 'sakura@example.com', 8, '2024-03-20', NULL),
  (16, 'kakashi@example.com', 9, '2024-03-25', NULL),
  (17, 'hinata@example.com', 10, '2024-03-30', NULL),
  (18, 'naruto@example.com', 2, '2024-03-05', '2024-03-25'),
  (19, 'sasuke@example.com', 3, '2024-02-01', '2024-02-21'),
  (20, 'sakura@example.com', 4, '2024-03-15', NULL);



INSERT INTO penalties (pid, bid, amount, paid_amount)
VALUES 
  (1, 1, 10, 5),
  (2, 2, 15, 0),
  (3, 3, 8, 8);


INSERT INTO reviews (rid, book_id, member, rating, rtext, rdate)
VALUES 
  (1, 1, 'naruto@example.com', 5, 'Believe it!', '2024-02-12'),
  (2, 1, 'naruto@example.com', 3.5, 'Believe it!', '2024-04-16'),
  (3, 2, 'sasuke@example.com', 4, 'Intriguing insights into the Uchiha clan.', '2024-02-18'),
  (4, 3, 'sakura@example.com', 3, 'Useful medical techniques.', '2024-02-22');
