CREATE DEFINER=`root`@`%` PROCEDURE `sp_login`(in p_emailAddress varchar(25))
BEGIN
select Password from Staff where EmailAddress = p_emailAddress;
END

CREATE DEFINER=`root`@`%` PROCEDURE `sp_getPhotoByUserid`(in p_userId int(11))
BEGIN
select link from photos where userID = p_userId;
END

CREATE DEFINER=`root`@`%` PROCEDURE `sp_delete`(in p_photoLink varchar(100))
BEGIN
delete from photos where p_photoLink = link;
END