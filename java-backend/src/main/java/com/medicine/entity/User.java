package com.medicine.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@TableName("user")
public class User {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String nickname;
    private String avatar;
    private String phoneNumber;
    private Integer gender;
    private LocalDate birthday;
    private String username;
    private String realName;
    private String status;
    private LocalDateTime lastLoginTime;
    private LocalDateTime createTime;
    private Integer isDelete;
}