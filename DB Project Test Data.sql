INSERT INTO `Person`(`username`, `password`, `firstName`, `lastName`, `bio`) VALUES ('abby','pass1','Abby','Lee','Dance Moms Leader');
INSERT INTO `Person`(`username`, `password`, `firstName`, `lastName`, `bio`) VALUES ('bobby','pass2','Bobby','Brown','Abbys Partner');
INSERT INTO `Person`(`username`, `password`, `firstName`, `lastName`, `bio`) VALUES ('colieen','pass3','Colieen','Douglas','Dance Mom');
INSERT INTO `Person`(`username`, `password`, `firstName`, `lastName`, `bio`) VALUES ('dan','pass2','Dan','Sucio','dirty dan');

INSERT INTO `Friendgroup`(`groupOwner`, `groupName`, `description`) VALUES ('abby','family','Lee Family');
INSERT INTO `Friendgroup`(`groupOwner`, `groupName`, `description`) VALUES ('abby','roommates','roommates of 221B');

INSERT INTO `Friendgroup`(`groupOwner`, `groupName`, `description`) VALUES ('bobby','roommates','42 Wallaby Way');
INSERT INTO `Friendgroup`(`groupOwner`, `groupName`, `description`) VALUES ('bobby','bowlingTeam','The Pinhead Larrys');

INSERT INTO `Photo`(`postingdate`, `filepath`, `allFollowers`, `caption`, `photoPoster`) VALUES (CURDATE(),'./roommates_b.jpg',True,'roommates','bobby');
INSERT INTO `Photo`(`postingdate`, `filepath`, `allFollowers`, `caption`, `photoPoster`) VALUES (CURDATE(),'./roommates_a.jpg',True,'roommates','abby');
INSERT INTO `Photo`(`postingdate`, `filepath`, `allFollowers`, `caption`, `photoPoster`) VALUES (CURDATE(),'./bowling_team.jpg',False,'bowlingTeam','bobby');
INSERT INTO `Photo`(`postingdate`, `filepath`, `allFollowers`, `caption`, `photoPoster`) VALUES (CURDATE(),'./family_bora_bora.jpg',False,'family vaca','abby');


INSERT INTO `BelongTo`(`member_username`, `owner_username`, `groupName`) VALUES ('colieen','abby','roommates');
INSERT INTO `BelongTo`(`member_username`, `owner_username`, `groupName`) VALUES ('abby','abby','roommates');
INSERT INTO `BelongTo`(`member_username`, `owner_username`, `groupName`) VALUES ('dan','abby','family');
INSERT INTO `BelongTo`(`member_username`, `owner_username`, `groupName`) VALUES ('abby','abby','family');
INSERT INTO `BelongTo`(`member_username`, `owner_username`, `groupName`) VALUES ('dan','bobby','roommates');
INSERT INTO `BelongTo`(`member_username`, `owner_username`, `groupName`) VALUES ('bobby','bobby','roommates');


INSERT INTO `Follow`(`username_followed`, `username_follower`, `followstatus`) VALUES ('bobby','abby',True);
INSERT INTO `Follow`(`username_followed`, `username_follower`, `followstatus`) VALUES ('bobby','colieen',False);